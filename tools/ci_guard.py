#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PRINT_ALLOWLIST = {
    Path("tests/test_config.py"),
    Path("tests/test_gui_show.py"),
    Path("tests/test_settings_dialog.py"),
}

QAPP_EXEC_ALLOWLIST = {Path("tests/test_gui_show.py")}

SYMBOL_ALLOWLIST = {Path("ui/constants.py"), Path("ui/__init__.py")}

RADON_ALLOWLIST = {

    "adapters/audio/ai_helpers.py:detect_audio_mode_with_ai",
    "adapters/audio/ai_helpers.py:merge_ai_results",
    "adapters/audio/fake_mode_detector.py:FakeAudioModeDetector._normalize_positions",
    "adapters/audio/steps.py:StrictParserStep.process",
    "adapters/audio/wav_reader.py:ZipWavFileReader",
    "adapters/audio/wav_reader.py:ZipWavFileReader.read_wav_files",
    "adapters/filesystem/file_discovery.py:discover_and_pair_files",
    "core/domain/parsing.py:StrictFilenameParser",
    "core/domain/parsing.py:StrictFilenameParser.parse",
    "ui/main_window.py:MainWindow.on_bottom_cell_clicked",
    "ui/models/results_table_model.py:ResultsTableModel.data",
    "ui/models/tracks_table_model.py:TracksTableModel.data",
    "ui/models/tracks_table_model.py:TracksTableModel.get_track_row_data",
}

MODULE_COVERAGE_THRESHOLDS = {
    "ui/dialogs/settings_dialog.py": 60,
    "ui/main_window.py": 40,
    "ui/models/results_table_model.py": 70,
    "ui/models/tracks_table_model.py": 70,
}


def _iter_py_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if ".venv" in path.parts or ".pytest_cache" in path.parts:
            continue
        yield path


def check_invariants() -> None:
    errors: list[str] = []

    pattern_checks = [
        (re.compile(r"QApplication\("), lambda rel: rel.parts and rel.parts[0] == "tests" and rel not in PRINT_ALLOWLIST and rel.name != "conftest.py"),
        (re.compile(r"qapp\.exec\("), lambda rel: rel.parts and rel.parts[0] == "tests" and rel not in QAPP_EXEC_ALLOWLIST),
        (re.compile(r"print\("), lambda rel: rel.parts and rel.parts[0] == "tests" and rel not in PRINT_ALLOWLIST),
        (re.compile(r"from\s+.+\s+import\s+_\w+"), lambda rel: True),
    ]

    for pattern, predicate in pattern_checks:
        for path in _iter_py_files(PROJECT_ROOT):
            rel = path.relative_to(PROJECT_ROOT)
            if not predicate(rel):
                continue
            text = path.read_text(encoding="utf-8")
            if pattern.search(text):
                errors.append(f"Invariant violation: pattern '{pattern.pattern}' in {rel}")

    ui_dir = PROJECT_ROOT / "ui"
    for path in _iter_py_files(ui_dir):
        rel = path.relative_to(PROJECT_ROOT)
        if rel in SYMBOL_ALLOWLIST:
            continue
        text = path.read_text(encoding="utf-8")
        if "SYMBOL_" in text:
            errors.append(f"Invariant violation: 'SYMBOL_' usage in {rel}")

    if errors:
        print("Invariant checks failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print("Invariant checks passed")


def check_resources() -> None:
    icons_rc = PROJECT_ROOT / "ui" / "_icons_rc.py"
    if not icons_rc.exists():
        print("Missing ui/_icons_rc.py")
        sys.exit(1)
    try:
        importlib.import_module("ui._icons_rc")
    except Exception as exc:  # pragma: no cover
        print(f"Failed to import ui._icons_rc: {exc}")
        sys.exit(1)
    print("Qt resource module available")


def check_radon(threshold: str = "C") -> None:
    targets = ["adapters", "core", "services", "ui"]
    result = subprocess.run(
        [sys.executable, "-m", "radon", "cc", "--min", threshold, *targets],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=PROJECT_ROOT,
    )
    output = result.stdout.strip()
    violations: list[str] = []
    current_path = ""
    for line in output.splitlines():
        if not line.startswith(" "):
            current_path = line.strip().replace("\\", "/")
            continue
        parts = line.strip().split()
        if len(parts) >= 3:
            name = parts[2]
            key = f"{current_path}:{name}"
            if key not in RADON_ALLOWLIST:
                violations.append(f"{key} ({parts[-1]})")
    if violations:
        print("Radon complexity gate failed; offending blocks (outside allowlist):")
        for item in violations:
            print(f"  - {item}")
        sys.exit(1)
    print("Radon complexity gate passed")


def check_module_coverage() -> None:
    """Check per-module coverage thresholds."""
    violations: list[str] = []

    # Generate coverage JSON data
    coverage_json_path = PROJECT_ROOT / "coverage.json"
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "json", "-o", str(coverage_json_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        violations.append(f"Module coverage gate failed: coverage json generation failed")
        return

    import json

    try:
        with open(coverage_json_path, 'r', encoding='utf-8') as f:
            coverage_data = json.load(f)

        # Clean up temp file
        coverage_json_path.unlink(missing_ok=True)

        files_data = coverage_data.get('files', {})

        for module_path, min_threshold in MODULE_COVERAGE_THRESHOLDS.items():
            # Normalize paths to POSIX style for cross-platform matching
            normalized_module = module_path.replace('\\', '/')

            # Find matching file in coverage data
            module_file = None
            for file_path in files_data:
                normalized_file = file_path.replace('\\', '/')
                if normalized_file == normalized_module or normalized_file.endswith('/' + normalized_module):
                    module_file = file_path
                    break

            if module_file is None:
                violations.append(f"Module coverage gate failed: {module_path} not found in coverage data (threshold: {min_threshold}%)")
                continue

            file_data = files_data[module_file]
            summary = file_data.get('summary', {})
            coverage_percentage = summary.get('percent_covered')

            if coverage_percentage is None:
                violations.append(f"Module coverage gate failed: {module_path} coverage parsing failed (threshold: {min_threshold}%)")
                continue

            if coverage_percentage < min_threshold:
                violations.append(f"Module coverage gate failed: {module_path} has {coverage_percentage:.1f}% (threshold: {min_threshold}%)")

    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        violations.append(f"Module coverage gate failed: error parsing coverage data - {e}")

    if violations:
        print("Module coverage gates failed:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    print("Module coverage gates passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="CI guard utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("invariants")
    sub.add_parser("resources")
    sub.add_parser("radon")
    sub.add_parser("coverage")

    args = parser.parse_args()

    if args.command == "invariants":
        check_invariants()
    elif args.command == "resources":
        check_resources()
    elif args.command == "radon":
        check_radon()
    elif args.command == "coverage":
        check_module_coverage()
    else:  # pragma: no cover
        parser.error("Unknown command")


if __name__ == "__main__":
    main()
