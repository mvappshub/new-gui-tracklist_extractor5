from __future__ import annotations
from typing import List

from core.domain.parsing import UNKNOWN_POSITION
from core.domain.steps import DetectionStep
from core.models.analysis import WavInfo
from core.ports import AudioModeDetector
from adapters.audio.steps import StrictParserStep, AiParserStep, DeterministicFallbackStep

class ChainedAudioModeDetector(AudioModeDetector):
    """
    Orchestrates audio mode detection using a Chain of Responsibility pattern.
    """
    def __init__(self, steps: List[DetectionStep] | None = None):
        if steps is None:
            self._steps: List[DetectionStep] = [
                StrictParserStep(),
                AiParserStep(),
                DeterministicFallbackStep(),
            ]
        else:
            self._steps = steps

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        if not wavs:
            return {}
        
        # Create a mutable copy for processing
        processing_wavs = [w.model_copy() for w in wavs]

        for step in self._steps:
            stop_chain = step.process(processing_wavs)
            if stop_chain:
                break
        
        return self._normalize_and_group(processing_wavs)

    def _normalize_and_group(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Groups WAVs by side and normalizes their positions."""
        side_map: dict[str, list[WavInfo]] = {}
        for wav in wavs:
            side = wav.side or "A"  # Default to "A" if side is still None
            side_map.setdefault(side, []).append(wav)

        for wav_list in side_map.values():
            if not wav_list:
                continue
            
            wav_list.sort(key=lambda x: (x.position if x.position is not None else UNKNOWN_POSITION, x.filename.lower()))
            
            for i, wav in enumerate(wav_list, start=1):
                wav.apply_parsed_info({"position": i})
        
        return side_map
