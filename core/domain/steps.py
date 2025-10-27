from __future__ import annotations

from typing import Protocol, List
from core.models.analysis import WavInfo

class DetectionStep(Protocol):
    """Protocol for a single step in the audio mode detection chain."""

    def process(self, wavs: List[WavInfo]) -> bool:
        """
        Processes a list of WavInfo objects to detect side and position.

        Args:
            wavs: The list of WavInfo objects to process.

        Returns:
            True if the chain should stop processing (definitive result found),
            False to continue to the next step.
        """
        ...
