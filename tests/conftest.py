from __future__ import annotations

import contextlib
import math
import zipfile
from pathlib import Path
from typing import Generator, Tuple

import numpy as np
import pytest
import soundfile as sf
from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtWidgets import QApplication

import config as config_module
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.settings import IdExtractionSettings, ToleranceSettings

@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """Provide a QApplication instance for Qt tests."""
    app = QApplication.instance()
    created = False
    if app is None:
        app = QApplication([])
        created = True

    yield app

    if created:
        with contextlib.suppress(Exception):
            # Allow pending events to process before quitting.
            QTimer.singleShot(0, app.quit)
            app.processEvents()
            app.quit()


@pytest.fixture
def isolated_config(monkeypatch, tmp_path) -> Generator[config_module.AppConfig, None, None]:
    """Provide an isolated configuration with temporary QSettings storage."""
    original_cfg = config_module.cfg
    org_name = original_cfg.settings.organizationName()
    app_name = original_cfg.settings.applicationName()

    user_settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, org_name, app_name)
    system_settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, org_name, app_name)
    original_user_dir = Path(user_settings.fileName()).parent
    original_system_dir = Path(system_settings.fileName()).parent

    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings_dir))
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, str(settings_dir))

    test_cfg = config_module.AppConfig()
    test_cfg.reset_to_defaults()
    monkeypatch.setattr(config_module, "cfg", test_cfg)

    yield test_cfg

    config_module.cfg = original_cfg
    QSettings.setDefaultFormat(original_format)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(original_user_dir))
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, str(original_system_dir))


def _generate_sine_wave(duration: float, sample_rate: int) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False, dtype=np.float32)
    angles = 2 * math.pi * 440 * t
    waveform = 0.5 * np.sin(angles)
    return waveform.astype(np.float32)


@pytest.fixture
def mock_wav_zip(tmp_path) -> Generator[Tuple[Path, str], None, None]:
    """Create a temporary ZIP containing a valid WAV file."""
    wav_filename = "test_track.wav"
    wav_path = tmp_path / wav_filename
    sample_rate = 44100
    data = _generate_sine_wave(2.0, sample_rate)
    sf.write(wav_path, data, sample_rate)

    zip_path = tmp_path / "test_archive.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(wav_path, arcname=f"tracks/{wav_filename}")

    yield zip_path, wav_filename


@pytest.fixture
def empty_zip(tmp_path) -> Generator[Path, None, None]:
    """Create an empty ZIP archive."""
    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(zip_path, "w"):
        pass
    yield zip_path


@pytest.fixture
def invalid_wav_zip(tmp_path) -> Generator[Tuple[Path, str], None, None]:
    """Create a ZIP containing an invalid WAV payload."""
    wav_filename = "broken_track.wav"
    zip_path = tmp_path / "invalid.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(wav_filename, b"not-a-valid-wav")
    yield zip_path, wav_filename


@pytest.fixture
def tolerance_settings() -> ToleranceSettings:
    """Provide default tolerance settings for tests."""
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.fixture
def id_extraction_settings() -> IdExtractionSettings:
    """Provide default numeric ID extraction settings for tests."""
    return IdExtractionSettings(min_digits=1, max_digits=6, ignore_numbers=[])


@pytest.fixture
def audio_mode_detector() -> FakeAudioModeDetector:
    """Provide fake audio mode detector for tests (no external API calls)."""
    return FakeAudioModeDetector()


@pytest.fixture
def settings_filename(tmp_path: Path) -> Path:
    """Provide temporary settings filename for DI tests."""
    return tmp_path / "test_settings.json"
