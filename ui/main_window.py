from __future__ import annotations

import logging
import os
from pathlib import Path

from PyQt6.QtCore import QEvent, QModelIndex, QSize, Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.models.analysis import SideResult
from core.models.settings import ExportSettings, ToleranceSettings
from core.ports import WaveformViewerPort
from pdf_viewer import PdfViewerDialog
from services.export_service import export_results_to_json
from ui.config_models import ThemeSettings
from ui.constants import *
from ui.delegates.action_cell_delegate import ActionCellDelegate
from ui.dialogs.settings_dialog import SettingsDialog
from ui.models.results_table_model import ResultsTableModel
from ui.models.tracks_table_model import TracksTableModel
from ui.workers.worker_manager import AnalysisWorkerManager
from config import AppConfig


class MainWindow(QMainWindow):
    def _show_safe_message_box(
        self,
        title: str,
        text: str,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
    ):
        if os.getenv("QT_QPA_PLATFORM") == "offscreen":
            logging.error(f"MODAL_DIALOG_BLOCKED: Title: {title}, Text: {text}")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.exec()

    def __init__(
        self,
        *,
        tolerance_settings: ToleranceSettings,
        export_settings: ExportSettings,
        theme_settings: ThemeSettings,
        waveform_viewer: WaveformViewerPort,
        worker_manager: AnalysisWorkerManager,
        settings_filename: Path,
        app_config: AppConfig,
    ):
        super().__init__()
        self.tolerance_settings = tolerance_settings
        self.export_settings = export_settings
        self.theme_settings = theme_settings
        self.waveform_viewer = waveform_viewer
        self.worker_manager = worker_manager
        self.worker_manager.setParent(self)
        self.settings_filename = Path(settings_filename)
        self.app_config = app_config

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1200, 800)

        self.setup_menu_bar()

        central = QWidget(self)
        central.setObjectName("Main")
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setObjectName("MainToolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setProperty("analysis-state", "false")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.run_button = QPushButton(BUTTON_RUN_ANALYSIS)
        self.run_button.setObjectName("RunButton")
        self.toolbar.addWidget(self.run_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        self.filter_section = QWidget()
        filter_layout = QHBoxLayout(self.filter_section)
        filter_layout.setContentsMargins(8, 0, 8, 0)
        filter_layout.addWidget(QLabel(LABEL_FILTER))

        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("FilterCombo")
        self.filter_combo.addItems([FILTER_ALL, FILTER_OK, FILTER_FAIL, FILTER_WARN])
        self.filter_combo.setMinimumWidth(100)
        filter_layout.addWidget(self.filter_combo)
        self.toolbar.addWidget(self.filter_section)

        spacer_between = QWidget()
        spacer_between.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        spacer_between.setFixedWidth(16)
        self.toolbar.addWidget(spacer_between)

        self.status_box = QWidget()
        status_layout = QHBoxLayout(self.status_box)
        status_layout.setContentsMargins(8, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        status_layout.addWidget(self.progress_bar)

        self.status_label = QLabel(STATUS_READY)
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setMinimumWidth(220)
        status_layout.addWidget(self.status_label)
        self.toolbar.addWidget(self.status_box)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.top_table = QTableView()
        self.top_model = ResultsTableModel(theme_settings=self.theme_settings)
        self.top_table.setModel(self.top_model)
        try:
            self.top_table.setIconSize(QSize(16, 16))
        except Exception:
            pass

        self.bottom_table = QTableView()
        self.bottom_model = TracksTableModel(
            tolerance_settings=self.tolerance_settings, theme_settings=self.theme_settings
        )
        self.bottom_table.setModel(self.bottom_model)

        splitter.addWidget(self.top_table)
        splitter.addWidget(self.bottom_table)
        splitter.setSizes([300, 400])
        main_layout.addWidget(splitter)

        self.setCentralWidget(central)

        self.setup_tables()
        self.connect_signals()

        self._auto_resize_pending = False

        def _apply_header_resizes():
            if not hasattr(self, "top_table") or not hasattr(self, "bottom_table"):
                return

            h_header = self.top_table.horizontalHeader()
            for col in (0, 2, 3, 4, 5, 6, 7):
                h_header.resizeSection(col, self.top_table.sizeHintForColumn(col))

            h_header_b = self.bottom_table.horizontalHeader()
            for col in (0, 3, 4, 5, 6):
                h_header_b.resizeSection(col, self.bottom_table.sizeHintForColumn(col))

        def _schedule_header_resizes():
            if self._auto_resize_pending:
                return
            self._auto_resize_pending = True
            QTimer.singleShot(0, lambda: (setattr(self, "_auto_resize_pending", False), _apply_header_resizes()))

        self._schedule_header_resizes = _schedule_header_resizes  # type: ignore[assignment]
        self.top_model._schedule_header_resizes = _schedule_header_resizes  # type: ignore[attr-defined]

        if self.windowHandle() is not None:

            def _on_screen_changed(screen):
                try:
                    screen.logicalDotsPerInchChanged.connect(lambda _=None: _schedule_header_resizes())
                    screen.physicalDotsPerInchChanged.connect(lambda _=None: _schedule_header_resizes())
                except Exception:
                    pass
                _schedule_header_resizes()

            self.windowHandle().screenChanged.connect(_on_screen_changed)
            _on_screen_changed(self.windowHandle().screen())

        self.installEventFilter(self)

    def on_filter_changed(self, filter_text: str):
        self.top_model.set_filter(filter_text)
        if self.top_model.rowCount() > 0:
            self.top_table.selectRow(0)
        else:
            self.top_table.clearSelection()
            self.bottom_model.update_data(None)

    def setup_tables(self):
        self.top_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.top_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.top_table.setMouseTracking(True)
        self.bottom_table.setMouseTracking(True)

        h_header = self.top_table.horizontalHeader()
        h_header.setStretchLastSection(False)
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        h_header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.top_table.setColumnWidth(6, 60)
        self.top_table.setColumnWidth(7, 60)

        bold = h_header.font()
        bold.setBold(True)
        h_header.setFont(bold)

        h_header_bottom = self.bottom_table.horizontalHeader()
        bbold = h_header_bottom.font()
        bbold.setBold(True)
        h_header_bottom.setFont(bbold)
        h_header_bottom.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h_header_bottom.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h_header_bottom.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setStretchLastSection(True)
        self.bottom_table.setColumnWidth(1, 200)

        self.top_table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.bottom_table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.top_table.setAlternatingRowColors(True)
        self.bottom_table.setAlternatingRowColors(True)

        # Install hover affordance delegates for action cells
        self.top_delegate = ActionCellDelegate(self.theme_settings, {6, 7})
        self.top_table.setItemDelegateForColumn(6, self.top_delegate)
        self.top_table.setItemDelegateForColumn(7, self.top_delegate)

    def connect_signals(self):
        self.run_button.clicked.connect(self.run_analysis)
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        selection_model = self.top_table.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self.on_top_row_selected)
        self.top_table.clicked.connect(self.on_top_cell_clicked)
        self.bottom_table.clicked.connect(self.on_bottom_cell_clicked)

        # Connect hover tracking for action cell affordance
        self.top_table.entered.connect(lambda idx: self.top_delegate.set_hovered_index(idx))
        self.top_table.installEventFilter(self)

        self.worker_manager.progress.connect(lambda msg: self._set_status(msg, running=True))
        self.worker_manager.result_ready.connect(self.top_model.add_result)
        self.worker_manager.finished.connect(self.on_analysis_finished)

    def eventFilter(self, obj, event):
        event_type = event.type()
        if event_type in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.FontChange,
            QEvent.Type.ApplicationFontChange,
            QEvent.Type.Resize,
        ):
            if hasattr(self, "_schedule_header_resizes"):
                self._schedule_header_resizes()
        # Clear hover state when mouse leaves table
        elif event_type == QEvent.Type.Leave:
            if obj is self.top_table:
                self.top_delegate.set_hovered_index(None)
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "_schedule_header_resizes"):
            self._schedule_header_resizes()

    def closeEvent(self, event):
        self.worker_manager.cleanup()
        super().closeEvent(event)

    def run_analysis(self):
        if not self.worker_manager.is_running():
            self._set_analysis_state(True)
            self.run_button.setEnabled(False)
            self._set_status(STATUS_ANALYZING, running=True)
            self.top_model.clear()
            self.bottom_model.update_data(None)
            self.worker_manager.start_analysis()

    def _set_status(self, text: str, running: bool):
        self.progress_bar.setVisible(running)
        if len(text) > 50:
            for separator in [" - ", ": ", ", ", " "]:
                if separator in text[:45]:
                    parts = text.split(separator, 1)
                    text = parts[0] + separator.rstrip()
                    break
            else:
                text = text[:47] + "..."
        self.status_label.setText(text)

    def setup_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear()
        settings_menu = menubar.addMenu("Settings")
        settings_action = settings_menu.addAction("Open settings...")
        settings_action.triggered.connect(self.open_settings)

    def _set_analysis_state(self, is_analyzing: bool):
        try:
            self.setProperty("analysis-state", "true" if is_analyzing else "false")
            if is_analyzing and hasattr(self, "status_label") and self.status_label is not None:
                self.status_label.setText(STATUS_ANALYZING)
        except Exception as exc:
            logging.exception("Failed to set analysis state: %s", exc)

    def on_analysis_finished(self, message: str):
        self._set_analysis_state(False)
        logging.info("Analysis finished: %s", message)

        try:
            all_results = getattr(self.top_model, "all_results", lambda: [])()
        except Exception:
            all_results = []

        export_path = export_results_to_json(
            results=all_results,
            export_settings=self.export_settings,
        )

        if export_path is not None:
            ready_msg = f"{STATUS_READY} - {message} - Exported: {export_path.name}"
        else:
            ready_msg = f"{STATUS_READY} - {message}"
        self._set_status(ready_msg, running=False)
        self.run_button.setEnabled(True)
        if self.top_model.rowCount() > 0:
            self.top_table.selectRow(0)

    def on_top_row_selected(self, current: QModelIndex, previous: QModelIndex):
        result = self.top_model.get_result(current.row())
        self.bottom_model.update_data(result)

    def on_top_cell_clicked(self, index: QModelIndex):
        result = self.top_model.get_result(index.row())
        if not result:
            return
        if index.column() == 6 and result.pdf_path:
            try:
                pdf_dialog = PdfViewerDialog(result.pdf_path, self)
                pdf_dialog.exec()
            except Exception as exc:
                logging.error("Failed to open PDF viewer: %s", exc)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(result.pdf_path)))
        elif index.column() == 7 and result.zip_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(result.zip_path)))

    def on_bottom_cell_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        if index.column() != 1:
            logging.info("Bottom table click ignored: column=%s", index.column())
            return

        top_idx = self.top_table.currentIndex()
        if not top_idx.isValid():
            logging.info("Waveform viewer not opened: no top row selected.")
            return

        result = self.top_model.get_result(top_idx.row())
        if not result:
            logging.info("Waveform viewer not opened: no result for selected row.")
            return
        if not result.zip_path:
            logging.info("Waveform viewer not opened: missing ZIP path.")
            return

        side: SideResult | None = self.bottom_model._data
        if side is None:
            logging.info("Waveform viewer not opened: no side data available.")
            return

        if index.row() >= len(side.pdf_tracks):
            logging.info("Waveform viewer not opened: total row selected.")
            return

        if side.mode != "tracks":
            logging.info("Waveform viewer not opened: side mode %s unsupported.", side.mode)
            return

        if index.row() >= len(side.wav_tracks):
            logging.info("Waveform viewer not opened: missing WAV track at row %s.", index.row())
            return

        wav_track = side.wav_tracks[index.row()]
        wav_filename = getattr(wav_track, "filename", None)
        if not wav_filename:
            logging.info("Waveform viewer not opened: WAV filename missing for row %s.", index.row())
            return

        try:
            self.waveform_viewer.show(result.zip_path, wav_filename, self)
        except Exception as exc:
            logging.error("Failed to open waveform viewer: %s", exc, exc_info=True)

    def open_settings(self):
        try:
            settings_dialog = SettingsDialog(settings_filename=self.settings_filename, app_config=self.app_config, parent=self)
            settings_dialog.exec()
        except Exception as exc:
            logging.error("Failed to open settings dialog: %s", exc)

    def _update_gz_logo(self):
        try:
            if not hasattr(self, "gz_logo_label"):
                self.gz_logo_label = QLabel(parent=self)
                self.gz_logo_label.setObjectName("gzLogo")

            logo_path = self.theme_settings.logo_path

            if logo_path.exists():
                from PyQt6.QtGui import QPixmap

                pixmap = QPixmap(str(logo_path))
                scaled_pixmap = pixmap.scaledToHeight(24, Qt.TransformationMode.SmoothTransformation)
                self.gz_logo_label.setPixmap(scaled_pixmap)
                self.gz_logo_label.show()
            else:
                self.gz_logo_label.setText("GZ Media")
                logging.warning("GZ Media logo file not found at %s, using text fallback", logo_path)
        except Exception as exc:
            logging.error("Failed to load GZ Media logo: %s", exc)
            if hasattr(self, "gz_logo_label"):
                self.gz_logo_label.hide()

    def _update_gz_claim_visibility(self):
        try:
            if not hasattr(self, "gz_claim_label"):
                self.gz_claim_label = QLabel(parent=self)

            if self.theme_settings.claim_visible:
                self.gz_claim_label.setText(self.theme_settings.claim_text)
                self.gz_claim_label.show()
            else:
                self.gz_claim_label.hide()
        except Exception as exc:
            logging.error("Failed to update GZ Media claim: %s", exc)
            if hasattr(self, "gz_claim_label"):
                self.gz_claim_label.hide()
