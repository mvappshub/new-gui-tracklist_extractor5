#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QFont

from ui.models.tracks_table_model import TracksTableModel
from core.domain.analysis_status import AnalysisStatus
from ui.constants import TABLE_HEADERS_BOTTOM

pytestmark = pytest.mark.gui


@pytest.fixture
def tolerance_settings():
    """Reuse tolerance settings fixture with warn_tolerance=2."""
    from core.models.settings import ToleranceSettings
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.fixture
def theme_settings():
    """Reuse theme settings fixture for tracks table."""
    from pathlib import Path
    from core.models.settings import ThemeSettings
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
def mock_side_result_tracks(theme_settings):
    """Reuse fixture with PDF and WAV tracks in tracks mode."""
    from pathlib import Path
    from core.models.analysis import SideResult, TrackInfo, WavInfo
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


@pytest.mark.parametrize("column,role,is_total_row", [
    # Regular rows (is_total_row=False) - test all combinations
    (0, Qt.ItemDataRole.DisplayRole, False),
    (0, Qt.ItemDataRole.DecorationRole, False),
    (0, Qt.ItemDataRole.BackgroundRole, False),
    (0, Qt.ItemDataRole.ToolTipRole, False),
    (0, Qt.ItemDataRole.TextAlignmentRole, False),
    (0, Qt.ItemDataRole.FontRole, False),
    (0, Qt.ItemDataRole.AccessibleTextRole, False),
    (1, Qt.ItemDataRole.DisplayRole, False),
    (2, Qt.ItemDataRole.DisplayRole, False),
    (3, Qt.ItemDataRole.DisplayRole, False),
    (4, Qt.ItemDataRole.DisplayRole, False),
    (5, Qt.ItemDataRole.DisplayRole, False),
    (6, Qt.ItemDataRole.DisplayRole, False),
    (6, Qt.ItemDataRole.DecorationRole, False),
    (6, Qt.ItemDataRole.ToolTipRole, False),
    (6, Qt.ItemDataRole.AccessibleTextRole, False),
    (6, Qt.ItemDataRole.TextAlignmentRole, False),
    # Total row (is_total_row=True) - test all combinations
    (0, Qt.ItemDataRole.DisplayRole, True),
    (0, Qt.ItemDataRole.DecorationRole, True),
    (0, Qt.ItemDataRole.BackgroundRole, True),
    (0, Qt.ItemDataRole.ToolTipRole, True),
    (0, Qt.ItemDataRole.TextAlignmentRole, True),
    (0, Qt.ItemDataRole.FontRole, True),
    (0, Qt.ItemDataRole.AccessibleTextRole, True),
    (1, Qt.ItemDataRole.DisplayRole, True),
    (1, Qt.ItemDataRole.BackgroundRole, True),
    (1, Qt.ItemDataRole.FontRole, True),
    (2, Qt.ItemDataRole.DisplayRole, True),
    (2, Qt.ItemDataRole.BackgroundRole, True),
    (2, Qt.ItemDataRole.FontRole, True),
    (3, Qt.ItemDataRole.DisplayRole, True),
    (4, Qt.ItemDataRole.DisplayRole, True),
    (5, Qt.ItemDataRole.DisplayRole, True),
    (6, Qt.ItemDataRole.DisplayRole, True),
    (6, Qt.ItemDataRole.DecorationRole, True),
    (6, Qt.ItemDataRole.BackgroundRole, True),
    (6, Qt.ItemDataRole.ToolTipRole, True),
    (6, Qt.ItemDataRole.AccessibleTextRole, True),
    (6, Qt.ItemDataRole.TextAlignmentRole, True),
    (6, Qt.ItemDataRole.FontRole, True),
])
def test_tracks_table_model_data_roles_parametrized(tolerance_settings, theme_settings, mock_side_result_tracks, column, role, is_total_row):
    """
    Parametrized test covering all (column, role, row_type) combinations for TracksTableModel.data().

    GIVEN a TracksTableModel with tracks data
    WHEN data(index, role) is called for each column/role/row_type combination
    THEN appropriate values are returned according to model logic
    """
    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(mock_side_result_tracks)

    row = model.rowCount() - 1 if is_total_row else 0  # Last row is total row
    index = model.index(row, column)
    result = model.data(index, role)

    # DisplayRole tests
    if role == Qt.ItemDataRole.DisplayRole:
        if not is_total_row:  # Regular track rows
            if column == 0:
                assert result == 1, f"Column {column} should return track position"
            elif column == 1:
                assert result == "track1.wav", f"Column {column} should return WAV filename"
            elif column == 2:
                assert result == "Track 1", f"Column {column} should return track title"
            elif column == 3:
                assert result == "03:00", f"Column {column} should return formatted PDF duration"
            elif column == 4:
                assert result == "03:01", f"Column {column} should return formatted WAV duration"
            elif column == 5:
                assert result == "+1", f"Column {column} should return duration difference"
            elif column == 6:
                assert result == "", f"Column {column} should return empty string (icon via DecorationRole)"
        else:  # Total row
            if column == 0:
                assert result == "", f"Total row column {column} should be empty"
            elif column == 1:
                assert result == "Total (tracks)", f"Total row column {column} should show total label"
            elif column == 2:
                assert result == "1 tracks", f"Total row column {column} should show track count"
            elif column == 3:
                assert result == "03:00", f"Total row column {column} should show total PDF time"
            elif column == 4:
                assert result == "03:01", f"Total row column {column} should show total WAV time"
            elif column == 5:
                assert result == "+1", f"Total row column {column} should show total difference"
            elif column == 6:
                assert result == "", f"Total row column {column} should be empty (icon via DecorationRole)"

    # DecorationRole tests
    elif role == Qt.ItemDataRole.DecorationRole:
        if column == 6 and not is_total_row:
            # Regular row - should return check/cross icon based on tolerance
            assert isinstance(result, QIcon), f"Regular row column {column} should return QIcon"
            assert not result.isNull(), f"Regular row column {column} icon should not be null"
        elif column == 6 and is_total_row:
            # Total row - should return status icon
            assert isinstance(result, QIcon), f"Total row column {column} should return QIcon"
            assert not result.isNull(), f"Total row column {column} icon should not be null"
        else:
            assert result is None, f"Column {column} should return None for DecorationRole"

    # BackgroundRole tests
    elif role == Qt.ItemDataRole.BackgroundRole:
        if is_total_row:
            assert isinstance(result, QColor), f"Total row should return QColor for BackgroundRole"
            # Should match total_row_bg_color from theme_settings
        else:
            assert result is None, f"Regular row should return None for BackgroundRole"

    # ToolTipRole tests
    elif role == Qt.ItemDataRole.ToolTipRole:
        if column == 6 and not is_total_row:
            assert result == "Match OK", f"Column {column} tooltip should be 'Match OK' for matching track"
        elif column == 6 and is_total_row:
            assert result == "Match OK", f"Column {column} tooltip should be 'Match OK' for OK status"
        else:
            assert result is None, f"Column {column} should return None for ToolTipRole"

    # AccessibleTextRole tests
    elif role == Qt.ItemDataRole.AccessibleTextRole:
        if column == 6 and not is_total_row:
            assert result == "Match OK", f"Column {column} accessible text should be 'Match OK' for matching track"
        elif column == 6 and is_total_row:
            assert result == "Match OK", f"Column {column} accessible text should be 'Match OK' for OK status"
        else:
            assert result is None, f"Column {column} should return None for AccessibleTextRole"

    # TextAlignmentRole tests
    elif role == Qt.ItemDataRole.TextAlignmentRole:
        if column == 6:
            assert result == Qt.AlignmentFlag.AlignCenter, f"Column {column} should be center-aligned"
        else:
            assert result is None, f"Other columns should return None for TextAlignmentRole"

    # FontRole tests
    elif role == Qt.ItemDataRole.FontRole:
        if is_total_row:
            assert isinstance(result, QFont), f"Total row should return QFont for FontRole"
            assert result.bold(), f"Total row font should be bold"
        else:
            assert result is None, f"Regular row should return None for FontRole"

    # Other roles should return None
    else:
        assert result is None, f"Column {column}, role {role}, is_total_row {is_total_row} should return None"


