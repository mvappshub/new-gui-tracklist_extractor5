from __future__ import annotations

import contextlib
import math
import os
import re
import socket
import uuid
import zipfile
from pathlib import Path
from typing import Callable, Generator, Tuple

import numpy as np
import pytest
import soundfile as sf
from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtWidgets import QApplication

import config as config_module
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.settings import IdExtractionSettings, ToleranceSettings


@pytest.fixture(scope="session", autouse=True)
def disable_network_access() -> Generator[None, None, None]:
    """Block outbound network usage during tests."""

    from pytest import MonkeyPatch

    monkeypatch = MonkeyPatch()

    def _blocked(*args, **kwargs):
        raise RuntimeError("Network access is disabled during tests")

    for attr in ("socket", "create_connection", "getaddrinfo"):
        if hasattr(socket, attr):
            monkeypatch.setattr(socket, attr, _blocked)

    try:
        yield
    finally:
        monkeypatch.undo()


@pytest.fixture(scope="session", autouse=True)
def unset_ai_api_keys() -> Generator[None, None, None]:
    """Ensure AI API keys are cleared so tests cannot hit external services."""

    from pytest import MonkeyPatch

    monkeypatch = MonkeyPatch()
    for key in ("OPENAI_API_KEY", "OPENROUTER_API_KEY"):
        if key in os.environ:
            monkeypatch.delenv(key, raising=False)
    try:
        yield
    finally:
        monkeypatch.undo()


@pytest.fixture(scope="session")
def isolated_qsettings(tmp_path_factory) -> Generator[Callable[[str | None], Path], None, None]:
    """Provide session-level helper to sandbox QSettings into temp files."""

    original_format = QSettings.defaultFormat()

    def _current_dir(scope: QSettings.Scope) -> Path:
        settings = QSettings(QSettings.Format.IniFormat, scope, config_module.DEFAULT_SETTINGS_ORG, config_module.DEFAULT_SETTINGS_APP)
        return Path(settings.fileName()).parent

    original_user_dir = _current_dir(QSettings.Scope.UserScope)
    original_system_dir = _current_dir(QSettings.Scope.SystemScope)

    def _sanitize(token: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", token)
        return cleaned[:64] if cleaned else uuid.uuid4().hex

    def _activate(token: str | None = None) -> Path:
        key = token or uuid.uuid4().hex
        safe_key = _sanitize(key)
        settings_dir = Path(tmp_path_factory.mktemp(f"qsettings-{safe_key}"))
        QSettings.setDefaultFormat(QSettings.Format.IniFormat)
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings_dir))
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, str(settings_dir))
        return settings_dir

    try:
        yield _activate
    finally:
        QSettings.setDefaultFormat(original_format)
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(original_user_dir))
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, str(original_system_dir))


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
def isolated_config(monkeypatch, isolated_qsettings, request) -> Generator[config_module.AppConfig, None, None]:
    """Provide an isolated configuration with temporary QSettings storage."""
    original_cfg = config_module.cfg
    settings_dir = isolated_qsettings(f"{request.node.nodeid}-config")
    test_cfg = config_module.AppConfig()
    test_cfg.reset_to_defaults()
    test_cfg.file = settings_dir / "settings.json"
    monkeypatch.setattr(config_module, "cfg", test_cfg)
    if hasattr(request.module, "cfg"):
        monkeypatch.setattr(request.module, "cfg", test_cfg, raising=False)

    yield test_cfg

    config_module.cfg = original_cfg
    with contextlib.suppress(AttributeError):
        test_cfg.settings.value.clear()
        test_cfg.settings.value.sync()


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


@pytest.fixture
def snapshot_json(request, tmp_path: Path) -> Callable[[dict, str], None]:
    """Provide lightweight snapshot comparison for JSON data."""

    def _compare(data: dict, snapshot_name: str) -> None:
        snapshot_path = Path(__file__).parent / "snapshots" / f"{snapshot_name}.json"
        if not snapshot_path.exists():
            # Create initial snapshot
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with snapshot_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            pytest.fail(f"Snapshot created: {snapshot_path}. Review and re-run tests.")

        # Load and compare
        import json
        with snapshot_path.open("r", encoding="utf-8") as f:
            expected = json.load(f)

        if data != expected:
            diff_lines = []
            import difflib
            expected_str = json.dumps(expected, indent=2, sort_keys=True)
            actual_str = json.dumps(data, indent=2, sort_keys=True)
            for line in difflib.unified_diff(
                expected_str.splitlines(),
                actual_str.splitlines(),
                fromfile="expected",
                tofile="actual",
                lineterm=""
            ):
                diff_lines.append(line)

            diff_display = "\n".join(diff_lines[:20])
            if len(diff_lines) > 20:
                diff_display += "\n... (truncated)"
            pytest.fail(f"Snapshot mismatch for '{snapshot_name}':\n{diff_display}")

    return _compare
