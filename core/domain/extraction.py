"""Domain-level abstractions for audio extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from core.models.analysis import WavInfo


class WavReader(Protocol):
    """Abstraction used by domain services to retrieve WAV metadata without performing I/O."""

    def read_wav_files(self, zip_path: Path) -> list[WavInfo]:
        """Return WAV metadata derived from the provided ZIP archive."""
