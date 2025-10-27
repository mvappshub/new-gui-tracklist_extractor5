from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult
from ui.config_models import ThemeSettings
from ui.constants import (
    COLOR_WHITE,
    FILTER_ALL,
    FILTER_FAIL,
    FILTER_OK,
    FILTER_WARN,
    TABLE_HEADERS_TOP,
)
from ui.theme import get_system_file_icon
from ui.theme import get_system_file_icon


class ResultsTableModel(QAbstractTableModel):
    """Model for the top table showing matched PDF/ZIP pairs."""

    def __init__(self, theme_settings: ThemeSettings):
        super().__init__()
        self.theme_settings = theme_settings
        self._headers = TABLE_HEADERS_TOP
        self._data: List[SideResult] = []
        self._filtered_data: List[SideResult] = []
        self._active_filter: str = FILTER_ALL
        self._seq_counter = 1

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._filtered_data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None
        row = index.row()
        if row < 0 or row >= len(self._filtered_data):
            return None
        result = self._filtered_data[row]
        column = index.column()

        if role == Qt.ItemDataRole.DecorationRole:
            if column == 6 and result.pdf_path:
                return get_system_file_icon("file")
            if column == 7 and result.zip_path:
                return get_system_file_icon("dir")

        if role == Qt.ItemDataRole.BackgroundRole:
            if column == 6 and result.pdf_path:
                return QColor(self.theme_settings.action_bg_color)
            if column == 7 and result.zip_path:
                return QColor(self.theme_settings.action_bg_color)

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return index.row() + 1
            if column == 1:
                return result.pdf_path.name
            if column == 2:
                return result.side
            if column == 3:
                return result.mode
            if column == 4:
                return f"{result.total_pdf_sec // 60:02d}:{result.total_pdf_sec % 60:02d}"
            if column == 5:
                return result.status.value

        if role == Qt.ItemDataRole.ForegroundRole and column == 5:
            return QColor(COLOR_WHITE)

        if role == Qt.ItemDataRole.BackgroundRole and column == 5:
            status_colors = self.theme_settings.status_colors
            color_value = status_colors.get(result.status.color_key())
            if color_value:
                return QColor(color_value)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column in (6, 7):
                return Qt.AlignmentFlag.AlignCenter
            if column in (3, 4, 5):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column in (0, 2):
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft

        if role == Qt.ItemDataRole.ToolTipRole and column == 1:
            return f"PDF: {result.pdf_path}\nZIP: {result.zip_path if result.zip_path else '-'}"
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 6 and result.pdf_path:
                return "Open PDF file"
            if column == 7 and result.zip_path:
                return "Open ZIP archive"

        return None

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]
            if role == Qt.ItemDataRole.FontRole:
                header_font = QFont()
                header_font.setBold(True)
                return header_font
        return None

    def add_result(self, result: SideResult) -> None:
        """Add a result to the model, maintaining filter state."""
        result_with_seq = result.model_copy()
        result_with_seq.seq = self._seq_counter
        self._seq_counter += 1

        self._data.append(result_with_seq)
        if self._passes_filter(result_with_seq):
            insert_row = len(self._filtered_data)
            self.beginInsertRows(QModelIndex(), insert_row, insert_row)
            self._filtered_data.append(result_with_seq)
            self.endInsertRows()
            if hasattr(self, "_schedule_header_resizes"):
                QTimer.singleShot(0, self._schedule_header_resizes)

    def get_result(self, row: int) -> Optional[SideResult]:
        if 0 <= row < len(self._filtered_data):
            return self._filtered_data[row]
        return None

    def clear(self) -> None:
        self.beginResetModel()
        self._data.clear()
        self._filtered_data.clear()
        self._active_filter = FILTER_ALL
        self._seq_counter = 1
        self.endResetModel()

    def all_results(self) -> List[SideResult]:
        return list(self._data)

    def set_filter(self, filter_text: str) -> None:
        valid_filters = {FILTER_ALL, FILTER_OK, FILTER_FAIL, FILTER_WARN}
        self._active_filter = filter_text if filter_text in valid_filters else FILTER_ALL
        self._rebuild_filtered_data()

    def _passes_filter(self, result: SideResult) -> bool:
        if self._active_filter == FILTER_ALL:
            return True
        status_by_filter = {
            FILTER_OK: AnalysisStatus.OK,
            FILTER_FAIL: AnalysisStatus.FAIL,
            FILTER_WARN: AnalysisStatus.WARN,
        }
        expected_status = status_by_filter.get(self._active_filter)
        if expected_status is None:
            return True
        return result.status == expected_status

    def _rebuild_filtered_data(self) -> None:
        self.beginResetModel()
        self._filtered_data = [res for res in self._data if self._passes_filter(res)]
        self.endResetModel()
