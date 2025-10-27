from __future__ import annotations

import logging
from PyQt6.QtCore import QObject, pyqtSignal

from core.models.settings import IdExtractionSettings, ToleranceSettings
from services.analysis_service import AnalysisService
from ui.config_models import WorkerSettings


class AnalysisWorker(QObject):
    """Runs the analysis service in a background thread with injected settings."""

    progress = pyqtSignal(str)
    result_ready = pyqtSignal(object)
    finished = pyqtSignal(str)

    def __init__(
        self,
        worker_settings: WorkerSettings,
        tolerance_settings: ToleranceSettings,
        id_extraction_settings: IdExtractionSettings,
    ):
        super().__init__()
        self.worker_settings = worker_settings
        self.tolerance_settings = tolerance_settings
        self.id_extraction_settings = id_extraction_settings

    def run(self) -> None:
        try:
            service = AnalysisService(
                tolerance_settings=self.tolerance_settings,
                id_extraction_settings=self.id_extraction_settings,
            )
            service.start_analysis(
                pdf_dir=self.worker_settings.pdf_dir,
                wav_dir=self.worker_settings.wav_dir,
                progress_callback=self.progress.emit,
                result_callback=self.result_ready.emit,
                finished_callback=self.finished.emit,
            )
        except Exception as exc:
            logging.error("Critical error in AnalysisWorker", exc_info=True)
            self.finished.emit(f"Critical Worker Error: {exc}")
