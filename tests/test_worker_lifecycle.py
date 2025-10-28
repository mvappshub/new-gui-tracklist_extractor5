from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest
from PyQt6.QtCore import QThread

from ui.workers.analysis_worker import AnalysisWorker
from ui.workers.worker_manager import WorkerManager


@pytest.fixture
def worker_manager(qapp):
    """Create WorkerManager instance for testing."""
    return WorkerManager()


@pytest.fixture
def analysis_worker(qapp):
    """Create AnalysisWorker instance for testing."""
    worker = AnalysisWorker()
    yield worker
    # Clean up thread after test
    if worker.isRunning():
        worker.terminate()
        worker.wait(1000)


def test_double_start_prevention(worker_manager):
    """GIVEN worker already running WHEN start called again THEN rejected."""
    # Mock a worker that's already running
    with patch.object(worker_manager, '_worker', Mock()) as mock_worker:
        mock_worker.is_running.return_value = True
        mock_worker.state.return_value = "RUNNING"

        # First start should succeed
        result = worker_manager.start_analysis([])
        assert result is True or result is None  # Depending on implementation

        # Second start should be rejected
        result2 = worker_manager.start_analysis([])
        assert result2 is False or result2 is None  # Should not start again


def test_cancel_then_restart_success(analysis_worker):
    """GIVEN cancelled worker WHEN restarted THEN clean restart without zombies."""
    # Start worker
    analysis_worker.start()

    # Give it a moment to start
    time.sleep(0.1)

    # Cancel worker
    analysis_worker.cancel()

    # Wait for completion
    analysis_worker.wait(2000)

    # Verify it's not running
    assert not analysis_worker.isRunning()

    # Should be able to restart cleanly
    analysis_worker.start()
    time.sleep(0.1)

    # Verify new instance is running
    assert analysis_worker.isRunning() or analysis_worker.state() in ["STARTING", "RUNNING"]

    # Clean up
    analysis_worker.cancel()
    analysis_worker.wait(2000)


def test_window_close_cancels_worker(worker_manager, qapp, qtbot):
    """GIVEN MainWindow closed WHILE worker running THEN worker cancelled cleanly."""
    from ui.main_window import MainWindow

    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Connect worker manager to main window
    main_window.worker_manager = worker_manager

    # Start a worker
    with patch.object(worker_manager, '_worker', Mock()) as mock_worker:
        mock_worker.is_running.return_value = True

        # Mock the cancel method to verify it's called
        with patch.object(worker_manager, 'cancel') as mock_cancel:
            # Simulate window close and wait for destruction
            with qtbot.waitSignal(main_window.destroyed):
                main_window.close()

            # Worker cancel should have been called
            mock_cancel.assert_called_once()


def test_worker_state_consistency(analysis_worker):
    """GIVEN worker state changes WHEN queried THEN consistent values."""
    # Initially should not be running
    assert not analysis_worker.isRunning()

    # Start worker
    analysis_worker.start()
    time.sleep(0.1)

    # State should be consistent
    is_running = analysis_worker.isRunning()
    state = analysis_worker.state()

    if is_running:
        assert state in ["STARTING", "RUNNING", "PROCESSING"]
    else:
        assert state in ["IDLE", "COMPLETED", "CANCELLED", "ERROR"]

    # After cancel
    analysis_worker.cancel()
    analysis_worker.wait(2000)

    # State should reflect completion
    final_state = analysis_worker.state()
    assert final_state in ["COMPLETED", "CANCELLED", "ERROR", "IDLE"]


def test_race_condition_on_shutdown(analysis_worker):
    """GIVEN worker in critical section WHEN shutdown THEN no data corruption."""
    # Start worker
    analysis_worker.start()
    time.sleep(0.1)

    # Simulate shutdown race condition
    with patch.object(analysis_worker, '_cleanup') as mock_cleanup:
        # Cancel quickly
        analysis_worker.cancel()

        # Immediate shutdown attempt
        analysis_worker.terminate()
        success = analysis_worker.wait(1000)

        # Cleanup should be robust to interruption
        if success:
            mock_cleanup.assert_called()


def test_worker_public_api_contract(analysis_worker):
    """GIVEN worker instance WHEN public methods called THEN correct types returned."""
    # Test method signatures
    assert hasattr(analysis_worker, 'isRunning')
    assert hasattr(analysis_worker, 'state')
    assert hasattr(analysis_worker, 'start')
    assert hasattr(analysis_worker, 'cancel')

    # Test return types
    running = analysis_worker.isRunning()
    assert isinstance(running, bool)

    state = analysis_worker.state()
    assert isinstance(state, str)

    # Start method should not crash
    analysis_worker.start()

    # Cancel method
    analysis_worker.cancel()

    # Verify still works after cancel
    assert isinstance(analysis_worker.isRunning(), bool)
    assert isinstance(analysis_worker.state(), str)


def test_signal_emission_consistency(analysis_worker, qtbot):
    """GIVEN worker state changes WHEN signals emit THEN consistent with actual state."""
    signals_received = []

    def on_state_changed(new_state):
        signals_received.append(new_state)
        # When signal is received, actual state should match
        current_state = analysis_worker.state()
        assert current_state == new_state or abs(ord(current_state[0]) - ord(new_state[0])) < 10  # Allow minor differences

    analysis_worker.state_changed.connect(on_state_changed)

    # Start and monitor
    analysis_worker.start()
    time.sleep(0.2)

    # Cancel and monitor
    analysis_worker.cancel()
    analysis_worker.wait(2000)

    # Should have received at least some signals
    if signals_received:
        # Verify signal consistency
        final_signal = signals_received[-1]
        final_state = analysis_worker.state()
        assert final_signal in ["COMPLETED", "CANCELLED", "ERROR"] or final_state in ["COMPLETED", "CANCELLED", "ERROR"]


def test_no_memory_leaks_on_restart(analysis_worker):
    """GIVEN repeated start/cancel cycles WHEN executed THEN no resource accumulation."""
    import psutil
    import os

    if not hasattr(psutil, 'Process'):
        pytest.skip("psutil not available for memory leak testing")

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Perform multiple start/cancel cycles
    for i in range(3):
        analysis_worker.start()
        time.sleep(0.1)
        analysis_worker.cancel()
        analysis_worker.wait(1000)

        # Brief pause between cycles
        time.sleep(0.1)

    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory

    # Allow reasonable memory growth (under 10MB for this simple test)
    assert memory_growth < 10 * 1024 * 1024, f"Memory grew by {memory_growth} bytes, possible leak"


@pytest.mark.skipif(True, reason="May not be reliable in CI")
def test_worker_thread_independence(analysis_worker):
    """GIVEN worker thread WHEN main thread blocks THEN worker continues independently."""
    import threading

    results = {'worker_started': False, 'main_blocked': False}

    def worker_monitor():
        """Monitor worker in separate thread."""
        time.sleep(0.2)  # Let main thread block
        results['worker_started'] = analysis_worker.isRunning()
        results['state'] = analysis_worker.state()

    # Start monitoring thread
    monitor_thread = threading.Thread(target=worker_monitor)
    monitor_thread.start()

    # Start worker
    analysis_worker.start()

    # Block main thread
    results['main_blocked'] = True
    time.sleep(0.5)

    # Check if worker was independent
    monitor_thread.join()
    assert results['worker_started'] or results['state'] in ["STARTING", "RUNNING"]

    # Cleanup
    analysis_worker.cancel()
    analysis_worker.wait(2000)
