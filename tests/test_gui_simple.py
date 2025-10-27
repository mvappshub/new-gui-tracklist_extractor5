#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

pytestmark = pytest.mark.gui


def test_basic_gui(qapp: QApplication, qtbot):
    """Test basic PyQt6 GUI functionality."""
    window = QWidget()
    window.setWindowTitle("Test GUI")
    window.resize(400, 200)

    layout = QVBoxLayout()
    label = QLabel("PyQt6 GUI Test - Basic functionality works!")
    layout.addWidget(label)

    window.setLayout(layout)
    window.show()

    qtbot.addWidget(window)
    QTimer.singleShot(100, window.close)
    qtbot.waitUntil(lambda: not window.isVisible(), timeout=1000)


if __name__ == "__main__":
    pytest.main([__file__])
