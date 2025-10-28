from __future__ import annotations

import logging
import os
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
)

from config import save_config, AppConfig
from ui.pages.settings_page import SettingsPage


class SettingsDialog(QDialog):
    """Modal settings dialog containing SettingsPage with Save/Cancel buttons."""

    settings_saved = pyqtSignal(object)

    def __init__(self, settings_filename: Path, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.settings_filename = Path(settings_filename)
        self._app_config = app_config
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.settings_page = SettingsPage(app_config, self.settings_filename, show_action_buttons=False)
        self.settings_page.settingChanged.connect(self._on_setting_changed)
        self.settings_page.saveRequested.connect(self._on_page_save_requested)
        self.settings_page.reloadRequested.connect(self._on_page_reload_requested)
        self.settings_page.resetRequested.connect(self._on_page_reset_requested)
        scroll_area.setWidget(self.settings_page)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

    def _show_safe_message_box(
        self,
        title: str,
        text: str,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
    ):
        if os.getenv("QT_QPA_PLATFORM") == "offscreen":
            logging.error(f"MODAL_DIALOG_BLOCKED: Title: {title}, Text: {text}")
            return

        parent = self.parent()
        if parent and hasattr(parent, "_show_safe_message_box"):
            parent._show_safe_message_box(title, text, icon)
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.exec()

    def _validate_settings(self) -> bool:
        """Validate settings before saving. Return True if valid, False if invalid."""
        errors = []

        # Check required paths are not empty
        for key, display_name in [
            ("input/pdf_dir", "PDF input directory"),
            ("input/wav_dir", "WAV input directory"),
            ("export/default_dir", "Export directory"),
        ]:
            value = self._app_config.get(key)
            if not value or str(value).strip() == "":
                errors.append(f"{display_name} cannot be empty")

        if errors:
            error_msg = "Please correct the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            self._show_safe_message_box(
                "Validation Error",
                error_msg,
                QMessageBox.Icon.Warning,
            )
            return False

        return True

    def _on_save(self) -> None:
        """Handle save button click - save config and accept dialog."""
        if self._validate_settings():
            if self._persist_settings():
                self.accept()

    def get_values(self) -> dict[str, object]:
        """Return current configuration values keyed by config path."""
        values = {}
        for key in self._app_config.get_all_keys():
            values[key] = self._app_config.get(key)
        return values

    def _persist_settings(self) -> bool:
        try:
            save_config(self.settings_filename)
        except Exception as exc:
            self._show_safe_message_box(
                "Save Error",
                f"Failed to save settings:\n{exc}",
                QMessageBox.Icon.Critical,
            )
            return False
        # fall through on success
        try:
            self.settings_saved.emit(self.get_values())
        except Exception as exc:
            logging.exception("Exception in settings_saved signal emission")
        return True

    def _on_setting_changed(self, key: str, value: object) -> None:
        try:
            self._app_config.set(key, value)
        except Exception as exc:
            self._show_safe_message_box(
                "Update Error",
                f"Failed to update setting '{key}':\n{exc}",
                QMessageBox.Icon.Critical,
            )

    def _on_page_save_requested(self) -> None:
        if self._persist_settings():
            self.settings_page._show_message("Settings saved", "Configuration saved successfully.", "info")

    def _on_page_reload_requested(self) -> None:
        try:
            self._app_config.settings.sync()
            self.settings_page._sync_from_config()
            self.settings_page._show_message("Settings reloaded", "Configuration reloaded from disk.", "info")
        except Exception as exc:
            self._show_safe_message_box(
                "Reload Error",
                f"Failed to reload settings:\n{exc}",
                QMessageBox.Icon.Critical,
            )

    def _on_page_reset_requested(self) -> None:
        try:
            self._app_config.reset_to_defaults()
            save_config(self.settings_filename)
            # save_config() already persists the config, no need for redundant save()
            self.settings_page._sync_from_config()
            self.settings_page._reenable_widgets()
            self.settings_page._show_message("Defaults restored", "All settings were reset to defaults.", "info")
        except Exception as exc:
            self._show_safe_message_box(
                "Reset Error",
                f"Failed to reset settings:\n{exc}",
                QMessageBox.Icon.Critical,
            )
