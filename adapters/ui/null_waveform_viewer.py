"""Null implementation of waveform viewer port.

This adapter provides a placeholder implementation that displays an informational
message when waveform viewing is requested. It serves as the default implementation
until a full waveform viewer is integrated.
"""

import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox, QWidget

from core.ports import WaveformViewerPort


class NullWaveformViewer(WaveformViewerPort):
    """Null adapter for waveform viewing that displays an informational message.

    This implementation satisfies the WaveformViewerPort protocol but does not
    provide actual waveform visualization. Instead, it shows a user-friendly
    message indicating that the feature is temporarily unavailable.

    This adapter allows the application to function without waveform viewing
    capabilities while maintaining the port-based architecture for future
    implementations.
    """

    def show(self, zip_path: Path, wav_filename: str, parent: QWidget | None = None) -> None:
        """Display an informational message about waveform viewer unavailability.

        Args:
            zip_path: Path to ZIP archive (unused in null implementation)
            wav_filename: Name of WAV file (unused in null implementation)
            parent: Parent widget for message box positioning
        """
        platform = os.getenv("QT_QPA_PLATFORM", "")
        if platform.lower() in ("offscreen", "minimal"):
            logging.info("Waveform viewer unavailable: %s in %s (headless).", wav_filename, zip_path)
            return

        QMessageBox.information(
            parent,
            "Feature Unavailable",
            "The waveform viewer is currently unavailable.\n\n"
            "This feature has been temporarily disabled during refactoring.",
        )
