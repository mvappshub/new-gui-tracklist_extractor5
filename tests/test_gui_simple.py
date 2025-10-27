#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import pytest
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

pytestmark = pytest.mark.gui


def test_basic_gui():
    """Test basic PyQt6 GUI functionality."""
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Test GUI")
    window.resize(400, 200)

    layout = QVBoxLayout()
    label = QLabel("PyQt6 GUI Test - Basic functionality works!")
    layout.addWidget(label)

    window.setLayout(layout)
    window.show()

    print("GUI launched successfully!")
    QTimer.singleShot(1000, app.quit)
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_basic_gui())
