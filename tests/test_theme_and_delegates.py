#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QColor, QPainter, QIcon
from PyQt6.QtWidgets import QStyle, QStyleOptionViewItem, QApplication

from ui.theme import get_custom_icon
from ui.delegates.action_cell_delegate import ActionCellDelegate
from core.models.settings import ThemeSettings

pytestmark = pytest.mark.gui


@pytest.fixture
def theme_settings():
    """Provide test theme settings for delegate tests."""
    return ThemeSettings(
        action_bg_color="#E0E7FF",
        status_ok_color="#10B981",
        status_warn_color="#F59E0B",
        status_fail_color="#EF4444",
        font_family="Arial",
        font_size=12,
        stylesheet_path=None,
    )


@pytest.mark.gui
def test_get_custom_icon_existing_asset(qapp):
    """Test get_custom_icon('check') returns non-null QIcon when asset exists."""
    # Test loading existing icon
    icon = get_custom_icon('check')
    assert not icon.isNull(), "Custom icon 'check' should load successfully"


@pytest.mark.gui
def test_get_custom_icon_nonexistent_fallback(qapp):
    """Test get_custom_icon('nonexistent') falls back to system icon or empty QIcon without crashing."""
    # Test loading nonexistent icon
    icon = get_custom_icon('nonexistent_icon_xyz')

    # Should not crash, and should be either a fallback or empty icon
    # (Empty is acceptable since there's no system fallback for unknown icons)
    assert isinstance(icon, QIcon), "Should return a QIcon object even for nonexistent icons"


@pytest.mark.gui
def test_icon_caching(qapp):
    """Test icon caching by calling get_custom_icon twice and verifying identical cacheKey values."""
    # First call
    icon1 = get_custom_icon('check')

    # Second call should return cached icon
    icon2 = get_custom_icon('check')

    # Both should be valid and have identical cacheKey values
    assert not icon1.isNull(), "First icon should be valid"
    assert not icon2.isNull(), "Second icon should be valid"
    assert icon1.cacheKey() == icon2.cacheKey(), "Both icons should have identical cacheKey values"


@pytest.mark.gui
def test_hidpi_icon_rendering(qapp, monkeypatch):
    """Test HiDPI icon rendering by mocking devicePixelRatio > 1 and verifying icon is still valid."""
    # Mock devicePixelRatio > 1 (HiDPI screen)
    mock_screen = MagicMock()
    mock_screen.devicePixelRatio.return_value = 2.0

    # Mock QApplication.primaryScreen() to return our mock
    with patch.object(QApplication, 'primaryScreen', return_value=mock_screen):
        icon = get_custom_icon('check')

        # Icon should still be valid even in HiDPI context
        assert not icon.isNull()


@pytest.mark.gui
def test_darken_color_function(theme_settings):
    """Test color darkening by exercising public paint() behavior."""
    delegate = ActionCellDelegate(theme_settings, {6})

    # Create mock index and set it as hovered
    index = MagicMock()
    index.column.return_value = 6
    index.row.return_value = 0
    delegate.set_hovered_index(index)

    # Create mock option with no selection
    option = QStyleOptionViewItem()
    option.rect = MagicMock()  # QRect mock
    option.state = QStyle.StateFlag.State_None  # Not selected

    # Mock painter to capture fillRect calls
    painter = MagicMock()
    painter.fillRect = MagicMock()

    # Call paint to trigger darkening behavior
    delegate.paint(painter, option, index)

    # Verify fillRect was called with darkened color
    assert painter.fillRect.called, "Should fill background for hovered action cell"

    # Extract the color used for darkening
    call_args = painter.fillRect.call_args
    fill_color = call_args[0][1]  # Second argument should be the color

    # Verify the fill color is darker than the original action background
    assert isinstance(fill_color, QColor), "Background should be filled with QColor"
    assert fill_color.isValid(), "Fill color should be valid"

    # Compare with original color to ensure darkening
    original_color = QColor(theme_settings.action_bg_color)
    _, _, original_value, _ = original_color.getHsvF()
    _, _, fill_value, _ = fill_color.getHsvF()

    # The fill color should be darker (lower value) than the original
    assert fill_value < original_value, f"Fill color {fill_color.name()} should be darker than {original_color.name()}"


