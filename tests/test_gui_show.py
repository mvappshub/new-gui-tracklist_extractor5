#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from PyQt6.QtCore import QTimer
from ui import MainWindow, AnalysisWorkerManager, load_tolerance_settings, load_export_settings, load_theme_settings, load_worker_settings, load_id_extraction_settings
from config import cfg, ConfigLoader
from adapters.ui.null_waveform_viewer import NullWaveformViewer

pytestmark = pytest.mark.gui

def test_gui_show(qapp, qtbot):
    """Test GUI show functionality."""
    print("Testing GUI show functionality...")

    # Mock dependencies for MainWindow constructor
    loader = ConfigLoader(cfg.settings)
    tolerance_settings = load_tolerance_settings(loader=loader)
    export_settings = load_export_settings(loader=loader)
    theme_settings = load_theme_settings(loader=loader)
    worker_settings = load_worker_settings(loader=loader)
    id_extraction_settings = load_id_extraction_settings(loader=loader)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    try:
        print("Creating MainWindow instance...")
        window = MainWindow(
            tolerance_settings=tolerance_settings,
            export_settings=export_settings,
            theme_settings=theme_settings,
            waveform_viewer=NullWaveformViewer(),
            worker_manager=worker_manager,
            settings_filename=cfg.file,
            app_config=cfg,
        )
        qtbot.addWidget(window)
        print("MainWindow created successfully")

        print("Showing MainWindow...")
        window.show()
        print("MainWindow shown successfully")

        # Allow the event loop to run briefly and then exit
        QTimer.singleShot(100, qapp.quit)
        qapp.exec()

    except Exception as e:
        print(f"GUI show error: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"GUI show error: {e}")
