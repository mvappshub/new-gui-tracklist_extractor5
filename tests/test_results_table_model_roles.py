#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon

from ui.models.results_table_model import ResultsTableModel
from core.domain.analysis_status import AnalysisStatus
from ui.constants import TABLE_HEADERS_TOP

pytestmark = pytest.mark.gui


@pytest.fixture
def theme_settings():
    """Reuse theme settings fixture from existing tests."""
    from pathlib import Path
    from core.models.settings import ThemeSettings
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
def mock_side_result(theme_settings):
    """Reuse mock side result fixture with PDF and ZIP paths."""
    from pathlib import Path
    from core.models.analysis import SideResult
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


@pytest.mark.parametrize("column,role", [
    # Test all columns (0-7) with all relevant roles
    (0, Qt.ItemDataRole.DisplayRole),
    (0, Qt.ItemDataRole.DecorationRole),
    (0, Qt.ItemDataRole.BackgroundRole),
    (0, Qt.ItemDataRole.ForegroundRole),
    (0, Qt.ItemDataRole.ToolTipRole),
    (0, Qt.ItemDataRole.TextAlignmentRole),
    (0, Qt.ItemDataRole.FontRole),
    (1, Qt.ItemDataRole.DisplayRole),
    (1, Qt.ItemDataRole.DecorationRole),
    (1, Qt.ItemDataRole.BackgroundRole),
    (1, Qt.ItemDataRole.ForegroundRole),
    (1, Qt.ItemDataRole.ToolTipRole),
    (1, Qt.ItemDataRole.TextAlignmentRole),
    (1, Qt.ItemDataRole.FontRole),
    (2, Qt.ItemDataRole.DisplayRole),
    (3, Qt.ItemDataRole.DisplayRole),
    (4, Qt.ItemDataRole.DisplayRole),
    (5, Qt.ItemDataRole.DisplayRole),
    (5, Qt.ItemDataRole.BackgroundRole),
    (5, Qt.ItemDataRole.ForegroundRole),
    (5, Qt.ItemDataRole.TextAlignmentRole),
    (6, Qt.ItemDataRole.DisplayRole),  # Action column - no display role
    (6, Qt.ItemDataRole.DecorationRole),
    (6, Qt.ItemDataRole.BackgroundRole),
    (6, Qt.ItemDataRole.ToolTipRole),
    (6, Qt.ItemDataRole.TextAlignmentRole),
    (7, Qt.ItemDataRole.DisplayRole),  # Action column - no display role
    (7, Qt.ItemDataRole.DecorationRole),
    (7, Qt.ItemDataRole.BackgroundRole),
    (7, Qt.ItemDataRole.ToolTipRole),
    (7, Qt.ItemDataRole.TextAlignmentRole),
])
def test_results_table_model_data_roles_parametrized(theme_settings, mock_side_result, column, role):
    """
    Parametrized test covering all (column, role) combinations for ResultsTableModel.data().

    GIVEN a ResultsTableModel with a SideResult
    WHEN data(index, role) is called for each column/role combination
    THEN appropriate values are returned according to model logic
    """
    model = ResultsTableModel(theme_settings)
    model.add_result(mock_side_result)

    index = model.index(0, column)

    result = model.data(index, role)

    # DisplayRole tests
    if role == Qt.ItemDataRole.DisplayRole:
        if column == 0:
            assert result == 1, f"Column {column} should return row number"
        elif column == 1:
            assert result == "test.pdf", f"Column {column} should return filename"
        elif column == 2:
            assert result == "A", f"Column {column} should return side"
        elif column == 3:
            assert result == "tracks", f"Column {column} should return mode"
        elif column == 4:
            assert result == "01:40", f"Column {column} should return formatted time"
        elif column == 5:
            assert result == "OK", f"Column {column} should return status text"
        elif column in (6, 7):  # Action columns have no display role
            assert result is None, f"Action column {column} should return None for DisplayRole"

    # DecorationRole tests
    elif role == Qt.ItemDataRole.DecorationRole:
        if column == 6:  # PDF column
            assert isinstance(result, QIcon), f"Column {column} should return QIcon for DecorationRole"
        elif column == 7:  # ZIP column
            assert isinstance(result, QIcon), f"Column {column} should return QIcon for DecorationRole"
        else:
            assert result is None, f"Column {column} should return None for DecorationRole"

    # BackgroundRole tests
    elif role == Qt.ItemDataRole.BackgroundRole:
        if column == 5:  # Status column
            assert isinstance(result, QColor), f"Column {column} should return QColor for BackgroundRole"
        elif column in (6, 7):  # Action columns
            assert isinstance(result, QColor), f"Column {column} should return QColor for BackgroundRole"
        else:
            assert result is None, f"Column {column} should return None for BackgroundRole"

    # ForegroundRole tests
    elif role == Qt.ItemDataRole.ForegroundRole:
        if column == 5:  # Status column
            assert isinstance(result, QColor), f"Column {column} should return QColor for ForegroundRole"
            assert result.name().lower() == "#ffffff", f"Status column should use white text"
        else:
            assert result is None, f"Column {column} should return None for ForegroundRole"

    # ToolTipRole tests
    elif role == Qt.ItemDataRole.ToolTipRole:
        if column == 1:
            assert isinstance(result, str), f"Column {column} should return tooltip string"
            assert "PDF: test.pdf" in result, f"Column {column} tooltip should contain PDF info"
        elif column == 6:
            assert result == "Open PDF file", f"Column {column} should return 'Open PDF file'"
        elif column == 7:
            assert result == "Open ZIP archive", f"Column {column} should return 'Open ZIP archive'"
        else:
            assert result is None, f"Column {column} should return None for ToolTipRole"

    # TextAlignmentRole tests
    elif role == Qt.ItemDataRole.TextAlignmentRole:
        alignment = result
        if column in (6, 7):
            assert alignment == Qt.AlignmentFlag.AlignCenter, f"Action column {column} should center align"
        elif column in (0, 2):
            assert alignment == Qt.AlignmentFlag.AlignCenter, f"Column {column} should center align"
        elif column in (3, 4, 5):
            assert alignment == (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter), f"Column {column} should right align"
        elif column == 1:
            assert alignment == Qt.AlignmentFlag.AlignLeft, f"Column {column} should left align"

    # Other roles should return None
    else:
        assert result is None, f"Column {column}, role {role} should return None"


