from __future__ import annotations

import ast
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog

from config import AVAILABLE_LLM_MODELS, DEFAULTS, AppConfig
from ui.dialogs.settings_dialog import SettingsDialog


SNAPSHOT_KEYS = [
    "llm/base_url",
    "llm/model",
    "export/auto",
    "export/default_dir",
    "analysis/tolerance_warn",
    "analysis/tolerance_fail",
    "input/pdf_dir",
    "input/wav_dir",
    "ui/dpi_scale",
]


def _make_dialog(qtbot, cfg: AppConfig) -> SettingsDialog:
    dialog = SettingsDialog(cfg.file, cfg)
    qtbot.addWidget(dialog)
    dialog.show()
    return dialog


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_open_dialog_shows_defaults(qapp, qtbot, isolated_config: AppConfig) -> None:
    """GIVEN a fresh config WHEN the dialog opens THEN defaults match config constants."""
    dialog = _make_dialog(qtbot, isolated_config)

    values = dialog.get_values()
    expected_defaults = {key: DEFAULTS[key] for key in SNAPSHOT_KEYS}

    actual_subset = {key: values[key] for key in SNAPSHOT_KEYS}
    assert actual_subset == expected_defaults


@pytest.mark.usefixtures("isolated_config")
def test_config_schema_snapshot(qapp, qtbot, isolated_config: AppConfig, snapshot_json) -> None:
    """GIVEN the dialog WHEN schema exported THEN dict matches approved snapshot."""
    dialog = _make_dialog(qtbot, isolated_config)

    payload = {key: dialog.get_values()[key] for key in SNAPSHOT_KEYS}
    snapshot_json(payload, "settings_schema")


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_save_and_reopen_preserves_values(qapp, qtbot, isolated_config: AppConfig, tmp_path) -> None:
    """GIVEN edited values WHEN saved THEN reopening shows exact persisted values."""
    dialog = _make_dialog(qtbot, isolated_config)

    # When - update model selection and directory paths
    target_model = next(model for model in AVAILABLE_LLM_MODELS if model != DEFAULTS["llm/model"])
    dialog.settings_page.model_group.model_combo.setCurrentText(target_model)

    pdf_dir = tmp_path / "inputs" / "pdf"
    wav_dir = tmp_path / "inputs" / "wav"
    export_dir = tmp_path / "exports"
    dialog.settings_page.paths_group.pdf_card.set_path(str(pdf_dir), update_config=True)
    dialog.settings_page.paths_group.wav_card.set_path(str(wav_dir), update_config=True)
    dialog.settings_page.paths_group.export_card.set_path(str(export_dir), update_config=True)

    dialog.settings_page.analysis_group.warn_slider.setValue(6)
    dialog.settings_page.analysis_group.fail_slider.setValue(12)

    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)

    saved_values = dialog.get_values()
    assert saved_values["llm/model"] == target_model
    assert saved_values["analysis/tolerance_warn"] == 6
    assert saved_values["analysis/tolerance_fail"] == 12
    assert saved_values["input/pdf_dir"] == str(pdf_dir)
    assert saved_values["input/wav_dir"] == str(wav_dir)
    assert saved_values["export/default_dir"] == str(export_dir)

    reopened = _make_dialog(qtbot, isolated_config)
    reopened_values = reopened.get_values()
    for key in SNAPSHOT_KEYS:
        assert reopened_values[key] == saved_values[key]


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_invalid_input_blocks_save(qapp, qtbot, isolated_config: AppConfig) -> None:
    """GIVEN invalid paths WHEN save attempted THEN dialog should reject (documented behaviour)."""
    dialog = _make_dialog(qtbot, isolated_config)

    # Make input invalid via UI
    dialog.settings_page.paths_group.pdf_card.set_path("", update_config=True)

    # Track settings_saved signal emissions
    save_emissions = []
    dialog.settings_saved.connect(save_emissions.append)

    # Capture settings file state if it exists
    settings_file_exists = isolated_config.file.exists()
    settings_file_mtime = isolated_config.file.stat().st_mtime if settings_file_exists else None

    # Attempt save
    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)

    # Assert dialog stays open (not accepted, remains visible)
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert dialog.isVisible()

    # Assert settings_saved signal not emitted
    assert len(save_emissions) == 0

    # Assert no persistence occurred - settings file unchanged
    if settings_file_exists:
        assert isolated_config.file.stat().st_mtime == settings_file_mtime


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_settings_saved_signal_emitted_once(qapp, qtbot, isolated_config: AppConfig, tmp_path) -> None:
    """GIVEN changed values WHEN saved THEN signal fires exactly once with payload."""
    dialog = _make_dialog(qtbot, isolated_config)
    dialog.settings_page.model_group.model_combo.setCurrentText(AVAILABLE_LLM_MODELS[1])
    dialog.settings_page.paths_group.pdf_card.set_path(str(tmp_path / "pdf"), update_config=True)

    emissions: list[dict] = []
    dialog.settings_saved.connect(emissions.append)

    with qtbot.waitSignal(dialog.settings_saved, timeout=1000) as blocker:
        qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)

    qtbot.wait(50)
    assert len(emissions) == 1
    payload = blocker.args[0]
    assert isinstance(payload, dict)
    for key in SNAPSHOT_KEYS:
        assert key in payload


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_public_getter_returns_model(qapp, qtbot, isolated_config: AppConfig) -> None:
    """GIVEN dialog WHEN queried THEN get_values exposes full config mapping."""
    dialog = _make_dialog(qtbot, isolated_config)
    values = dialog.get_values()
    keys_from_config = set(isolated_config.get_all_keys())
    assert set(values) == keys_from_config
    for key in keys_from_config:
        assert values[key] == isolated_config.get(key)


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_auto_export_toggle_roundtrip(qapp, qtbot, isolated_config: AppConfig) -> None:
    """GIVEN auto-export toggled WHEN saved and reopened THEN state persists."""
    dialog = _make_dialog(qtbot, isolated_config)

    initial_state = dialog.get_values()["export/auto"]
    toggled_state = not bool(initial_state)

    # Use the public toggle widget
    dialog.settings_page.paths_group.auto_export_toggle.setChecked(toggled_state)

    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    reopened = _make_dialog(qtbot, isolated_config)
    assert reopened.get_values()["export/auto"] == toggled_state


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_tolerance_boundary_values(qapp, qtbot, isolated_config: AppConfig) -> None:
    """GIVEN boundary slider values WHEN saved THEN persisted values remain exact."""
    dialog = _make_dialog(qtbot, isolated_config)
    dialog.settings_page.analysis_group.warn_slider.setValue(1)
    dialog.settings_page.analysis_group.fail_slider.setValue(20)

    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    reopened = _make_dialog(qtbot, isolated_config)
    values = reopened.get_values()
    assert values["analysis/tolerance_warn"] == 1
    assert values["analysis/tolerance_fail"] == 20


