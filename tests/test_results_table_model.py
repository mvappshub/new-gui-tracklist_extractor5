from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from ui.config_models import ThemeSettings
from core.models.analysis import SideResult
from core.domain.analysis_status import AnalysisStatus
from ui.models.results_table_model import ResultsTableModel

pytestmark = pytest.mark.usefixtures("qtbot")


@pytest.fixture
def theme_settings():
    return ThemeSettings(
        font_family="",
        font_size=10,
        stylesheet_path=Path(),
        status_colors={"ok": "#10B981", "warn": "#F59E0B", "fail": "#EF4444"},
        logo_path=Path(),
        claim_visible=True,
        claim_text="Emotions. Materialized.",
        action_bg_color="#E0E7FF",
        total_row_bg_color="#F3F4F6",
    )


@pytest.fixture
def mock_side_result():
    return SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[],
        wav_tracks=[],
        total_pdf_sec=100,
        total_wav_sec=100.0,
        total_difference=0,
    )


def test_results_table_model_creation(theme_settings):
    model = ResultsTableModel(theme_settings=theme_settings)
    assert model.rowCount() == 0
    assert model.columnCount() == len(model._headers)


def test_add_result_increases_row_count(theme_settings, mock_side_result):
    model = ResultsTableModel(theme_settings=theme_settings)
    model.add_result(mock_side_result)
    assert model.rowCount() == 1
    assert model.all_results()[0].pdf_path.name == "test.pdf"


def test_data_retrieval(theme_settings, mock_side_result):
    model = ResultsTableModel(theme_settings=theme_settings)
    model.add_result(mock_side_result)

    index_file = model.index(0, 1)
    assert model.data(index_file, Qt.ItemDataRole.DisplayRole) == "test.pdf"

    index_status = model.index(0, 5)
    assert model.data(index_status, Qt.ItemDataRole.DisplayRole) == "OK"


def test_status_color(theme_settings, mock_side_result):
    mock_side_result.status = AnalysisStatus.WARN

    model = ResultsTableModel(theme_settings=theme_settings)
    model.add_result(mock_side_result)

    index_status = model.index(0, 5)
    color = model.data(index_status, Qt.ItemDataRole.BackgroundRole)

    assert color is not None
    assert color.name().lower() == theme_settings.status_colors["warn"].lower()
