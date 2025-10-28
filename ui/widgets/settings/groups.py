from __future__ import annotations

from typing import Iterable, Sequence, Union

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)


def format_scale_option(option: Union[float, str]) -> str:
    if isinstance(option, (float, int)):
        return f"{int(float(option) * 100)}%"
    if isinstance(option, str) and option.upper() == "AUTO":
        return "Follow system"
    return str(option)


def normalize_scale_value(value: object) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        upper = stripped.upper()
        if upper == "FOLLOW SYSTEM":
            return "AUTO"
        if upper == "AUTO":
            return "AUTO"
        try:
            return float(stripped)
        except ValueError:
            return stripped
    return value


def coerce_folder(value: object) -> str:
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        iterator = iter(value)
        first = next(iterator, "")
        return str(first) if first else ""
    return str(value) if value else ""


class FolderSettingCard(QWidget):
    """Single-folder selector implemented with standard PyQt6 components."""

    settingChanged = pyqtSignal(str, str)

    def __init__(
        self,
        setting_key: str,
        initial_path: str = "",
        title: str | None = None,
        content: str | None = None,
        directory: str = "./",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setting_key = setting_key
        self._dialog_directory = directory

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        if title:
            title_label = QLabel(title)
            title_font = title_label.font()
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)

        if content:
            content_label = QLabel(content)
            content_label.setStyleSheet("color: gray;")
            layout.addWidget(content_label)

        controls_layout = QHBoxLayout()

        self.path_input = QLineEdit(self)
        self.path_input.setMinimumWidth(520)
        self.path_input.setClearButtonEnabled(True)
        self.path_input.editingFinished.connect(self._on_edit_finished)
        controls_layout.addWidget(self.path_input, 1)

        controls_layout.addSpacing(12)

        browse_button = QPushButton(self.tr("Browse"), self)
        browse_button.setFixedWidth(120)
        browse_button.clicked.connect(self._on_browse)
        controls_layout.addWidget(browse_button)

        layout.addLayout(controls_layout)

        self.set_path(initial_path, update_config=False)

    def set_path(self, path: str, update_config: bool = True) -> None:
        normalized = path or ""
        if self.path_input.text() != normalized:
            self.path_input.blockSignals(True)
            self.path_input.setText(normalized)
            self.path_input.blockSignals(False)
        if update_config and self.setting_key:
            self.settingChanged.emit(self.setting_key, normalized)

    def _on_edit_finished(self) -> None:
        path = self.path_input.text().strip()
        if self.setting_key:
            self.settingChanged.emit(self.setting_key, path)

    def _on_browse(self) -> None:
        current = self.path_input.text().strip() or self._dialog_directory
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), current)
        if folder and self.setting_key:
            self.set_path(folder, update_config=True)


class UiGroup(QGroupBox):
    """Group widget for user interface configuration."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        available_scales: Sequence[Union[str, float]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("User Interface", parent)
        self._available_scales = list(available_scales)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        scale_layout = QHBoxLayout()
        scale_label = QLabel("Interface scaling:")
        scale_label.setFixedWidth(150)
        scale_layout.addWidget(scale_label)

        self.scale_combo = QComboBox(self)
        for option in self._available_scales:
            label = format_scale_option(option)
            self.scale_combo.addItem(label, option)
        self.scale_combo.currentIndexChanged.connect(self._on_scale_index_changed)
        scale_layout.addWidget(self.scale_combo)
        scale_layout.addStretch()

        layout.addLayout(scale_layout)

    def _on_scale_index_changed(self, index: int) -> None:
        value = self.scale_combo.itemData(index, Qt.ItemDataRole.UserRole)
        canonical = normalize_scale_value(value if value is not None else self.scale_combo.currentText())
        self.settingChanged.emit("ui/dpi_scale", canonical)

    def sync_from_config(self, value: object) -> None:
        canonical = normalize_scale_value(value if value is not None else "AUTO")
        self.scale_combo.blockSignals(True)
        try:
            for index in range(self.scale_combo.count()):
                candidate = normalize_scale_value(self.scale_combo.itemData(index, Qt.ItemDataRole.UserRole))
                if candidate == canonical:
                    self.scale_combo.setCurrentIndex(index)
                    break
        finally:
            self.scale_combo.blockSignals(False)


class ModelGroup(QGroupBox):
    """Group widget for primary model selection."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        available_models: Sequence[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Model Configuration", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        model_layout = QHBoxLayout()
        label = QLabel("Primary model:")
        label.setFixedWidth(150)
        model_layout.addWidget(label)

        self.model_combo = QComboBox(self)
        self.model_combo.addItems(list(available_models))
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()

        layout.addLayout(model_layout)

    def _on_model_changed(self, value: str) -> None:
        self.settingChanged.emit("llm/model", value)

    def sync_from_config(self, model: str) -> None:
        self.model_combo.blockSignals(True)
        try:
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
        finally:
            self.model_combo.blockSignals(False)


