"""Real AI-backed audio mode detector adapter.

Implements the AudioModeDetector protocol using OpenAI/OpenRouter APIs.
Wraps existing wav_extractor_wave functions for strict parsing → AI fallback →
deterministic fallback → normalization.
"""

from __future__ import annotations

from core.models.analysis import WavInfo
from core.ports import AudioModeDetector
from adapters.audio.ai_helpers import detect_audio_mode_with_ai, normalize_positions


class AiAudioModeDetector(AudioModeDetector):
    """Real AI-backed audio mode detector using OpenAI/OpenRouter APIs.

    Wraps existing wav_extractor_wave functions for strict parsing → AI fallback →
    deterministic fallback → normalization.
    """

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Detect audio side and position from WAV filenames using AI.

        Args:
            wavs: List of WavInfo objects with filename and duration_sec populated.

        Returns:
            Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
            with side and position populated and normalized (sequential 1, 2, 3...).

        Raises:
            No exceptions raised - handles edge cases gracefully.
        """
        # Handle empty input
        if not wavs:
            return {}

        # Call AI detection function directly with unified WavInfo type
        side_map = detect_audio_mode_with_ai(wavs)

        # Normalize positions to be sequential (1, 2, 3...) with no gaps
        normalize_positions(side_map)

        # side_map is already in unified WavInfo type
        return side_map
