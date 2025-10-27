"""Delegate for rendering hover affordance on action cells in tables."""

from __future__ import annotations

from typing import Set

from PyQt6.QtCore import QModelIndex, QRect
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QAbstractItemView, QStyledItemDelegate, QStyle


def _darken_color(color: str, factor: float = 0.15) -> QColor:
    """Darken a hex color by a given factor (0.0 to 1.0).

    Args:
        color: Hex color string (e.g., '#E0E7FF')
        factor: Darkening factor (0.0-1.0, where 1.0 is black)

    Returns:
        QColor object
    """
    qcolor = QColor(color)
    if not qcolor.isValid():
        return QColor(color)

    # Reduce lightness by factor
    h, s, v, a = qcolor.getHsv()
    if v > 0:
        v = max(0, int(v * (1 - factor)))
    qcolor.setHsv(h, s, v, a)
    return qcolor


class ActionCellDelegate(QStyledItemDelegate):
    """Delegate that renders a subtle hover tint on action cells in specified columns.

    This delegate checks if a cell is in a configured action column and if the mouse
    is hovering over it. If so, it draws a slightly darker background tint before
    rendering the normal content.
    """

    def __init__(self, theme_settings, action_columns: Set[int] | list[int]):
        """Initialize the delegate.

        Args:
            theme_settings: ThemeSettings object with action_bg_color
            action_columns: Set or list of column indices that are action cells
        """
        super().__init__()
        self.theme_settings = theme_settings
        self.action_columns = set(action_columns)
        self._hovered_index: QModelIndex | None = None

    def paint(
        self,
        painter: QPainter,
        option,
        index,
    ) -> None:
        """Paint the cell with hover affordance if applicable.

        Args:
            painter: QPainter for drawing
            option: QStyleOptionViewItem with styling info
            index: QModelIndex of the cell
        """
        # Only apply hover effect for action columns
        if index.column() not in self.action_columns:
            super().paint(painter, option, index)
            return

        # Check if cell is hovered and not selected
        # Compare with the currently hovered index tracked via mouse events
        is_hovered = (
            self._hovered_index is not None
            and self._hovered_index.row() == index.row()
            and self._hovered_index.column() == index.column()
        )
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)

        if is_hovered and not is_selected:
            # Draw hover tint background
            hover_color = _darken_color(
                self.theme_settings.action_bg_color,
                factor=0.15,
            )
            painter.fillRect(option.rect, hover_color)

        # Call parent paint to render the icon and text
        super().paint(painter, option, index)

    def set_hovered_index(self, index: QModelIndex | None) -> None:
        """Set the currently hovered cell index.

        Args:
            index: QModelIndex of the hovered cell, or None if no cell is hovered
        """
        self._hovered_index = index