class PathsGroup(QGroupBox):
    """Group widget for directory configuration."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        pdf_dir: str,
        wav_dir: str,
        export_dir: str,
        auto_export: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Directory Paths", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.pdf_card = FolderSettingCard(
            "input/pdf_dir",
            coerce_folder(pdf_dir),
            "PDF input directory",
            "Folder scanned for tracklist PDF files.",
            parent=self,
        )
        self.pdf_card.settingChanged.connect(self.settingChanged.emit)
        layout.addWidget(self.pdf_card)

        self.wav_card = FolderSettingCard(
            "input/wav_dir",
            coerce_folder(wav_dir),
            "WAV input directory",
            "Folder containing mastered WAV files.",
            parent=self,
        )
        self.wav_card.settingChanged.connect(self.settingChanged.emit)
        layout.addWidget(self.wav_card)

        self.export_card = FolderSettingCard(
            "export/default_dir",
            coerce_folder(export_dir),
            "Export directory",
            "Destination directory for generated reports.",
            parent=self,
        )
        self.export_card.settingChanged.connect(self.settingChanged.emit)
        layout.addWidget(self.export_card)

        # Auto-export toggle
        auto_export_layout = QHBoxLayout()
        auto_export_label = QLabel("Auto-export results:")
        auto_export_label.setFixedWidth(150)
        auto_export_layout.addWidget(auto_export_label)

        self.auto_export_toggle = QCheckBox("Automatically export results", self)
        self.auto_export_toggle.stateChanged.connect(self._on_auto_export_changed)
        auto_export_layout.addWidget(self.auto_export_toggle)
        auto_export_layout.addStretch()

        layout.addLayout(auto_export_layout)

    def _on_auto_export_changed(self, state: int) -> None:
        self.settingChanged.emit("export/auto", bool(state))

    def sync_paths(self, pdf_dir: str, wav_dir: str, export_dir: str, auto_export: bool = True) -> None:
        self.pdf_card.set_path(coerce_folder(pdf_dir), update_config=False)
        self.wav_card.set_path(coerce_folder(wav_dir), update_config=False)
        self.export_card.set_path(coerce_folder(export_dir), update_config=False)
        self.auto_export_toggle.blockSignals(True)
        try:
            self.auto_export_toggle.setChecked(auto_export)
        finally:
            self.auto_export_toggle.blockSignals(False)


class AnalysisGroup(QGroupBox):
    """Group widget for analysis tolerance sliders."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        warn_tolerance: int,
        fail_tolerance: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Analysis Configuration", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        warn_layout = QHBoxLayout()
        warn_label = QLabel("Warning tolerance:")
        warn_label.setFixedWidth(150)
        warn_layout.addWidget(warn_label)

        self.warn_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.warn_slider.setRange(1, 10)
        self.warn_slider.setFixedWidth(200)
        self.warn_slider.valueChanged.connect(self._on_warn_changed)
        warn_layout.addWidget(self.warn_slider)

        self.warn_value_label = QLabel(self)
        self.warn_value_label.setFixedWidth(30)
        self.warn_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn_layout.addWidget(self.warn_value_label)
        warn_layout.addStretch()

        layout.addLayout(warn_layout)

        fail_layout = QHBoxLayout()
        fail_label = QLabel("Failure tolerance:")
        fail_label.setFixedWidth(150)
        fail_layout.addWidget(fail_label)

        self.fail_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.fail_slider.setRange(1, 20)
        self.fail_slider.setFixedWidth(200)
        self.fail_slider.valueChanged.connect(self._on_fail_changed)
        fail_layout.addWidget(self.fail_slider)

        self.fail_value_label = QLabel(self)
        self.fail_value_label.setFixedWidth(30)
        self.fail_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fail_layout.addWidget(self.fail_value_label)
        fail_layout.addStretch()

        layout.addLayout(fail_layout)

        self.sync_from_config(warn_tolerance, fail_tolerance)

    def _on_warn_changed(self, value: int) -> None:
        self.warn_value_label.setText(f"{value}s")
        self.settingChanged.emit("analysis/tolerance_warn", value)

    def _on_fail_changed(self, value: int) -> None:
        self.fail_value_label.setText(f"{value}s")
        self.settingChanged.emit("analysis/tolerance_fail", value)

    def sync_from_config(self, warn_tolerance: int, fail_tolerance: int) -> None:
        self.warn_slider.blockSignals(True)
        self.fail_slider.blockSignals(True)
        try:
            self.warn_slider.setValue(int(warn_tolerance))
            self.warn_value_label.setText(f"{int(warn_tolerance)}s")
            self.fail_slider.setValue(int(fail_tolerance))
            self.fail_value_label.setText(f"{int(fail_tolerance)}s")
        finally:
            self.warn_slider.blockSignals(False)
            self.fail_slider.blockSignals(False)
