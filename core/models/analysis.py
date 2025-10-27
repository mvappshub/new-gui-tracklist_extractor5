from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from core.domain.analysis_status import AnalysisStatus


class TrackInfo(BaseModel):
    title: str
    side: str
    position: int
    duration_sec: int


class WavInfo(BaseModel):
    filename: str
    duration_sec: float
    side: str | None = None
    position: int | None = None

    def apply_parsed_info(self, parsed_data: dict[str, Any]) -> None:
        """Update side and position fields using metadata from parsing helpers."""

        if not isinstance(parsed_data, dict):
            return

        side_value = parsed_data.get("side")
        if isinstance(side_value, str):
            normalized_side = side_value.strip().upper()
            if normalized_side and normalized_side != "UNKNOWN":
                self.side = normalized_side

        position_value = parsed_data.get("position")
        if position_value is None:
            return

        try:
            position_int = int(position_value)
        except (TypeError, ValueError):
            return

        if position_int > 0:
            self.position = position_int


class SideResult(BaseModel):
    seq: int
    pdf_path: Path
    zip_path: Path
    side: str
    mode: str
    status: AnalysisStatus
    pdf_tracks: list[TrackInfo]
    wav_tracks: list[WavInfo]
    total_pdf_sec: int
    total_wav_sec: float
    total_difference: int


@dataclass
class FilePair:
    """Represents a paired PDF and ZIP file based on a shared numeric ID."""

    pdf: Path
    zip: Path
