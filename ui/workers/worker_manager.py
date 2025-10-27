from __future__ import annotations

from enum import Enum, auto

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from core.models.settings import IdExtractionSettings, ToleranceSettings
from ui.config_models import WorkerSettings
from ui.workers.analysis_worker import AnalysisWorker


class WorkerState(Enum):
    """Lifecycle states exposed by AnalysisWorkerManager."""

    IDLE = auto()
    RUNNING = auto()
    FINISHED = auto()
    FAILED = auto()


class AnalysisWorkerManager(QObject):
    """Manages the lifecycle of AnalysisWorker, injecting required settings."""

    progress = pyqtSignal(str)
    result_ready = pyqtSignal(object)
    finished = pyqtSignal(str)
    state_changed = pyqtSignal(object)

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
        self._state = WorkerState.IDLE

    def state(self) -> WorkerState:
        """Return the current worker lifecycle state."""
        return self._state

    def _set_state(self, new_state: WorkerState) -> None:
        if self._state is new_state:
            return
        self._state = new_state
        self.state_changed.emit(new_state)

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
        self._worker.finished.connect(self._handle_finished)
        self._worker.finished.connect(self.cleanup)

        self._thread.started.connect(self._worker.run)
        self._set_state(WorkerState.RUNNING)
        self._thread.start()

    def cleanup(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait(1000)
        self._thread = None
        self._worker = None
        if self._state in {WorkerState.FINISHED, WorkerState.FAILED}:
            return
        self._set_state(WorkerState.IDLE)

    def _handle_finished(self, message: str) -> None:
        lowered = (message or "").lower()
        if "error" in lowered or "fail" in lowered:
            self._set_state(WorkerState.FAILED)
        else:
            self._set_state(WorkerState.FINISHED)
