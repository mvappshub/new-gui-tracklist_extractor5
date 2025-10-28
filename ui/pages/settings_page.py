from __future__ import annotations


from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QFrame,
)

from pathlib import Path
from typing import TYPE_CHECKING

from config import AVAILABLE_DPI_SCALES, AVAILABLE_LLM_MODELS
from ui.widgets.settings import UiGroup, ModelGroup, PathsGroup, AnalysisGroup

if TYPE_CHECKING:
    from config import AppConfig


class SettingsPage(QWidget):
    """Application settings interface."""

    settingChanged = pyqtSignal(str, object)
    saveRequested = pyqtSignal()
    reloadRequested = pyqtSignal()
    resetRequested = pyqtSignal()

    def __init__(
        self,
        app_config: "AppConfig",
        settings_filename: Path,
        show_action_buttons: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("settingsPage")
        # Store injected configuration for future use
        self.cfg = app_config
        self.settings_filename = settings_filename
        self.show_action_buttons = show_action_buttons

        self._init_ui()
        self._sync_from_config()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)  # No frame
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)

        self.ui_group = UiGroup(AVAILABLE_DPI_SCALES, parent=self.container)
        self.ui_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.ui_group)

        self.model_group = ModelGroup(AVAILABLE_LLM_MODELS, parent=self.container)
        self.model_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.model_group)

        self.paths_group = PathsGroup(
            pdf_dir=self.cfg.get("input/pdf_dir", "./data/pdf"),
            wav_dir=self.cfg.get("input/wav_dir", "./data/wav"),
            export_dir=self.cfg.get("export/default_dir", "exports"),
            auto_export=self.cfg.get("export/auto", True),
            parent=self.container,
        )
        self.paths_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.paths_group)

        warn_default = getattr(self.cfg.analysis_tolerance_warn, "value", self.cfg.get("analysis/tolerance_warn", 2))
        fail_default = getattr(self.cfg.analysis_tolerance_fail, "value", self.cfg.get("analysis/tolerance_fail", 5))
        self.analysis_group = AnalysisGroup(int(warn_default), int(fail_default), parent=self.container)
        self.analysis_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.analysis_group)

        self._build_actions_group()

        self.container_layout.addStretch(1)


    def _build_actions_group(self) -> None:
        # Skip action buttons if embedded in dialog (dialog has its own buttons)
        if not self.show_action_buttons:
            return

        group = QGroupBox("Actions", self.container)
        group_layout = QVBoxLayout(group)

        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setFixedHeight(40)
        self.save_button.clicked.connect(self._save_settings)
        group_layout.addWidget(self.save_button)

        # Reload button
        self.reload_button = QPushButton("Reload Settings")
        self.reload_button.setFixedHeight(40)
        self.reload_button.clicked.connect(self._reload_settings)
        group_layout.addWidget(self.reload_button)

        # Reset button
        self.reset_button = QPushButton("Reset to defaults")
        self.reset_button.setFixedHeight(40)
        self.reset_button.clicked.connect(self._reset_settings)
        group_layout.addWidget(self.reset_button)

        self.container_layout.addWidget(group)


    def _save_settings(self) -> None:
        self.saveRequested.emit()

    def _reload_settings(self) -> None:
        self.reloadRequested.emit()

    def _reset_settings(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset settings",
            "This will restore all settings to their default values.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.resetRequested.emit()

    def _reenable_widgets(self) -> None:
        scroll = getattr(self, "scroll", None)
        if scroll is not None:
            scroll.setEnabled(True)
            viewport = scroll.viewport()
            if viewport is not None:
                viewport.setEnabled(True)
        container = getattr(self, "container", None)
        if container is not None:
            container.setEnabled(True)

    def _sync_from_config(self) -> None:
        if hasattr(self, "paths_group"):
            self.paths_group.sync_paths(
                self.cfg.get("input/pdf_dir", "./data/pdf"),
                self.cfg.get("input/wav_dir", "./data/wav"),
                self.cfg.get("export/default_dir", "exports"),
                self.cfg.get("export/auto", True),
            )

        if hasattr(self, "ui_group"):
            raw_scale = getattr(self.cfg.ui_dpi_scale, "value", self.cfg.get("ui/dpi_scale", "AUTO"))
            self.ui_group.sync_from_config(raw_scale)

        if hasattr(self, "model_group"):
            model_value = getattr(self.cfg.llm_model, "value", self.cfg.get("llm/model", AVAILABLE_LLM_MODELS[0]))
            self.model_group.sync_from_config(model_value)

        if hasattr(self, "analysis_group"):
            warn_value = getattr(self.cfg.analysis_tolerance_warn, "value", self.cfg.get("analysis/tolerance_warn", 2))
            fail_value = getattr(self.cfg.analysis_tolerance_fail, "value", self.cfg.get("analysis/tolerance_fail", 5))
            self.analysis_group.sync_from_config(int(warn_value), int(fail_value))

    def _show_message(self, title: str, content: str, message_type: str = "info") -> None:
        if message_type == "error":
            QMessageBox.critical(self, title, content)
        elif message_type == "warning":
            QMessageBox.warning(self, title, content)
        else:
            QMessageBox.information(self, title, content)
