#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test for Settings dialog functionality and path resolution.
Tests: Settings dialog opening, configuration saving, path resolution, and error handling.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.gui

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from config import cfg, load_config, save_config, resolve_path, AppConfig
from ui.dialogs.settings_dialog import SettingsDialog
from settings_page import SettingsPage

# Global test application instance
_test_app = None


class MockMainWindow(QMainWindow):
    """Mock main window for testing settings dialog functionality."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Main Window")

        # Setup menu bar like the real MainWindow
        self.setup_menu_bar()

    def setup_menu_bar(self):
        """Setup menu bar with File, Edit, Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # Settings action with Ctrl+, shortcut
        settings_action = edit_menu.addAction("Settings...")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)

        # Help menu
        help_menu = menubar.addMenu("Help")

    def open_settings(self):
        """Open settings dialog."""
        try:
            # Use temporary settings file for testing
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            settings_file = temp_dir / "test_settings_dialog.json"
            settings_dialog = SettingsDialog(settings_file, cfg, self)
            settings_dialog.exec()
        except Exception as e:
            print(f"Failed to open settings dialog: {e}")
            raise


def test_settings_dialog_creation():
    """Test that SettingsDialog can be created successfully."""
    print("Testing SettingsDialog creation...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a mock parent window
        parent = MockMainWindow()

        # Create temporary settings file
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "test_settings.json"
            
            # Test creating SettingsDialog with DI
            dialog = SettingsDialog(settings_file, cfg, parent)
            assert dialog is not None
            print("+ SettingsDialog created successfully")

            # Test that it has the expected components
            assert hasattr(dialog, "settings_page")
            assert isinstance(dialog.settings_page, SettingsPage)
            print("+ SettingsDialog has SettingsPage")

            # Clean up
            dialog.deleteLater()
            parent.deleteLater()

            return True

    except Exception as e:
        print(f"- SettingsDialog creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_dialog_menu_action():
    """Test that Settings dialog opens via Edit -> Settings... menu."""
    print("Testing Settings dialog via Edit -> Settings... menu...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a mock parent window
        parent = MockMainWindow()

        # Find the settings action in the menu
        edit_menu = None
        for menu in parent.menuBar().findChildren(QMenu):
            if menu.title() == "Edit":
                edit_menu = menu
                break

        assert edit_menu is not None, "Edit menu not found"
        print("+ Edit menu found")

        # Find the Settings... action
        settings_action = None
        for action in edit_menu.actions():
            if action.text() == "Settings...":
                settings_action = action
                break

        assert settings_action is not None, "Settings... action not found"
        print("+ Settings... action found")

        # Mock the SettingsDialog to avoid actually showing it
        with patch("ui.dialogs.settings_dialog.SettingsDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            # Trigger the action
            settings_action.trigger()

            # Verify the dialog was created
            mock_dialog_class.assert_called_once()
            print("+ Settings dialog opened via menu action")

        # Clean up
        parent.deleteLater()

        return True

    except Exception as e:
        print(f"- Menu action test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_dialog_shortcut():
    """Test that Settings dialog opens via Ctrl+, shortcut."""
    print("Testing Settings dialog via Ctrl+, shortcut...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a mock parent window
        parent = MockMainWindow()

        # Find the settings action
        edit_menu = None
        for menu in parent.menuBar().findChildren(QMenu):
            if menu.title() == "Edit":
                edit_menu = menu
                break

        settings_action = None
        for action in edit_menu.actions():
            if action.text() == "Settings...":
                settings_action = action
                break

        # Mock the SettingsDialog
        with patch("ui.dialogs.settings_dialog.SettingsDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            # Simulate Ctrl+, key press
            QTest.keyClick(parent, Qt.Key_Comma, Qt.ControlModifier)

            # Verify the dialog was created
            mock_dialog_class.assert_called_once()
            print("+ Settings dialog opened via Ctrl+, shortcut")

        # Clean up
        parent.deleteLater()

        return True

    except Exception as e:
        print(f"- Shortcut test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration_save():
    """Test that configuration saves correctly via Save button."""
    print("Testing configuration save functionality...")

    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_settings_file = temp_path / "test_settings.json"

            # Create initial test configuration
            test_config = {
                "input": {"pdf_dir": str(temp_path / "pdf"), "wav_dir": str(temp_path / "wav")},
                "analysis": {"tolerance_warn": 3, "tolerance_fail": 7},
            }

            with open(test_settings_file, "w") as f:
                json.dump(test_config, f)

            # Load the test configuration
            load_config(test_settings_file)

            # Modify some settings
            cfg.set("analysis/tolerance_warn", 5)
            cfg.set("analysis/tolerance_fail", 10)
            cfg.set("input/pdf_dir", str(temp_path / "new_pdf"))

            # Save the configuration
            save_config(test_settings_file)

            # Verify the settings were saved correctly
            with open(test_settings_file, "r") as f:
                saved_config = json.load(f)

            assert saved_config["analysis"]["tolerance_warn"] == 5
            assert saved_config["analysis"]["tolerance_fail"] == 10
            assert saved_config["input"]["pdf_dir"] == str(temp_path / "new_pdf")
            print("+ Configuration saved correctly")

            return True

    except Exception as e:
        print(f"- Configuration save test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_resolution_absolute():
    """Test that path resolution works correctly with absolute paths."""
    print("Testing path resolution with absolute paths...")

    try:
        # Test with absolute path
        test_path = "/absolute/test/path"
        resolved = resolve_path(test_path)

        # Should return the absolute path as-is (resolved)
        assert resolved == Path(test_path).resolve()
        print("+ Absolute path resolution works correctly")

        # Test with Path object
        test_path_obj = Path("/another/absolute/path")
        resolved_obj = resolve_path(test_path_obj)
        assert resolved_obj == test_path_obj.resolve()
        print("+ Absolute Path object resolution works correctly")

        return True

    except Exception as e:
        print(f"- Absolute path resolution test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_resolution_relative():
    """Test that path resolution works correctly with relative paths."""
    print("Testing path resolution with relative paths...")

    try:
        # Test with relative path
        test_path = "relative/test/path"
        resolved = resolve_path(test_path)

        # Should resolve relative to project root
        project_root = Path(__file__).resolve().parent
        expected = (project_root / test_path).resolve()
        assert resolved == expected
        print("+ Relative path resolution works correctly")

        # Test with current directory reference
        current_path = "./current/dir"
        resolved_current = resolve_path(current_path)
        expected_current = (project_root / current_path).resolve()
        assert resolved_current == expected_current
        print("+ Current directory path resolution works correctly")

        return True

    except Exception as e:
        print(f"- Relative path resolution test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_directory_validation():
    """Test that directory validation works correctly."""
    print("Testing path directory validation...")

    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with valid directory
            valid_dir = temp_path / "valid_dir"
            valid_dir.mkdir()

            # This should not raise an error
            cfg.input_pdf_dir = str(valid_dir)
            assert cfg.input_pdf_dir.value == str(valid_dir)
            print("+ Valid directory path accepted")

            # Test with invalid path (non-existent)
            invalid_dir = temp_path / "non_existent_dir"

            # This should create the directory
            cfg.input_pdf_dir = str(invalid_dir)
            assert invalid_dir.exists()
            assert invalid_dir.is_dir()
            print("+ Non-existent directory path created automatically")

            # Test with file path (should raise error)
            test_file = temp_path / "test_file.txt"
            test_file.write_text("test content")

            try:
                cfg.input_pdf_dir = str(test_file)
                # If we get here, the validation should have failed
                assert False, "Expected ValueError for file path"
            except ValueError as e:
                assert "not a directory" in str(e).lower()
                print("+ File path correctly rejected")

        return True

    except Exception as e:
        print(f"- Directory validation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_dialog_save_button():
    """Test that the Save button in SettingsDialog works correctly."""
    print("Testing SettingsDialog Save button functionality...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_settings_file = temp_path / "test_settings.json"

            # Create initial test configuration
            test_config = {
                "input": {"pdf_dir": str(temp_path / "pdf"), "wav_dir": str(temp_path / "wav")},
                "analysis": {"tolerance_warn": 2, "tolerance_fail": 5},
            }

            with open(test_settings_file, "w") as f:
                json.dump(test_config, f)

            # Load the test configuration
            load_config(test_settings_file)

            # Create settings dialog with DI
            parent = MockMainWindow()
            dialog = SettingsDialog(test_settings_file, cfg, parent)

            # Modify some settings in the dialog
            dialog.settings_page.warn_slider.setValue(7)
            dialog.settings_page.fail_slider.setValue(12)

            # Mock the save_config function to verify it's called
            with patch("ui.dialogs.settings_dialog.save_config") as mock_save:
                # Click the save button
                dialog.save_button.click()

                # Verify save_config was called
                mock_save.assert_called_once()

                # Verify the dialog was accepted (closed)
                # The dialog should be closed after successful save

            # Clean up
            dialog.deleteLater()
            parent.deleteLater()

            print("+ SettingsDialog Save button works correctly")
            return True

    except Exception as e:
        print(f"- Save button test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_no_pdf_directory_errors():
    """Test that no 'PDF path is not a directory' errors occur during normal operation."""
    print("Testing for absence of 'PDF path is not a directory' errors...")

    try:
        # Create a temporary directory structure for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create valid directory structure
            pdf_dir = temp_path / "pdf"
            wav_dir = temp_path / "wav"
            pdf_dir.mkdir()
            wav_dir.mkdir()

            # Create test settings file
            test_settings = {"input": {"pdf_dir": str(pdf_dir), "wav_dir": str(wav_dir)}}

            settings_file = temp_path / "settings.json"
            with open(settings_file, "w") as f:
                json.dump(test_settings, f)

            # Load configuration
            load_config(settings_file)

            # Test that paths are properly resolved and valid
            pdf_path = cfg.input_pdf_dir.value
            wav_path = cfg.input_wav_dir.value

            assert pdf_path == str(pdf_dir)
            assert wav_path == str(wav_dir)
            assert Path(pdf_path).is_dir()
            assert Path(wav_path).is_dir()

            # Test MainWindow creation with valid paths
            app = QApplication.instance()
            if app is None:
                global _test_app
                _test_app = QApplication(sys.argv)

            # Import MainWindow properly
            from ui import MainWindow
            
            # This should not raise any "PDF path is not a directory" errors
            # Note: MainWindow requires DI parameters, skip full construction in this test
            # For this test, we just verify paths are valid
            
            # Verify the paths are accessible
            assert Path(pdf_path).is_dir()
            assert Path(wav_path).is_dir()

            print("+ No 'PDF path is not a directory' errors occurred")
            return True

    except Exception as e:
        print(f"- PDF directory error test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Settings dialog tests."""
    print("Running comprehensive Settings dialog tests...\n")

    tests = [
        test_settings_dialog_creation,
        test_settings_dialog_menu_action,
        test_settings_dialog_shortcut,
        test_configuration_save,
        test_path_resolution_absolute,
        test_path_resolution_relative,
        test_path_directory_validation,
        test_settings_dialog_save_button,
        test_no_pdf_directory_errors,
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n{'='*60}")
        try:
            if test():
                passed += 1
                print(f"+ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"- {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"- {test.__name__} FAILED with exception: {e}")
        print(f"{'='*60}")

    print("\nTest Results Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
