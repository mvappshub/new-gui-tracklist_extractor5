"""Port interfaces for hexagonal architecture - domain depends on these abstractions, adapters implement them."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget

from core.models.analysis import WavInfo


class AudioModeDetector(Protocol):
    """Protocol for detecting audio side/position from WAV filenames.

    This protocol defines the contract for audio mode detection strategies.
    Implementations can use various approaches (AI-backed, deterministic parsing, etc.)
    while maintaining the same interface.

    Purpose:
        Detect side (e.g., "A", "B") and position (1, 2, 3...) from WAV filenames.
        This abstraction allows the domain layer to remain independent of detection
        strategy, enabling easy swapping between AI-backed and test implementations.

    Input:
        list[WavInfo]: List of WavInfo objects with filename and duration_sec populated.
        The side and position fields may be None initially.

    Output:
        dict[str, list[WavInfo]]: Dictionary mapping side (e.g., "A", "B") to list of
        WavInfo objects with side and position fields populated and normalized.

    Normalization:
        Positions must be sequential (1, 2, 3...) with no gaps or duplicates.
        For each side, positions are renumbered to start at 1 and increment by 1.
    """

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Detect audio side and position from WAV filenames.

        Args:
            wavs: List of WavInfo objects with filename and duration_sec populated.

        Returns:
            Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
            with side and position fields populated and normalized.
        """
        ...


class WaveformViewerPort(Protocol):
    """Protocol for waveform viewer implementations.

    This protocol defines the contract for waveform visualization components.
    Implementations can provide different viewing/editing capabilities while
    maintaining the same interface.

    Purpose:
        Display and optionally edit audio waveforms from WAV files in ZIP archives.
        This abstraction allows the UI layer to remain independent of specific
        waveform viewer implementations, enabling easy swapping between different
        viewers or a null implementation.

    Input:
        zip_path: Path to ZIP archive containing WAV files
        wav_filename: Name of the WAV file within the ZIP to display
        parent: Optional parent widget for dialog positioning

    Output:
        None - implementations typically show a modal or non-modal dialog
    """

    def show(self, zip_path: Path, wav_filename: str, parent: QWidget | None = None) -> None:
        """Open and display the waveform viewer for the specified audio file.

        Args:
            zip_path: Path to ZIP archive containing the WAV file
            wav_filename: Name of the WAV file to display (may include subdirectory path)
            parent: Optional parent widget for proper dialog positioning and modality
        """
        ...
