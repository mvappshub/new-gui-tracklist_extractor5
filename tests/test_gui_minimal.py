#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from ui import MainWindow, AnalysisWorkerManager, load_export_settings, load_theme_settings, load_worker_settings
from adapters.ui.null_waveform_viewer import NullWaveformViewer

pytestmark = pytest.mark.gui

def test_gui_minimal(qtbot, isolated_config, tolerance_settings, id_extraction_settings):
    """Test minimal GUI initialization using proper fixtures."""

    # Dependencies are now loaded using fixtures or from the isolated_config
    export_settings = load_export_settings(isolated_config)
    theme_settings = load_theme_settings(isolated_config)
    worker_settings = load_worker_settings(isolated_config)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    window = MainWindow(
        tolerance_settings=tolerance_settings,
        export_settings=export_settings,
        theme_settings=theme_settings,
        waveform_viewer=NullWaveformViewer(),
        worker_manager=worker_manager,
        settings_filename=isolated_config.file,
        app_config=isolated_config,
    )
    qtbot.addWidget(window)

    assert window.isVisible() is False # We don't call show()
    assert "Final Cue Sheet Checker" in window.windowTitle()