def test_tracks_table_model_tracks_mode_with_exact_tolerance(tolerance_settings, theme_settings, mock_side_result_tracks):
    """
    Test track with difference exactly at warn_tolerance boundary.

    GIVEN a track with difference exactly at warn_tolerance (2.0)
    WHEN DecorationRole requested for match column
    THEN returns check icon (tolerance match)
    """
    # Create result where difference == tolerance (should get check icon)
    exact_tolerance_result = mock_side_result_tracks.model_copy()
    exact_tolerance_result.wav_tracks[0] = exact_tolerance_result.wav_tracks[0].model_copy(update={"duration_sec": 182.0})
    exact_tolerance_result.total_difference = 2.0

    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(exact_tolerance_result)

    index = model.index(0, 6)  # Match column, first track
    icon = model.data(index, Qt.ItemDataRole.DecorationRole)

    assert isinstance(icon, QIcon), "Should return QIcon for exact tolerance match"
    assert not icon.isNull(), "Exact tolerance match should not be null icon"


def test_tracks_table_model_tracks_mode_exceeding_tolerance(tolerance_settings, theme_settings, mock_side_result_tracks):
    """
    Test track with difference exceeding warn_tolerance.

    GIVEN a track with difference exceeding warn_tolerance (2.1 > 2.0)
    WHEN DecorationRole requested for match column
    THEN returns cross icon (tolerance exceeded)
    """
    # Create result where difference > tolerance (should get cross icon)
    exceed_tolerance_result = mock_side_result_tracks.model_copy()
    exceed_tolerance_result.wav_tracks[0] = exceed_tolerance_result.wav_tracks[0].model_copy(update={"duration_sec": 182.1})
    exceed_tolerance_result.total_difference = 2.1

    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(exceed_tolerance_result)

    index = model.index(0, 6)  # Match column, first track
    icon = model.data(index, Qt.ItemDataRole.DecorationRole)

    assert isinstance(icon, QIcon), "Should return QIcon for exceeded tolerance"
    assert not icon.isNull(), "Exceeded tolerance should not be null icon"


