# Test Suite Overview

This directory hosts the anti–reward-hacking verification suite that keeps AI-assisted extraction honest and regression-free. The tests are grouped into the following categories:

- **AI contract tests** (`tests/test_ai_contracts.py`) assert the exact wire-format used by `VlmClient` and `ai_helpers`, including prompts, `response_format`, base64 image encoding, and error handling paths.
- **PDF extractor integration** (`tests/test_pdf_extractor_contract.py`) exercises `extract_pdf_tracklist` end-to-end with mocked renderers and AI responses, covering valid data, empty payloads, exceptions, and multi-page aggregation.
- **Parser & comparison sanity checks** (`tests/test_parser_sanity.py`) pin strict filename parsing, tracklist parsing, and tolerance boundaries for `compare_data`, including doctest coverage for negative scenarios.
- **GUI hygiene tests** (`tests/test_gui_simple.py`, `tests/test_gui_minimal.py`, `tests/test_gui_show.py`, `tests/test_settings_dialog.py`) ensure every Qt test reuses the shared `qapp` fixture and drives the event loop explicitly via `qtbot.waitUntil` instead of `app.exec()`.
- **Architecture & guard-rails** (`tests/test_architecture.py`, `tests/snapshots/*.py`) enforce layered imports with import-linter, monitor cyclomatic complexity (radon), check invariant greps, and protect UI models with snapshots.
- **Worker & export contracts** (`tests/test_worker_contracts.py`, `tests/test_export_auto.py`, `tests/test_export_service.py`) verify worker state transitions, signal types, directory creation, and failure propagation for export routines.
- **Resource integrity** (`tests/test_resources.py`) confirms `_icons_rc.py` is compiled and that required `:/icons/*` assets resolve via `QResource`.

## Running Tests

Run the full suite:

```bash
pytest
```

Execute the anti–reward-hacking regression command (Task 7.1):

```bash
pytest tests/test_ai_contracts.py \
       tests/test_pdf_extractor_contract.py \
       tests/test_parser_sanity.py \
       tests/test_gui_simple.py \
       tests/test_architecture.py \
       tests/test_worker_contracts.py \
       tests/snapshots/test_analysis_status_snapshot.py \
       tests/snapshots/test_results_table_model_snapshot.py
```

Lint architecture contracts directly:

```bash
python -m importlinter.cli lint --config linter.ini
```

Check cyclomatic complexity thresholds:

```bash
radon cc src --total-average
```

Run doctests for parser modules:

```bash
pytest --doctest-modules core/parsers
```

## Key Fixtures (tests/conftest.py)

- **`disable_network_access`** *(session, autouse)* – monkeypatches `socket` APIs so no test can reach the Internet.
- **`unset_ai_api_keys`** *(session, autouse)* – clears `OPENAI_API_KEY` and `OPENROUTER_API_KEY` to prevent accidental live calls.
- **`qapp`** *(session)* – single `QApplication` instance shared by all Qt tests; always request it via the fixture.
- **`isolated_qsettings`** *(session)* – helper that rewires `QSettings` paths into temporary directories for per-test isolation.
- **`isolated_config`** – hands each test a fresh `AppConfig` bound to the isolated QSettings storage; also monkeypatches module-level `cfg` references.
- **Media fixtures** (`mock_wav_zip`, `empty_zip`, `invalid_wav_zip`) – supply WAV archives for audio-path tests.
- **Tolerance & ID fixtures** (`tolerance_settings`, `id_extraction_settings`, `audio_mode_detector`) – provide deterministic configuration objects.

## Authoring Guidelines

- Treat AI-facing code as a contract: assert request payloads, temperature, message structure, and JSON shape explicitly.
- Prefer `qtbot.waitUntil` / `qtbot.wait` over manual event loops, and always add widgets via `qtbot.addWidget` for cleanup.
- When testing file-system or settings behaviour, rely on `isolated_config` / `isolated_qsettings` so tests never touch user data.
- For negative I/O scenarios, raise `PermissionError` or `IOError` and assert the exception propagates (no silent fallbacks).
- Extend architectural guard-rails by editing `linter.ini` and adding snapshot tests when UI surface changes.
- Snapshot updates must be deliberate—run `pytest --snapshot-update` locally and commit regenerated JSON alongside code changes.

## CI Expectations

The CI pipeline runs the following fail-fast stages (see F-PRE6/F-PRE9 requirements):

1. **Invariant greps** – abort if forbidden patterns such as `QApplication(` in tests or `print(` in production appear.
2. **Resource compilation** – validate `_icons_rc.py` via `tests/test_resources.py`; failing to compile resources should fail the build.
3. **Radon complexity gate** – fail when any function reaches complexity ≥ 15 (warn at > 10).
4. **Doctests** – run on parser modules to keep documentation examples current.
5. **Unit & integration tests** – standard pytest run with coverage reporting.
6. **Diff coverage** – require ≥ 85 % coverage on modified files.
7. **Snapshot verification** – ensure UI snapshots match the committed JSON fixtures.

Keep those stages green locally before pushing to avoid noisy CI cycles.
