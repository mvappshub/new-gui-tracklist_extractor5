from __future__ import annotations
import logging
from typing import List

from core.domain.parsing import StrictFilenameParser
from core.models.analysis import WavInfo
from adapters.audio.ai_helpers import ai_parse_batch, merge_ai_results

class StrictParserStep:
    """First step: attempts to parse side/position using strict regex rules."""
    def __init__(self) -> None:
        self._parser = StrictFilenameParser()

    def process(self, wavs: List[WavInfo]) -> bool:
        all_parsed = True
        for wav in wavs:
            if wav.side is None or wav.position is None:
                parsed = self._parser.parse(wav.filename)
                updates: dict[str, object] = {}
                if wav.side is None and parsed.side:
                    updates["side"] = parsed.side
                if wav.position is None and parsed.position is not None:
                    updates["position"] = parsed.position
                if updates:
                    wav.apply_parsed_info(updates)
            if wav.side is None or wav.position is None:
                all_parsed = False
        return all_parsed

class AiParserStep:
    """Second step: uses an AI model as a fallback for unparsed files."""
    def process(self, wavs: List[WavInfo]) -> bool:
        unparsed_wavs = [w for w in wavs if w.side is None or w.position is None]
        if not unparsed_wavs:
            return True  # Chain can stop, everything is parsed

        try:
            filenames = [w.filename for w in unparsed_wavs]
            ai_map = ai_parse_batch(filenames)
            if ai_map:
                merge_ai_results(unparsed_wavs, ai_map)
        except Exception as e:
            logging.warning(f"AI parser step failed: {e}", exc_info=True)

        # Never stop the chain here; always allow fallback
        return False

class DeterministicFallbackStep:
    """Final step: assigns default side/position if all else fails."""
    def process(self, wavs: List[WavInfo]) -> bool:
        if not wavs:
            return True

        # Only run if NO files have a side assigned
        if any(w.side for w in wavs):
            return True

        wavs.sort(key=lambda x: x.filename.lower())
        for i, wav in enumerate(wavs, start=1):
            updates: dict[str, object] = {}
            if not wav.side:
                updates["side"] = "A"
            if wav.position is None:
                updates["position"] = i
            if updates:
                wav.apply_parsed_info(updates)
        return True # This is the last step, always stop