@pytest.mark.gui
def test_action_cell_delegate_creation(theme_settings):
    """Test ActionCellDelegate construction and basic properties."""
    columns = {6, 7}
    delegate = ActionCellDelegate(theme_settings, columns)

    assert delegate.theme_settings == theme_settings
    assert delegate.action_columns == columns


@pytest.mark.gui
def test_hovered_cell_gets_darker_background(theme_settings):
    """
    Scenario: Hovered cell gets darker background
    GIVEN delegate with hovered index set to (row=0, col=6)
    WHEN paint() is called for that index
    THEN painter.fillRect() is called with darkened color
    """
    delegate = ActionCellDelegate(theme_settings, {6})

    # Create mock index for column 6
    index = MagicMock()
    index.column.return_value = 6
    index.row.return_value = 0
    delegate.set_hovered_index(index)  # Set the same hovered index

    # Create mock option with no selection
    option = QStyleOptionViewItem()
    option.rect = MagicMock()  # QRect mock
    option.state = QStyle.StateFlag.State_None  # Not selected

    # Mock painter
    painter = MagicMock()
    painter.fillRect = MagicMock()

    # WHEN paint is called with the same index
    delegate.paint(painter, option, index)

    # THEN fillRect should be called with darkened color
    assert painter.fillRect.called, "Should fill background for hovered action cell"

    # Verify the color passed is a QColor (darkened version)
    call_args = painter.fillRect.call_args
    fill_color = call_args[0][1]  # Second argument should be the color
    assert isinstance(fill_color, QColor), "Background should be filled with QColor"


@pytest.mark.gui
def test_non_hovered_cell_uses_default_rendering(theme_settings):
    """
    Scenario: Non-hovered cell uses default rendering
    GIVEN delegate with no hovered index
    WHEN paint() is called
    THEN no custom background is drawn
    """
    delegate = ActionCellDelegate(theme_settings, {6})
    delegate.set_hovered_index(None)  # No hover

    # Mock painter that tracks fillRect calls
    painter = MagicMock()
    painter.fillRect = MagicMock()

    option = QStyleOptionViewItem()
    option.state = QStyle.StateFlag.State_None

    # Mock index for action column but not hovered
    index = MagicMock()
    index.column.return_value = 6
    index.row.return_value = 0

    # WHEN paint is called
    delegate.paint(painter, option, index)

    # THEN no custom background should be drawn
    assert not painter.fillRect.called, "Non-hovered action cell should not get custom background"


@pytest.mark.gui
def test_selected_cell_ignores_hover(theme_settings):
    """
    Scenario: Selected cell ignores hover
    GIVEN a selected cell (option.state has State_Selected)
    WHEN paint() is called even with hover
    THEN no hover tint is applied
    """
    delegate = ActionCellDelegate(theme_settings, {6})
    delegate.set_hovered_index(QModelIndex())  # Set hover index

    # Create selected cell option
    option = QStyleOptionViewItem()
    option.state = QStyle.StateFlag.State_Selected  # Selected!

    painter = MagicMock()
    painter.fillRect = MagicMock()

    index = MagicMock()
    index.column.return_value = 6
    index.row.return_value = 0

    # WHEN paint is called on selected cell
    delegate.paint(painter, option, index)

    # THEN no hover tint applied
    assert not painter.fillRect.called, "Selected cell should not get hover tint"


@pytest.mark.gui
def test_non_action_column_no_custom_rendering(theme_settings):
    """
    Test that non-action columns don't get custom rendering."""
    delegate = ActionCellDelegate(theme_settings, {6, 7})

    painter = MagicMock()
    painter.fillRect = MagicMock()

    option = QStyleOptionViewItem()
    option.state = QStyle.StateFlag.State_None

    # Mock index for non-action column (e.g., column 0)
    index = MagicMock()
    index.column.return_value = 0
    index.row.return_value = 0

    # WHEN paint is called for non-action column
    delegate.paint(painter, option, index)

    # THEN no custom background should be drawn
    assert not painter.fillRect.called, "Non-action columns should not get custom rendering"


@pytest.mark.gui
def test_delegate_hover_index_tracking(theme_settings):
    """Test setting and clearing hover index."""
    delegate = ActionCellDelegate(theme_settings, {6})

    # Initially no hover
    assert delegate._hovered_index is None

    # Set hover index
    mock_index = QModelIndex()
    delegate.set_hovered_index(mock_index)
    assert delegate._hovered_index is mock_index

    # Clear hover
    delegate.set_hovered_index(None)
    assert delegate._hovered_index is None
