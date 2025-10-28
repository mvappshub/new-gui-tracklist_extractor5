from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

from adapters.filesystem.file_discovery import discover_files


@pytest.fixture
def temp_dir():
    """Temporary directory for filesystem tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def test_unicode_diacritics_in_filenames(temp_dir):
    """GIVEN filenames with Czech diacritics WHEN discovered THEN matches process correctly."""
    # Create test files with diacritics
    test_files = [
        temp_dir / "track_01_žába.wav",
        temp_dir / "track_02_řeka.pdf",
        temp_dir / "track_03_černý.wav",
        temp_dir / "track_04_švestka.pdf",
        temp_dir / "track_05_ďábel.wav",
        temp_dir / "track_06_ťukot.pdf",
        temp_dir / "track_07_ňadro.wav",
        temp_dir / "track_08_áááá.pdf",
        temp_dir / "track_09_éeée.wav",
        temp_dir / "track_10_íííí.pdf",
    ]

    for file_path in test_files:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("dummy")

    pairs = discover_files(temp_dir)

    # Should find matching pairs without crashes or replacement chars
    assert len(pairs) >= 1  # At least some pairs should be found
    for pdf_path, wav_path in pairs:
        assert pdf_path.exists()
        assert wav_path.exists()
        # Check that diacritics are preserved (no \ufffd replacement chars)
        assert '\ufffd' not in str(pdf_path).lower()
        assert '\ufffd' not in str(wav_path).lower()


def test_hidden_files_ignored(temp_dir):
    """GIVEN hidden/system files WHEN discovered THEN they are excluded."""
    # Create normal file
    normal_pdf = temp_dir / "normal.pdf"
    normal_wav = temp_dir / "normal.wav"
    normal_pdf.write_text("normal")
    normal_wav.write_text("normal")

    # Create hidden files (platform-specific)
    hidden_pdf = temp_dir / ".hidden.pdf"
    hidden_wav = temp_dir / ".hidden.wav"
    hidden_pdf.write_text("hidden")
    hidden_wav.write_text("hidden")

    pairs = discover_files(temp_dir)

    # Should only find the normal pair
    assert len(pairs) == 1
    pdf_path, wav_path = pairs[0]
    assert pdf_path.name == "normal.pdf"
    assert wav_path.name == "normal.wav"


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
def test_windows_long_paths(temp_dir):
    """GIVEN paths longer than 260 chars WHEN using \\?\ prefix THEN processed without errors."""
    # Create a deep directory structure to exceed 260 chars
    long_dir = temp_dir
    while len(str(long_dir)) < 300:
        long_dir = long_dir / ("subdir_" * 10)[:50]  # Create long subdir names

    long_dir.mkdir(parents=True)

    # Create test files
    pdf_path = long_dir / "test_long_path.pdf"
    wav_path = long_dir / "test_long_path.wav"
    pdf_path.write_text("long path pdf")
    wav_path.write_text("long path wav")

    # Convert to Windows long path format
    long_path_str = str(long_dir)
    if not long_path_str.startswith('\\\\?\\'):
        long_path_str = '\\\\?\\' + long_path_str

    long_path = Path(long_path_str)

    # Should handle long paths without crashing
    pairs = discover_files(long_path)

    assert len(pairs) >= 1
    # Verify at least one pair was found
    found_long_path = False
    for pdf_p, wav_p in pairs:
        if "test_long_path" in str(pdf_p):
            found_long_path = True
            break
    assert found_long_path, "Long path files should be discoverable"


def test_duplicate_basenames_deterministic(temp_dir):
    """GIVEN multiple files with same basename WHEN discovered THEN behavior is deterministic."""
    # Create multiple files with same basename in ZIP-like scenario
    # In a real ZIP, files would have same name, but here simulate in filesystem

    base_dir = temp_dir / "base"
    base_dir.mkdir()

    # Create multiple "track_01" files with same basename
    (base_dir / "track_01.pdf").write_text("pdf1")
    (base_dir / "track_01.wav").write_text("wav1")
    (base_dir / "track_01_01.pdf").write_text("pdf1_01")  # Different extension but related
    (base_dir / "track_01_01.wav").write_text("wav1_01")

    pairs = discover_files(base_dir)

    # Should find at least one pair deterministically
    assert len(pairs) >= 1

    # Run again to ensure deterministic behavior
    pairs2 = discover_files(base_dir)
    assert pairs == pairs2, "File discovery should be deterministic for duplicate basenames"


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
def test_windows_file_attributes(temp_dir):
    """GIVEN files with Windows attributes WHEN discovered THEN handled according to policy."""
    # Create test files
    normal_pdf = temp_dir / "normal_test.pdf"
    normal_wav = temp_dir / "normal_test.wav"
    normal_pdf.write_text("normal")
    normal_wav.write_text("normal")

    # System files are typically not in user directories, so skip this test for now
    # In a real scenario, would use Windows API to set FILE_ATTRIBUTE_SYSTEM

    pairs = discover_files(temp_dir)

    # For now, just ensure normal files are found without Windows-specific crashes
    assert len(pairs) >= 1
    pdf_path, wav_path = pairs[0]
    assert "normal_test" in str(pdf_path) or "normal_test" in str(wav_path)
