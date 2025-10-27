from __future__ import annotations

import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QObject, pyqtSignal

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ExportSettings
from services.export_service import export_results_to_json


pytestmark = pytest.mark.gui


@pytest.fixture
def worker_settings(tmp_path):
    from ui.config_models import WorkerSettings

    return WorkerSettings(pdf_dir=tmp_path, wav_dir=tmp_path)


@pytest.fixture
def patched_worker(monkeypatch):
    class DummyWorker(QObject):
        progress = pyqtSignal(str)
        result_ready = pyqtSignal(object)
        finished = pyqtSignal(str)

        def __init__(self, *args, **kwargs):
            super().__init__()
            self.run = MagicMock()

    monkeypatch.setattr("ui.workers.worker_manager.AnalysisWorker", DummyWorker)
    return DummyWorker


def _make_manager(worker_settings, tolerance_settings, id_extraction_settings):
    from ui.workers.worker_manager import AnalysisWorkerManager

    return AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )


def _make_side_result(tmp_path: Path) -> SideResult:
    return SideResult(
        seq=1,
        pdf_path=tmp_path / "track.pdf",
        zip_path=tmp_path / "track.zip",
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[TrackInfo(title="Track 1", side="A", position=1, duration_sec=120)],
        wav_tracks=[WavInfo(filename="track1.wav", duration_sec=120.0, side="A", position=1)],
        total_pdf_sec=120,
        total_wav_sec=120.0,
        total_difference=0,
    )


def test_worker_manager_state_transitions(qtbot, worker_settings, tolerance_settings, id_extraction_settings, patched_worker):
    from ui.workers.worker_manager import WorkerState

    manager = _make_manager(worker_settings, tolerance_settings, id_extraction_settings)
    observed: List[WorkerState] = []
    manager.state_changed.connect(lambda state: observed.append(state))

    assert manager.state() is WorkerState.IDLE
    assert isinstance(manager.is_running(), bool)

    manager.start_analysis()
    qtbot.waitUntil(lambda: manager._worker is not None and manager._worker.run.called, timeout=1000)

    assert manager.state() is WorkerState.RUNNING
    assert observed[0] is WorkerState.RUNNING

    manager._worker.finished.emit("Completed successfully")
    qtbot.waitUntil(lambda: manager.state() is WorkerState.FINISHED, timeout=1000)

    assert observed[-1] is WorkerState.FINISHED
    assert manager.state() is WorkerState.FINISHED
    qtbot.waitUntil(lambda: not manager.is_running(), timeout=1000)


def test_worker_manager_failure_state(qtbot, worker_settings, tolerance_settings, id_extraction_settings, patched_worker):
    from ui.workers.worker_manager import WorkerState

    manager = _make_manager(worker_settings, tolerance_settings, id_extraction_settings)
    states = []
    manager.state_changed.connect(states.append)

    manager.start_analysis()
    qtbot.waitUntil(lambda: manager._worker is not None and manager._worker.run.called, timeout=1000)

    manager._worker.finished.emit("Critical worker error happened")
    qtbot.waitUntil(lambda: manager.state() is WorkerState.FAILED, timeout=1000)

    assert states[0] is WorkerState.RUNNING
    assert states[-1] is WorkerState.FAILED
    assert manager.state() is WorkerState.FAILED

    manager.cleanup()
    qtbot.waitUntil(lambda: not manager.is_running(), timeout=1000)


def test_worker_cleanup_resets_to_idle(qtbot, worker_settings, tolerance_settings, id_extraction_settings, patched_worker):
    from ui.workers.worker_manager import WorkerState

    manager = _make_manager(worker_settings, tolerance_settings, id_extraction_settings)

    manager.start_analysis()
    qtbot.waitUntil(lambda: manager._worker is not None and manager._worker.run.called, timeout=1000)
    assert manager.state() is WorkerState.RUNNING

    manager.cleanup()
    qtbot.waitUntil(lambda: manager.state() is WorkerState.IDLE, timeout=1000)


def test_export_missing_directory(tmp_path):
    export_dir = tmp_path / "nested" / "exports"
    export_settings = ExportSettings(auto_export=True, export_dir=export_dir)
    results = [_make_side_result(tmp_path)]

    exported_path = export_results_to_json(results, export_settings)

    assert exported_path is not None
    assert exported_path.exists()
    assert exported_path.parent == export_dir
    assert export_dir.exists()

    payload = json.loads(exported_path.read_text(encoding="utf-8"))
    assert payload["count"] == 1


def test_export_write_error(tmp_path, monkeypatch):
    export_dir = tmp_path / "exports"
    export_settings = ExportSettings(auto_export=True, export_dir=export_dir)
    results = [_make_side_result(tmp_path)]

    def _raise_permission(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(json, "dump", _raise_permission)

    with pytest.raises(PermissionError):
        export_results_to_json(results, export_settings)

    assert export_dir.exists()
    assert not any(export_dir.glob("*.json"))

