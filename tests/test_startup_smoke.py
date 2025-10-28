#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.config_models import (
    load_tolerance_settings,
    load_id_extraction_settings,
    load_export_settings,
    load_theme_settings,
    load_worker_settings,
)
from ui.workers.worker_manager import AnalysisWorkerManager
from ui.theme import get_custom_icon
from adapters.ui.null_waveform_viewer import NullWaveformViewer
import config as config_module

pytestmark = pytest.mark.gui


def test_headless_startup_smoke(qtbot, isolated_config, monkeypatch):
    """
    Headless startup smoke test (F-UIH1) that verifies the full DI wiring
    from app.py without calling app.exec().

    This test ensures:
    - All settings can be loaded via config loaders
    - AnalysisWorkerManager constructs successfully
    - MainWindow DI wiring works end-to-end
    - Fonts and stylesheets load without errors
    - Basic resource availability (icons)
    - Clean lifecycle management (show/close) without blocking dialogs
    """
    # Set headless environment (matches app.py behavior)
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    # Mirror app.py DI assembly (lines ~80-84)
    # Use isolated_config like app.py does
    config_loader = config_module.ConfigLoader(isolated_config.settings)

    tolerance_settings = load_tolerance_settings(loader=config_loader)
    id_extraction_settings = load_id_extraction_settings(loader=config_loader)
    export_settings = load_export_settings(loader=config_loader)
    theme_settings = load_theme_settings(loader=config_loader)
    worker_settings = load_worker_settings(loader=config_loader)

    # Create worker manager with all settings
    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    # Create MainWindow with full DI (no app_config in plan, use isolated_config)
    window = MainWindow(
        tolerance_settings=tolerance_settings,
        export_settings=export_settings,
        theme_settings=theme_settings,
        waveform_viewer=NullWaveformViewer(),
        worker_manager=worker_manager,
        settings_filename=isolated_config.file,
        app_config=isolated_config,
    )

    # Register window with qtbot
    qtbot.addWidget(window)

    # Should construct without exceptions
    assert window is not None
    assert window.windowTitle() == "Final Cue Sheet Checker"

    # Verify resources are available (icon loading works)
    check_icon = get_custom_icon('check')
    assert not check_icon.isNull(), "Custom icon 'check' should be available"

    # Test clean lifecycle without calling app.exec()
    window.show()

    # Close window clean (like main() would do if interrupted)
    window.close()

    # Let Qt process any pending events/cleanup
    app = QApplication.instance()
    if app:
        # Process pending events briefly to ensure clean shutdown
        QTimer.singleShot(10, lambda: None)  # Dummy timer to process events
        app.processEvents()
