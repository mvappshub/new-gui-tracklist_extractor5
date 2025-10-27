#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from ui import MainWindow, AnalysisWorkerManager, load_tolerance_settings, load_export_settings, load_theme_settings, load_worker_settings, load_id_extraction_settings
from config import AppConfig
from adapters.ui.null_waveform_viewer import NullWaveformViewer

pytestmark = pytest.mark.gui


def test_gui_show(qapp, qtbot, isolated_config: AppConfig):
    """Test GUI show functionality."""

    # Mock dependencies for MainWindow constructor using isolated config
    tolerance_settings = load_tolerance_settings(cfg=isolated_config)
    export_settings = load_export_settings(cfg=isolated_config)
    theme_settings = load_theme_settings(cfg=isolated_config)
    worker_settings = load_worker_settings(cfg=isolated_config)
    id_extraction_settings = load_id_extraction_settings(cfg=isolated_config)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    try:
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

        window.show()
        qtbot.waitUntil(window.isVisible, timeout=1000)
        qtbot.wait(100)

        window.close()
        qtbot.waitUntil(lambda: not window.isVisible(), timeout=1000)

    except Exception as e:
        import traceback
        traceback.print_exc()
        pytest.fail(f"GUI show error: {e}")