def _run_rg(pattern: str, *extra_args: str) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[1]
    cmd = ["rg", "--no-ignore", pattern, "tests", *extra_args]
    return subprocess.run(
        cmd,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_no_qapplication_in_tests(qapp, qtbot) -> None:
    """GIVEN hygiene rules WHEN scanning tests THEN QApplication construction is absent."""
    if shutil.which("rg") is None:
        pytest.skip("rg binary not available for hygiene scan.")

    result = _run_rg(r"QApplication\(", "--glob", "!tests/conftest.py", "--glob", "!tests/test_settings_dialog.py")
    if result.returncode == 0:
        offending = result.stdout.strip().splitlines()
        pytest.fail(f"Tests must use qapp fixture instead of QApplication(): {json.dumps(offending, indent=2)}")
    assert result.returncode in (0, 1), result.stderr


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_no_exec_in_tests(qapp, qtbot) -> None:
    """GIVEN hygiene rules WHEN scanning tests THEN event loop exec calls are absent."""
    if shutil.which("rg") is None:
        pytest.skip("rg binary not available for hygiene scan.")

    result = _run_rg(r"\.exec\(", "--glob", "!tests/conftest.py")
    if result.returncode == 0:
        offending = result.stdout.strip().splitlines()
        pytest.fail(f"Tests must not call app.exec(): {json.dumps(offending, indent=2)}")
    assert result.returncode in (0, 1), result.stderr


def _decorator_is_gui(marker: ast.AST) -> bool:
    if isinstance(marker, ast.Attribute):
        return marker.attr == "gui" and isinstance(marker.value, ast.Attribute) and marker.value.attr == "mark"
    if isinstance(marker, ast.Call):
        return _decorator_is_gui(marker.func)
    return False


@pytest.mark.gui
@pytest.mark.usefixtures("isolated_config")
def test_all_ui_tests_use_fixtures(qapp, qtbot) -> None:
    """GIVEN gui-marked tests WHEN inspected THEN they declare qapp or qtbot fixtures."""
    repo_root = Path(__file__).resolve().parents[1]
    gui_functions: list[tuple[Path, str]] = []

    for path in repo_root.glob("tests/**/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and any(_decorator_is_gui(dec) for dec in node.decorator_list):
                arg_names = {arg.arg for arg in node.args.args}
                if not {"qtbot", "qapp"} & arg_names:
                    gui_functions.append((path.relative_to(repo_root), node.name))

    if gui_functions:
        details = ", ".join(f"{path}::{name}" for path, name in gui_functions)
        pytest.fail(f"GUI tests must request qapp or qtbot fixtures: {details}")
