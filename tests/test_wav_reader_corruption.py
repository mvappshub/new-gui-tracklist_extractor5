from __future__ import annotations

import io
import struct
from pathlib import Path
from unittest.mock import patch

import pytest

from adapters.audio.wav_reader import WavReader


@pytest.fixture
def wav_reader():
    """Create WavReader instance for testing."""
    return WavReader()


def test_invalid_riff_header_handling(wav_reader, tmp_path, caplog):
    """GIVEN WAV with invalid RIFF header WHEN reading THEN skips with WARN."""
    # Create file with invalid RIFF header
    bad_riff_file = tmp_path / "bad_riff.wav"

    # Write invalid RIFF data
    with open(bad_riff_file, 'wb') as f:
        f.write(b'RIFF')  # Valid RIFF
        f.write(struct.pack('<I', 100))  # File size
        f.write(b'NOTWAVE')  # Invalid WAVE marker
        f.write(b'dummy_data' * 10)

    # Contract: skip with WARN
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(bad_riff_file)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'invalid' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


def test_corrupted_wav_data_chunk(wav_reader, tmp_path, caplog):
    """GIVEN WAV with corrupted data chunk WHEN reading THEN skips with WARN."""
    corrupted_file = tmp_path / "corrupted_data.wav"

    # Create minimal valid WAV header but corrupt data
    with open(corrupted_file, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36))  # Total size
        f.write(b'WAVE')

        # Format chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # Format chunk size
        f.write(struct.pack('<HHIIHH', 1, 1, 44100, 44100, 1, 8))  # PCM, mono, etc.

        # Data chunk with corrupted size
        f.write(b'data')
        f.write(struct.pack('<I', 1000))  # Claim 1000 bytes
        f.write(b'x' * 10)  # But only write 10 bytes

    # Contract: skip with WARN
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(corrupted_file)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'truncated' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


def test_truncated_wav_file(wav_reader, tmp_path, caplog):
    """GIVEN truncated WAV file WHEN reading THEN skips with WARN."""
    truncated_file = tmp_path / "truncated.wav"

    # Write incomplete WAV header
    with open(truncated_file, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 1000))  # Large claimed size
        f.write(b'WAVE')
        # Stop abruptly - no format chunk

    # Contract: skip with WARN
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(truncated_file)

    assert result is None
    assert any('truncated' in record.message.lower() or 'corrupt' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


def test_corrupted_zip_with_wav(wav_reader, tmp_path, caplog):
    """GIVEN corrupted ZIP containing WAV WHEN reading THEN skips with WARN."""
    corrupted_zip = tmp_path / "corrupted.zip"

    # Create file that looks like ZIP but is corrupted
    with open(corrupted_zip, 'wb') as f:
        f.write(b'PK\x03\x04')  # ZIP header
        f.write(b'\x00' * 20)   # Corrupted ZIP data
        f.write(b'RIFF')        # Embedded RIFF data
        f.write(b'\x00' * 10)   # Truncated

    # Contract: skip with WARN for ZIP corruption
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(corrupted_zip)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'invalid' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


def test_gibberish_file_as_wav(wav_reader, tmp_path, caplog):
    """GIVEN complete gibberish file WHEN treated as WAV THEN skips with WARN."""
    gibberish_file = tmp_path / "gibberish.wav"

    # Write random bytes
    with open(gibberish_file, 'wb') as f:
        f.write(b'A' * 44)  # Size of typical WAV header
        f.write(b'random_gibberish_data' * 100)

    # Contract: skip with WARN
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(gibberish_file)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'invalid' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


@pytest.mark.xfail(reason="Big-endian WAV files are an edge case not currently handled")
def test_wav_with_wrong_endianness(wav_reader, tmp_path, caplog):
    """GIVEN WAV with big-endian data WHEN reading THEN handles correctly or gracefully."""
    endian_file = tmp_path / "big_endian.wav"

    # Create WAV with mixed endianness (shouldn't happen but might in corrupted files)
    with open(endian_file, 'wb') as f:
        # RIFF header (little endian)
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36))  # Little endian size
        f.write(b'WAVE')

        # Format chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('>HHIIHH', 1, 1, 44100, 44100, 1, 8))  # Big endian format data

    # For now, xfail this edge case
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(endian_file)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'invalid' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


def test_extremely_large_wav_header(wav_reader, tmp_path, caplog):
    """GIVEN WAV claiming impossibly large size WHEN reading THEN skips with WARN."""
    huge_file = tmp_path / "huge_header.wav"

    # Create WAV header claiming enormous size
    with open(huge_file, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 2**31 - 1))  # Maximum 32-bit value
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<HHIIHH', 1, 1, 44100, 44100, 1, 8))

        # Data chunk claiming massive size
        f.write(b'data')
        f.write(struct.pack('<I', 2**30))  # 1GB claimed
        f.write(b'x' * 100)  # But only small actual data

    # Contract: skip with WARN (fail safely without memory issues)
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(huge_file)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'invalid' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')


def test_nested_corruption_patterns(wav_reader, tmp_path, caplog):
    """GIVEN WAV with multiple corruption types WHEN reading THEN skips with WARN."""
    nested_corrupt_file = tmp_path / "nested_corrupt.wav"

    with open(nested_corrupt_file, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 100))
        f.write(b'WAVE')
        # Valid format chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<HHIIHH', 1, 1, 44100, 44100, 1, 8))
        # Data chunk with wrong size and truncated data
        f.write(b'data')
        f.write(struct.pack('<I', 1000))  # Claims 1000 bytes
        f.write(b'short_data')  # Only 10 bytes

    # Contract: skip with WARN for first corruption encountered
    with caplog.at_level('WARNING'):
        result = wav_reader.read_duration(nested_corrupt_file)

    assert result is None
    assert any('corrupt' in record.message.lower() or 'truncated' in record.message.lower()
               for record in caplog.records if record.levelname == 'WARNING')
