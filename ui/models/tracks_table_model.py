from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult
from core.models.settings import ToleranceSettings
from ui.config_models import ThemeSettings
from ui.constants import (
    LABEL_TOTAL_TRACKS,
    PLACEHOLDER_DASH,
    TABLE_HEADERS_BOTTOM,
)
from ui.theme import get_custom_icon


class TracksTableModel(QAbstractTableModel):
    """Model for the bottom table showing track details."""

    def __init__(self, tolerance_settings: ToleranceSettings, theme_settings: ThemeSettings):
        """Initialize TracksTableModel with dependency injection.

        Args:
            tolerance_settings: Tolerance settings for match calculations.
            theme_settings: Theme settings for styling.
        """
        super().__init__()
        self.tolerance_settings = tolerance_settings
        self.theme_settings = theme_settings

        self._headers = TABLE_HEADERS_BOTTOM
        self._data: Optional[SideResult] = None

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if not index.isValid():
            return base
        if index.row() == self.rowCount() - 1:
            return base & ~Qt.ItemFlag.ItemIsSelectable
        return base

    def rowCount(self, parent: QModelIndex = QModelIndex()):  # type: ignore[override]
        if not self._data or not self._data.pdf_tracks:
            return 0
        return len(self._data.pdf_tracks) + 1

    def columnCount(self, parent: QModelIndex = QModelIndex()):  # type: ignore[override]
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not self._data:
            return None

        row = index.row()
        column = index.column()
        is_total_row = row == self.rowCount() - 1

        # Column 6 (Match) - Icon rendering
        if role == Qt.ItemDataRole.DecorationRole and column == 6 and not is_total_row:
            if self._data.mode == "tracks":
                pdf_track = self._data.pdf_tracks[row] if row < len(self._data.pdf_tracks) else None
                wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None

                if pdf_track and wav_track:
                    difference = wav_track.duration_sec - pdf_track.duration_sec
                    try:
                        track_tolerance = float(self.tolerance_settings.warn_tolerance)
                    except (TypeError, ValueError):
                        track_tolerance = 2.0

                    # Return check or cross icon based on tolerance
                    if abs(difference) <= track_tolerance:
                        return get_custom_icon("check")
                    else:
                        return get_custom_icon("cross")
                else:
                    return get_custom_icon("cross")
            return None

        # Column 6 (Match) - Total row icon
        if role == Qt.ItemDataRole.DecorationRole and column == 6 and is_total_row:
            if self._data.status == AnalysisStatus.OK:
                return get_custom_icon("check")
            else:
                return get_custom_icon("cross")

        if role in (Qt.ItemDataRole.AccessibleTextRole, Qt.ItemDataRole.ToolTipRole) and column == 6:
            if is_total_row:
                return "Match OK" if self._data.status == AnalysisStatus.OK else "No match"
            else:
                if self._data.mode == "tracks":
                    pdf_track = self._data.pdf_tracks[row] if row < len(self._data.pdf_tracks) else None
                    wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None

                    if pdf_track and wav_track:
                        difference = wav_track.duration_sec - pdf_track.duration_sec
                        try:
                            track_tolerance = float(self.tolerance_settings.warn_tolerance)
                        except (TypeError, ValueError):
                            track_tolerance = 2.0

                        if abs(difference) <= track_tolerance:
                            return "Match OK"
                    return "No match"
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if is_total_row:
                return self.get_total_row_data(column)
            return self.get_track_row_data(row, column)

        if role == Qt.ItemDataRole.BackgroundRole and is_total_row:
            return QColor(self.theme_settings.total_row_bg_color)

        if role == Qt.ItemDataRole.FontRole and is_total_row:
            font = QFont()
            font.setBold(True)
            return font

        if role == Qt.ItemDataRole.TextAlignmentRole and column == 6:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def get_track_row_data(self, row: int, column: int):
        if not self._data or row >= len(self._data.pdf_tracks):
            return ""

        pdf_track = self._data.pdf_tracks[row]

        if self._data.mode == "tracks":
            wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None
            difference = (wav_track.duration_sec - pdf_track.duration_sec) if wav_track else None

            try:
                track_tolerance = float(self.tolerance_settings.warn_tolerance)
            except (TypeError, ValueError):
                track_tolerance = 2.0

            if column == 0:
                return pdf_track.position
            if column == 1:
                return wav_track.filename if wav_track else PLACEHOLDER_DASH
            if column == 2:
                return pdf_track.title
            if column == 3:
                return f"{pdf_track.duration_sec // 60:02d}:{pdf_track.duration_sec % 60:02d}"
            if column == 4:
                if wav_track:
                    return f"{int(wav_track.duration_sec) // 60:02d}:{int(wav_track.duration_sec) % 60:02d}"
                return PLACEHOLDER_DASH
            if column == 5:
                return f"{difference:+.0f}" if difference is not None else PLACEHOLDER_DASH
            if column == 6:
                return ""  # Icon is shown via DecorationRole
        else:
            if column == 0:
                return pdf_track.position
            if column == 1:
                return PLACEHOLDER_DASH
            if column == 2:
                return pdf_track.title
            if column == 3:
                return f"{pdf_track.duration_sec // 60:02d}:{pdf_track.duration_sec % 60:02d}"
            if column == 4:
                return PLACEHOLDER_DASH
            if column == 5:
                return PLACEHOLDER_DASH
            if column == 6:
                return PLACEHOLDER_DASH
            return PLACEHOLDER_DASH
        return ""

    def get_total_row_data(self, column: int):
        if not self._data:
            return ""

        if column == 1:
            if self._data.mode == "side" and self._data.wav_tracks:
                return self._data.wav_tracks[0].filename
            return LABEL_TOTAL_TRACKS
        if column == 2:
            return f"{len(self._data.pdf_tracks)} tracks"
        if column == 3:
            return f"{self._data.total_pdf_sec // 60:02d}:{self._data.total_pdf_sec % 60:02d}"
        if column == 4:
            return f"{int(self._data.total_wav_sec) // 60:02d}:{int(self._data.total_wav_sec) % 60:02d}"
        if column == 5:
            return f"{self._data.total_difference:+.0f}"
        if column == 6:
            return ""  # Icon is shown via DecorationRole
        return ""

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def update_data(self, result: Optional[SideResult]) -> None:
        self.beginResetModel()
        self._data = result
        self.endResetModel()
