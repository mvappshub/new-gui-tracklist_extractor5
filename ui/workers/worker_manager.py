from __future__ import annotations

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from core.models.settings import IdExtractionSettings, ToleranceSettings
from ui.config_models import WorkerSettings
from ui.workers.analysis_worker import AnalysisWorker


class AnalysisWorkerManager(QObject):
    """Manages the lifecycle of AnalysisWorker, injecting required settings."""

    progress = pyqtSignal(str)
    result_ready = pyqtSignal(object)
    finished = pyqtSignal(str)

    def __init__(
        self,
        worker_settings: WorkerSettings,
        tolerance_settings: ToleranceSettings,
        id_extraction_settings: IdExtractionSettings,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.worker_settings = worker_settings
        self.tolerance_settings = tolerance_settings
        self.id_extraction_settings = id_extraction_settings
        self._worker: AnalysisWorker | None = None
        self._thread: QThread | None = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def start_analysis(self) -> None:
        if self.is_running():
            return

        self._thread = QThread()
        self._worker = AnalysisWorker(
            worker_settings=self.worker_settings,
            tolerance_settings=self.tolerance_settings,
            id_extraction_settings=self.id_extraction_settings,
        )
        self._worker.moveToThread(self._thread)

        self._worker.progress.connect(self.progress)
        self._worker.result_ready.connect(self.result_ready)
        self._worker.finished.connect(self.finished)
        self._worker.finished.connect(self.cleanup)

        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def cleanup(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait(1000)
        self._thread = None
        self._worker = None
