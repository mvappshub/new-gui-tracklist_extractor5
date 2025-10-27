"""Fake audio mode detector adapter for tests.

Implements the AudioModeDetector protocol with deterministic filename parsing.
No external API calls - guarantees consistent results for same inputs.
"""

from __future__ import annotations

from core.domain.parsing import UNKNOWN_POSITION, StrictFilenameParser
from core.models.analysis import WavInfo
from core.ports import AudioModeDetector


class FakeAudioModeDetector(AudioModeDetector):
    """Fake audio mode detector for tests.

    Uses deterministic filename parsing with no external API calls.
    Guarantees consistent results for same inputs.
    """

    def __init__(self) -> None:
        self._parser = StrictFilenameParser()

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Detect audio side and position from WAV filenames using deterministic parsing.

        Args:
            wavs: List of WavInfo objects with filename and duration_sec populated.

        Returns:
            Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
            with side and position populated and normalized (sequential 1, 2, 3...).

        Raises:
            No exceptions raised - handles edge cases gracefully.
        """
        if not wavs:
            return {}

        parsed_wavs = []
        for wav in wavs:
            parsed_info = self._parser.parse(wav.filename)
            parsed_wavs.append(
                WavInfo(
                    filename=wav.filename,
                    duration_sec=wav.duration_sec,
                    side=parsed_info.side,
                    position=parsed_info.position,
                )
            )

        side_map: dict[str, list[WavInfo]] = {}
        for wav in parsed_wavs:
            side = wav.side or "A"  # Default to "A" if side is None
            side_map.setdefault(side, []).append(wav)

        for wav_list in side_map.values():
            wav_list.sort(
                key=lambda x: (x.position if x.position is not None else UNKNOWN_POSITION, x.filename.lower())
            )

        self._normalize_positions(side_map)

        return side_map

    def _normalize_positions(self, side_map: dict[str, list[WavInfo]]) -> None:
        """Normalize positions to be sequential (1, 2, 3...) with no gaps or duplicates."""
        for wav_list in side_map.values():
            if not wav_list:
                continue

            wav_list.sort(
                key=lambda x: (x.position if x.position is not None else UNKNOWN_POSITION, x.filename.lower())
            )

            actual = [w.position for w in wav_list]
            expected = list(range(1, len(wav_list) + 1))

            has_missing = any(pos is None for pos in actual)
            non_none_positions = {p for p in actual if p is not None}
            has_duplicates = len([p for p in actual if p is not None]) != len(non_none_positions)

            if has_missing or has_duplicates or actual != expected:
                for i, wav in enumerate(wav_list, start=1):
                    wav.apply_parsed_info({"position": i})
