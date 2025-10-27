#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Viewer Module for Tracklist Extractor
Provides custom PDF viewing functionality
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from pathlib import Path


class PdfViewerDialog(QDialog):
    """Custom PDF viewer dialog using system default viewer."""

    def __init__(self, pdf_path: Path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.setWindowTitle(f"PDF Viewer - {pdf_path.name}")
        self.resize(900, 700)

        # Create layout
        layout = QVBoxLayout(self)

        # For now, just open with system viewer and close dialog
        # In future, this could be extended with embedded PDF viewer
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path)))
        except Exception as e:
            print(f"Failed to open PDF: {e}")

        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

        # Auto-close after opening (since we're using system viewer)
        self.accept()
