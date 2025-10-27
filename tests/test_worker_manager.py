from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QObject, pyqtSignal


@pytest.fixture
def mock_worker_settings(tmp_path):
    from ui.config_models import WorkerSettings

    return WorkerSettings(pdf_dir=tmp_path, wav_dir=tmp_path)


@pytest.fixture
def mock_analysis_worker(monkeypatch):
    class MockWorker(QObject):
        progress = pyqtSignal(str)
        result_ready = pyqtSignal(object)
        finished = pyqtSignal(str)

        def __init__(
            self,
            worker_settings,
            tolerance_settings,
            id_extraction_settings,
        ):
            super().__init__()
            self.worker_settings = worker_settings
            self.tolerance_settings = tolerance_settings
            self.id_extraction_settings = id_extraction_settings
            self.run = MagicMock()

    monkeypatch.setattr("ui.workers.worker_manager.AnalysisWorker", MockWorker)
    return MockWorker


def wait_for_worker(manager, qtbot, condition, timeout=1000):
    qtbot.waitUntil(lambda: manager._worker is not None, timeout=timeout)
    qtbot.waitUntil(condition, timeout=timeout)


def test_worker_manager_creation(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )
    assert not manager.is_running()
    assert manager._thread is None
    assert manager._worker is None


def test_start_analysis_starts_thread_and_worker(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
    mock_analysis_worker,
    qtbot,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    manager.start_analysis()
    wait_for_worker(manager, qtbot, lambda: manager._worker.run.called)

    assert manager._thread is not None
    assert manager._worker is not None
    assert manager._worker.run.called

    manager.cleanup()
    assert manager._thread is None
    assert manager._worker is None


def test_cleanup_stops_thread(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
    mock_analysis_worker,
    qtbot,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )
    manager.start_analysis()
    wait_for_worker(manager, qtbot, lambda: manager._worker.run.called)

    manager.cleanup()
    qtbot.waitUntil(lambda: not manager.is_running(), timeout=1000)

    assert manager._thread is None
    assert manager._worker is None


def test_signals_are_forwarded(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
    mock_analysis_worker,
    qtbot,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    progress_values = []
    result_values = []
    finished_values = []

    manager.progress.connect(lambda msg: progress_values.append(msg))
    manager.result_ready.connect(lambda payload: result_values.append(payload))
    manager.finished.connect(lambda msg: finished_values.append(msg))

    manager.start_analysis()
    wait_for_worker(manager, qtbot, lambda: manager._worker.run.called)

    manager._worker.progress.emit("In progress...")
    manager._worker.result_ready.emit({"data": 1})
    manager._worker.finished.emit("Done")

    assert progress_values == ["In progress..."]
    assert result_values == [{"data": 1}]
    assert finished_values == ["Done"]

    manager.cleanup()