@pytest.mark.parametrize("status,expected_color", [
    (AnalysisStatus.OK, "#10B981"),
    (AnalysisStatus.WARN, "#F59E0B"),
    (AnalysisStatus.FAIL, "#EF4444"),
])
def test_results_table_model_status_colors(theme_settings, mock_side_result, status, expected_color):
    """
    GIVEN a ResultsTableModel with different status values
    WHEN BackgroundRole requested for status column
    THEN correct status colors are returned
    """
    mock_side_result.status = status

    model = ResultsTableModel(theme_settings)
    model.add_result(mock_side_result)

    index = model.index(0, 5)  # Status column
    background = model.data(index, Qt.ItemDataRole.BackgroundRole)

    assert isinstance(background, QColor)
    assert background.name().upper() == expected_color.upper(), \
        f"Status {status.value} should use color {expected_color}"


@pytest.mark.parametrize("invalid_row", [-1, 999])
def test_results_table_model_invalid_indices(theme_settings, mock_side_result, invalid_row):
    """
    GIVEN a ResultsTableModel with one result
    WHEN data() called with invalid row indices
    THEN None is returned for all roles
    """
    model = ResultsTableModel(theme_settings)
    model.add_result(mock_side_result)

    for column in range(len(TABLE_HEADERS_TOP)):
        for role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.BackgroundRole,
                     Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.ToolTipRole]:
            index = model.index(invalid_row, column)
            result = model.data(index, role)
            assert result is None, f"Invalid index ({invalid_row}, {column}) should return None for role {role}"


def test_results_table_model_empty_returns_zero_rows(theme_settings):
    """
    GIVEN a ResultsTableModel with no results
    WHEN rowCount() called
    THEN 0 is returned
    """
    model = ResultsTableModel(theme_settings)
    assert model.rowCount() == 0


@pytest.mark.parametrize("column", range(len(TABLE_HEADERS_TOP)))
def test_results_table_model_data_with_no_results(theme_settings, column):
    """
    GIVEN a ResultsTableModel with no results
    WHEN data() called for any column
    THEN None is returned
    """
    model = ResultsTableModel(theme_settings)

    index = model.index(0, column)
    result = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert result is None, f"Empty model should return None for column {column}"


def test_results_table_model_scenario_display_role_column_5_ok_status(theme_settings, mock_side_result):
    """
    Scenario: ResultsTableModel with OK status
    GIVEN a ResultsTableModel with OK status
    WHEN DisplayRole requested for column 5
    THEN returns 'OK'
    """
    model = ResultsTableModel(theme_settings)
    model.add_result(mock_side_result)

    index = model.index(0, 5)
    result = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert result == "OK"


def test_results_table_model_scenario_decoration_role_column_6(theme_settings, mock_side_result):
    """
    Scenario: ResultsTableModel with PDF file
    GIVEN a ResultsTableModel with PDF file in result
    WHEN DecorationRole requested for column 6
    THEN returns file icon
    """
    model = ResultsTableModel(theme_settings)
    model.add_result(mock_side_result)

    index = model.index(0, 6)  # PDF column
    result = model.data(index, Qt.ItemDataRole.DecorationRole)
    assert isinstance(result, QIcon)