def test_tracks_table_model_side_mode(tolerance_settings, theme_settings):
    """
    Test side mode with single WAV file.

    GIVEN a side result in "side" mode
    WHEN data requested for various columns
    THEN PLACEHOLDER_DASH appears for missing WAV columns
    """
    from pathlib import Path
    from core.models.analysis import SideResult, TrackInfo, WavInfo

    pdf_track = TrackInfo(title="Side Track", side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename="full_side.wav", duration_sec=181.0, side="A", position=1)

    side_result = SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=None,
        side="A",
        mode="side",  # Side mode
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=181.0,
        total_difference=1,
    )

    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(side_result)

    # Test various columns for side mode
    index_row1_col1 = model.index(0, 1)  # WAV filename column (regular row)
    index_total_col1 = model.index(1, 1)  # WAV filename column (total row)

    # Regular row should show WAV filename
    assert model.data(index_row1_col1, Qt.ItemDataRole.DisplayRole) == "full_side.wav"

    # Total row should show the WAV filename (for side mode)
    assert model.data(index_total_col1, Qt.ItemDataRole.DisplayRole) == "full_side.wav"


def test_tracks_table_model_missing_wav_tracks(tolerance_settings, theme_settings):
    """
    Test missing WAV tracks (row index exceeds wav_tracks length).

    GIVEN a result with PDF tracks but missing WAV tracks
    WHEN data requested beyond available WAV tracks
    THEN PLACEHOLDER_DASH appears appropriately
    """
    from pathlib import Path
    from core.models.analysis import SideResult, TrackInfo

    pdf_track = TrackInfo(title="Track 1", side="A", position=1, duration_sec=180)

    # SideResult with PDF tracks but no WAV tracks
    missing_wav_result = SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.FAIL,  # Failed status due to missing WAV
        pdf_tracks=[pdf_track],
        wav_tracks=[],  # No WAV tracks available
        total_pdf_sec=180,
        total_wav_sec=0.0,
        total_difference=0,
    )

    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(missing_wav_result)

    # Test regular row columns
    index = model.index(0, 1)  # WAV filename column
    result = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert result == "-", "Missing WAV tracks should show PLACEHOLDER_DASH"

    # Test match column
    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)
    assert isinstance(icon, QIcon), "Should still return icon even with missing WAV tracks"


def test_tracks_table_model_total_row_not_selectable(tolerance_settings, theme_settings, mock_side_result_tracks):
    """
    Test that total row is not selectable (flags method).

    GIVEN a TracksTableModel with data
    WHEN flags() called for total row
    THEN ItemIsSelectable flag is not set
    """
    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(mock_side_result_tracks)

    total_row_index = model.index(model.rowCount() - 1, 0)  # Total row
    regular_row_index = model.index(0, 0)  # Regular row

    total_flags = model.flags(total_row_index)
    regular_flags = model.flags(regular_row_index)

    # Total row should not be selectable
    assert not (total_flags & Qt.ItemFlag.ItemIsSelectable), "Total row should not be selectable"

    # Regular row should be selectable (among other flags)
    assert (regular_flags & Qt.ItemFlag.ItemIsSelectable), "Regular row should be selectable"


@pytest.mark.parametrize("status,expected_tooltip", [
    (AnalysisStatus.OK, "Match OK"),
    (AnalysisStatus.FAIL, "No match"),
])
def test_tracks_table_model_total_row_status_variations(tolerance_settings, theme_settings, mock_side_result_tracks, status, expected_tooltip):
    """
    Test status variations affect total row tooltips and icons.

    GIVEN SideResult with different statuses
    WHEN total row DecorationRole and ToolTipRole requested
    THEN appropriate status-based results returned
    """
    status_result = mock_side_result_tracks.model_copy()
    status_result.status = status

    model = TracksTableModel(tolerance_settings, theme_settings)
    model.update_data(status_result)

    index = model.index(1, 6)  # Total row, match column

    tooltip = model.data(index, Qt.ItemDataRole.ToolTipRole)
    accessible_text = model.data(index, Qt.ItemDataRole.AccessibleTextRole)
    icon = model.data(index, Qt.ItemDataRole.DecorationRole)

    assert tooltip == expected_tooltip, f"Tooltip should be '{expected_tooltip}' for {status.value} status"
    assert accessible_text == expected_tooltip, f"Accessible text should be '{expected_tooltip}' for {status.value} status"
    assert isinstance(icon, QIcon), f"Should return QIcon for {status.value} status"
    assert not icon.isNull(), f"Status icon should not be null for {status.value}"
