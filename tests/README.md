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

## BDD UI Tests

SettingsDialog BDD tests are located in `tests/test_settings_dialog_bdd.py`. These tests use Given/When/Then structure for readability and cover 6 feature groups: smoke testing with defaults, round-trip persistence, validation & error handling, signals & public contract, critical toggles & boundaries, and CI invariants & hygiene.

Run BDD tests specifically:

```bash
pytest -m gui tests/test_settings_dialog_bdd.py -v
```

## IO/Audio Edge Case Tests

Comprehensive edge case testing for filesystem operations, audio processing, and system interactions:

- **Filesystem edge cases** (`tests/test_file_discovery_fs_edges.py`) - Unicode paths, hidden files, Windows long paths, and deterministic duplicate handling
- **Export edge cases** (`tests/test_export_fs_edges.py`) - read-only directories, locked files, permission errors, and partial write cleanup
- **Audio corruption handling** (`tests/test_wav_reader_corruption.py`) - invalid RIFF headers, corrupted data chunks, truncated files, and malformed ZIP containers
- **Configuration migration** (`tests/test_config_migrations.py`) - missing keys, unknown keys, type mismatches, and atomic save operations
- **Worker lifecycle safety** (`tests/test_worker_lifecycle.py`) - double-start prevention, cancel/restart sequences, race conditions, and signal consistency
- **Temporary cleanup robustness** (`tests/test_tmp_cleanup.py`) - locked temp files, permission handling, and cleanup verification

Run edge case tests:

```bash
pytest tests/test_file_discovery_fs_edges.py \
       tests/test_export_fs_edges.py \
       tests/test_wav_reader_corruption.py \
       tests/test_config_migrations.py \
       tests/test_worker_lifecycle.py \
       tests/test_tmp_cleanup.py -v
```

For Windows-specific tests (use `--basetemp` for temp cleanup):

```bash
pytest tests/test_*_edges.py tests/test_*_lifecycle.py tests/test_*_cleanup.py \
       --basetemp=.pytest_tmp -k "windows or long_path or sharing"
```

## Snapshot Testing

Configuration schema snapshots are stored in `tests/snapshots/settings_schema.json`. These are approval tests that must be deliberately updated when the configuration schema changes intentionally.

To update snapshots:
1. Review the test failure output showing expected vs actual values
2. Manually update `tests/snapshots/settings_schema.json` with the new expected values
3. Re-run tests to verify the snapshot matches

Never auto-update snapshots without reviewing changes. Snapshot mismatches indicate unintended configuration schema changes and should trigger investigation.

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
- Use Given/When/Then comments in BDD-style tests for clarity and readability.
- All SettingsDialog tests must verify behavior through public API (`get_values()`, signals) not internal widget state.
- Configuration changes must round-trip through QSettings and dialog reopen to verify persistence.
- Prefer `qtbot.waitUntil` / `qtbot.wait` over manual event loops, and always add widgets via `qtbot.addWidget` for cleanup.
- When testing file-system or settings behaviour, rely on `isolated_config` / `isolated_qsettings` so tests never touch user data.
- For negative I/O scenarios, raise `PermissionError` or `IOError` and assert the exception propagates (no silent fallbacks).
- Extend architectural guard-rails by editing `linter.ini` and adding snapshot tests when UI surface changes.
- Snapshot updates must be deliberate—edit `tests/snapshots/settings_schema.json` manually upon intentional schema changes, then re-run tests. (Adopting `syrupy` or `pytest-snapshot` would enable `--snapshot-update` in the future.)

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
