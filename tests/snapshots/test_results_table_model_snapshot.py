from __future__ import annotations

import json
from pathlib import Path

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult
from core.models.settings import ThemeSettings
from ui.models.results_table_model import ResultsTableModel

pytestmark = pytest.mark.gui

SNAPSHOT_FILE = Path(__file__).with_name("results_table_model.json")


def _create_theme() -> ThemeSettings:
    return ThemeSettings(
        font_family="Poppins",
        font_size=13,
        stylesheet_path=Path("gz_media.qss"),
        status_colors={"ok": "#10B981", "warn": "#F59E0B", "fail": "#EF4444"},
        logo_path=Path("assets/gz_logo_white.png"),
        claim_visible=True,
        claim_text="Emotions. Materialized.",
        action_bg_color="#E0E7FF",
        total_row_bg_color="#F3F4F6",
    )


def _serialize_columns(model: ResultsTableModel) -> list[dict[str, object]]:
    columns = []
    for column in range(model.columnCount()):
        header = model.headerData(column, orientation=Qt.Orientation.Horizontal)
        index = model.index(0, column)
        decoration = model.data(index, role=Qt.ItemDataRole.DecorationRole)
        renderer = None
        if decoration is not None:
            renderer = type(decoration).__name__
        columns.append({"header": header, "renderer": renderer})
    return columns


def test_results_table_model_snapshot(qapp: QApplication):
    expected = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    theme = _create_theme()
    model = ResultsTableModel(theme)

    side_result = SideResult(
        seq=1,
        pdf_path=Path("sample.pdf"),
        zip_path=Path("sample.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[],
        wav_tracks=[],
        total_pdf_sec=200,
        total_wav_sec=200,
        total_difference=0,
    )
    model.add_result(side_result)

    actual = {"columns": _serialize_columns(model)}
    assert actual == expected, "ResultsTableModel snapshot mismatch."
