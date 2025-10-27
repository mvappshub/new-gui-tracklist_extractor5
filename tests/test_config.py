#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import config as config_module


def test_config(isolated_config):
    """Test configuration system functionality."""
    print("Testing configuration system...")

    try:
        # Test basic config access via isolated fixture (monkeypatched in config_module)
        cfg = config_module.cfg
        print(f"LLM Model: {cfg.llm_model}")
        print(f"PDF Dir: {cfg.input_pdf_dir}")
        print(f"WAV Dir: {cfg.input_wav_dir}")
        print(f"Export Dir: {cfg.export_default_dir}")
        print(f"UI Theme: {cfg.ui_theme}")
        print(f"UI Font Size: {cfg.ui_base_font_size}")
        print(f"Analysis Tolerance: {cfg.analysis_tolerance_warn}")

        print("Configuration system works correctly!")
        assert True

    except Exception as e:
        print(f"Configuration error: {e}")
        pytest.fail(f"Configuration error: {e}")


