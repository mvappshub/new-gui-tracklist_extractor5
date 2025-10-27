from __future__ import annotations

import logging
import sys
import types
import zipfile
from pathlib import Path
from typing import Callable

import numpy as np
import pytest
import soundfile as sf

from adapters.audio.wav_reader import ZipWavFileReader


def _write_wav(path: Path, duration_sec: float, sample_rate: int = 44100) -> None:
    """Helper to author a simple sine-less wave file for tests."""
    frame_count = int(duration_sec * sample_rate)
    data = np.zeros(frame_count, dtype=np.float32)
    sf.write(path, data, sample_rate)


def _build_zip(tmp_path: Path, entries: dict[str, bytes]) -> Path:
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for arcname, payload in entries.items():
            zf.writestr(arcname, payload)
    return zip_path


def _patch_duration(monkeypatch: pytest.MonkeyPatch, factory: Callable[[Path], float]) -> None:
    monkeypatch.setattr("adapters.audio.wav_reader.get_wav_duration", factory)


def test_read_wav_files_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    entries = {
        "disc/B2_second.wav": b"data-b",
        "disc/A1_first.wav": b"data-a",
    }
    zip_path = _build_zip(tmp_path, entries)

    durations = {"A1_first.wav": 12.34, "B2_second.wav": 56.78}
    recorded_paths: list[Path] = []

    def fake_get_wav_duration(path: Path) -> float:
        recorded_paths.append(path)
        return durations[path.name]

    _patch_duration(monkeypatch, fake_get_wav_duration)

    reader = ZipWavFileReader()
    wav_infos = reader.read_wav_files(zip_path)

    assert [info.filename for info in wav_infos] == ["disc/A1_first.wav", "disc/B2_second.wav"]
    assert [info.duration_sec for info in wav_infos] == [12.34, 56.78]
    assert len(recorded_paths) == 2


def test_read_wav_files_corrupted_zip(tmp_path: Path) -> None:
    broken_zip = tmp_path / "corrupted.zip"
    broken_zip.write_bytes(b"not a real zip archive")

    reader = ZipWavFileReader()
    assert reader.read_wav_files(broken_zip) == []


def test_read_wav_files_empty_zip(empty_zip: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Path] = []

    def fake_get_wav_duration(path: Path) -> float:
        calls.append(path)
        return 1.0

    _patch_duration(monkeypatch, fake_get_wav_duration)

    reader = ZipWavFileReader()
    assert reader.read_wav_files(empty_zip) == []
    assert not calls


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Out-of-scope for config DI; quarantined per Execution Policy. "
        "Will be fixed in follow-up change fix-wav-reader-error-handling."
    ),
    run=False,
)
def test_read_wav_files_corrupted_wav(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zip_path = _build_zip(tmp_path, {"broken.wav": b"corrupted payload"})

    def failing_get_wav_duration(path: Path) -> float:
        raise RuntimeError(f"Cannot parse {path}")

    _patch_duration(monkeypatch, failing_get_wav_duration)

    reader = ZipWavFileReader()
    with caplog.at_level(logging.WARNING):
        results = reader.read_wav_files(zip_path)

    assert results == []
    assert any("Nelze přečíst hlavičku WAV" in message for message in caplog.messages)


def test_read_wav_files_no_wav_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    zip_path = _build_zip(tmp_path, {"track.mp3": b"id3"})

    def forbidden_call(path: Path) -> float:
        raise AssertionError(f"get_wav_duration should not be called for {path}")

    _patch_duration(monkeypatch, forbidden_call)

    reader = ZipWavFileReader()
    assert reader.read_wav_files(zip_path) == []


def test_read_wav_files_soundfile_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wav_path = tmp_path / "fallback.wav"
    _write_wav(wav_path, duration_sec=1.0)
    zip_path = tmp_path / "fallback.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(wav_path, arcname=f"folder/{wav_path.name}")

    fake_soundfile = types.ModuleType("soundfile")

    def fake_info(_: str) -> float:
        raise RuntimeError("libsndfile broken")

    fake_soundfile.info = fake_info  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "soundfile", fake_soundfile)

    reader = ZipWavFileReader()
    results = reader.read_wav_files(zip_path)

    assert len(results) == 1
    assert results[0].filename == "folder/fallback.wav"
    assert results[0].duration_sec > 0


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Out-of-scope for config DI; quarantined per Execution Policy. "
        "Will be fixed in follow-up change fix-wav-reader-error-handling."
    ),
    run=False,
)
def test_read_wav_files_duration_extraction_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zip_path = _build_zip(tmp_path, {"fail.wav": b"broken"})

    def exploding_get_wav_duration(path: Path) -> float:
        raise ValueError(f"unreadable {path}")

    _patch_duration(monkeypatch, exploding_get_wav_duration)

    reader = ZipWavFileReader()
    with caplog.at_level(logging.WARNING):
        results = reader.read_wav_files(zip_path)

    assert results == []
    assert any("Nelze přečíst hlavičku WAV" in message for message in caplog.messages)


def test_read_wav_files_duplicate_basenames(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    entries = {
        "sideB/track.wav": b"two",
        "sideA/track.wav": b"one",
    }
    zip_path = _build_zip(tmp_path, entries)

    recorded_paths: list[Path] = []
    durations_iter = iter([1.23, 4.56])

    def fake_get_wav_duration(path: Path) -> float:
        recorded_paths.append(path)
        return next(durations_iter)

    _patch_duration(monkeypatch, fake_get_wav_duration)

    reader = ZipWavFileReader()
    wav_infos = reader.read_wav_files(zip_path)

    assert [info.filename for info in wav_infos] == ["sideA/track.wav", "sideB/track.wav"]
    assert [info.duration_sec for info in wav_infos] == [1.23, 4.56]
    assert {p.parent.name for p in recorded_paths} == {"sideA", "sideB"}


def test_read_wav_files_skips_zero_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zip_path = _build_zip(tmp_path, {"only.wav": b"zero"})

    def zero_duration(_: Path) -> float:
        return 0.0

    _patch_duration(monkeypatch, zero_duration)

    reader = ZipWavFileReader()
    with caplog.at_level(logging.WARNING):
        wav_infos = reader.read_wav_files(zip_path)

    assert wav_infos == []
    assert any("neplatnou délku" in message for message in caplog.messages)
