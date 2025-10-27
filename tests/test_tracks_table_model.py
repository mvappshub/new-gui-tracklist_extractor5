from __future__ import annotations
from core.domain.analysis_status import AnalysisStatus

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ToleranceSettings
from ui.config_models import ThemeSettings
from ui.models.tracks_table_model import TracksTableModel

pytestmark = pytest.mark.usefixtures("qtbot")


@pytest.fixture
def tolerance_settings():
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.fixture
def theme_settings():
    return ThemeSettings(
        font_family="Poppins, Segoe UI, Arial, sans-serif",
        font_size=10,
        stylesheet_path=Path("gz_media.qss"),
        status_colors={"ok": "#10B981", "warn": "#F59E0B", "fail": "#EF4444"},
        logo_path=Path("assets/gz_logo_white.png"),
        claim_visible=True,
        claim_text="Emotions. Materialized.",
        action_bg_color="#E0E7FF",
        total_row_bg_color="#F3F4F6",
    )


@pytest.fixture
def mock_side_result_tracks():
    pdf_track = TrackInfo(title="Track 1", side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename="track1.wav", duration_sec=181.0, side="A", position=1)
    return SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=181.0,
        total_difference=1,
    )


def test_tracks_table_model_creation(tolerance_settings, theme_settings):
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    assert model.rowCount() == 0
    assert model.columnCount() == len(model._headers)


def test_update_data_populates_model(tolerance_settings, theme_settings, mock_side_result_tracks):
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(mock_side_result_tracks)
    # One track row + total row
    assert model.rowCount() == 2


def test_track_match_icon_ok(tolerance_settings, theme_settings, mock_side_result_tracks):
    """Test that successful match displays check icon via DecorationRole."""
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(mock_side_result_tracks)

    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)

    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()


def test_track_match_icon_fail(tolerance_settings, theme_settings, mock_side_result_tracks):
    """Test that failed match displays cross icon via DecorationRole."""
    failure_result = mock_side_result_tracks.model_copy()
    failure_result.wav_tracks[0] = failure_result.wav_tracks[0].model_copy(update={"duration_sec": 184.0})
    failure_result.total_difference = 4

    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(failure_result)

    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)

    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()


def test_track_match_display_empty(tolerance_settings, theme_settings, mock_side_result_tracks):
    """Test that Match column returns empty string for DisplayRole (icon only)."""
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(mock_side_result_tracks)

    index_match = model.index(0, 6)
    display_text = model.data(index_match, Qt.ItemDataRole.DisplayRole)

    # Verify DisplayRole returns empty string (icon is shown via DecorationRole)
    assert display_text == ""
