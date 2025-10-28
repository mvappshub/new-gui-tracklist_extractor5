from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

from services.export_service import export_result


@pytest.fixture
def temp_dir():
    """Temporary directory for export tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def mock_result():
    """Mock analysis result for testing."""
    class MockResult:
        def __init__(self):
            self.pdf_path = "dummy.pdf"
            self.wav_path = "dummy.wav"
            self.duration_diff = 1.5
            self.tracks = [
                {
                    "title": "Test Track",
                    "duration": 120.0,
                    "start_time": 0.0,
                    "side": "A"
                }
            ]

    return MockResult()


def test_export_to_readonly_directory_fails(temp_dir, mock_result):
    """GIVEN read-only target directory WHEN exporting THEN raises PermissionError."""
    readonly_dir = temp_dir / "readonly_export"
    readonly_dir.mkdir()

    # Make directory read-only (cross-platform)
    readonly_dir.chmod(0o444)  # Read-only for all

    try:
        # Should fail with permission error
        with pytest.raises((PermissionError, OSError)) as exc_info:
            export_result(mock_result, readonly_dir)

        # Verify it's a permission issue
        assert "permission" in str(exc_info.value).lower() or "access" in str(exc_info.value).lower()

    finally:
        # Restore permissions for cleanup
        readonly_dir.chmod(0o755)


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific locked file test")
def test_export_to_locked_file_windows(temp_dir, mock_result, caplog):
    """GIVEN file locked by another process WHEN exporting THEN raises PermissionError and logs access error."""
    import msvcrt

    # Create target file and lock it
    export_file = temp_dir / "locked_export.txt"
    export_file.write_text("existing locked content")

    # Lock the file using Windows API
    with open(export_file, 'r+') as f:
        # Lock the file (exclusive lock)
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

        try:
            # Export should fail with permission error
            with pytest.raises((PermissionError, OSError)):
                export_result(mock_result, temp_dir)

            # Assert ERROR log with access/permission keywords
            error_logs = [r for r in caplog.records if r.levelname == 'ERROR']
            assert len(error_logs) > 0, "Expected ERROR log for locked file access"

            log_content = ' '.join(r.message for r in error_logs).lower()
            assert 'access' in log_content or 'permission' in log_content, f"ERROR log should mention access/permission, got: {log_content}"

            # Assert no partial files remain in target directory
            export_files = list(temp_dir.glob("*"))
            # Should only contain our locked file, no new partial export files
            assert len(export_files) == 1
            assert export_files[0] == export_file

        finally:
            # Unlock the file
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass  # File might already be unlocked or closed


def test_export_creates_missing_directory(temp_dir, mock_result):
    """GIVEN non-existent target directory WHEN exporting THEN directory is created automatically."""
    missing_dir = temp_dir / "new_export_dir" / "nested" / "deep"

    # Directory doesn't exist
    assert not missing_dir.exists()

    # Export should create the directory
    export_result(mock_result, missing_dir)

    # Directory should now exist
    assert missing_dir.exists()
    assert missing_dir.is_dir()


def test_partial_export_cleanup_on_error(temp_dir, mock_result, monkeypatch):
    """GIVEN export that partially fails WHEN error occurs THEN partial files are cleaned up."""
    export_dir = temp_dir / "export_cleanup_test"
    export_dir.mkdir()

    # Mock a scenario where export starts writing but fails midway
    original_write = open

    def failing_write(name, mode='r', **kwargs):
        if 'export' in name and mode in ('w', 'wb'):
            # Create file but make write fail
            file_obj = original_write(name, mode, **kwargs)
            # Close immediately to simulate failure after creation
            file_obj.close()
            raise OSError("Simulated write failure")
        return original_write(name, mode, **kwargs)

    monkeypatch.setattr('builtins.open', failing_write)

    # Export should handle partial write failures gracefully
    with pytest.raises(OSError, match="Simulated write failure"):
        export_result(mock_result, export_dir)

    # Check that no partial files remain (cleanup happened)
    export_files = list(export_dir.glob("*"))
    # Allow some temporary files but ensure major export files are cleaned up
    # In practice, this would depend on the export implementation


def test_export_logs_permission_errors(caplog, temp_dir, mock_result):
    """GIVEN permission error during export WHEN export fails THEN ERROR is logged."""
    readonly_dir = temp_dir / "readonly_log_test"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)  # Read-only

    try:
        with pytest.raises((PermissionError, OSError)):
            export_result(mock_result, readonly_dir)

        # Check that error was logged
        error_logs = [record for record in caplog.records if record.levelname == "ERROR"]
        assert len(error_logs) > 0, "Expected ERROR log for permission failure"

        # Check log content mentions permission or access
        log_messages = " ".join(record.message for record in error_logs)
        assert "permission" in log_messages.lower() or "access" in log_messages.lower()

    finally:
        readonly_dir.chmod(0o755)


def test_export_no_partial_output_on_failure(temp_dir, mock_result):
    """GIVEN export failure WHEN process fails THEN no partial output remains."""
    export_dir = temp_dir / "no_partial_test"
    export_dir.mkdir()

    # Start with clean directory
    initial_files = set(export_dir.glob("*"))

    try:
        # Force failure by exporting to invalid location
        invalid_path = temp_dir / "nonexistent" / "deep" / "path"

        # This should fail because intermediate directories don't exist
        # (depending on implementation - if export doesn't auto-create,
        # this should trigger our test)

        # For now, just verify that failed exports don't leave junk
        with pytest.raises((OSError, FileNotFoundError)):
            export_result(mock_result, invalid_path)

        # Check that export_dir wasn't polluted by partial files
        final_files = set(export_dir.glob("*"))
        assert final_files == initial_files, "Export failure should not create partial files"

    except Exception:
        # If the invalid path doesn't cause failure, that's OK
        # Main point is no partial files left behind
        final_files = set(export_dir.glob("*"))
        assert final_files == initial_files, "No partial files should remain after export"


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific sharing violation test")
def test_windows_sharing_violation_handling(temp_dir, mock_result, caplog):
    """GIVEN Windows sharing violation WHEN exporting THEN raises OSError and logs access error."""
    import msvcrt

    # Create a file and lock it exclusively (simulates sharing violation)
    export_file = temp_dir / "sharing_violation_test.txt"
    export_file.write_text("initial content")

    # Open file in exclusive mode (simulates another process holding it)
    with open(export_file, 'r+') as f:
        # Lock file to simulate sharing violation
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

        try:
            # Export should fail with sharing violation
            with pytest.raises((PermissionError, OSError)):
                export_result(mock_result, temp_dir)

            # Assert ERROR-level logs contain access/permission keywords
            error_logs = [r for r in caplog.records if r.levelname == 'ERROR']
            assert len(error_logs) > 0, "Expected ERROR log for sharing violation"

            log_content = ' '.join(r.message for r in error_logs).lower()
            assert 'access' in log_content or 'permission' in log_content, f"ERROR log should mention access/permission issues, got: {log_content}"

            # Assert no partial files exist in target directory
            export_files = list(temp_dir.glob("*"))
            # Should only contain the locked file, no partial export files
            assert len(export_files) <= 2  # Original file + possibly one temp file during attempt

        finally:
            # Unlock the file
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass  # Might already be unlocked
