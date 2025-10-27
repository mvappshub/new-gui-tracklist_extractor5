# Waveform Test Suite

## Overview

This directory contains the automated tests for the waveform viewer feature. The suite is organised into the following categories:

- **Unit tests** (`test_waveform_viewer.py`) verify the behaviour of `WaveformViewerDialog`.
- **Unit tests** (`test_waveform_editor.py`) cover `WaveformEditorDialog`, including region selection, snapping, and marker handling.
- **Integration tests** (`test_waveform_integration.py`) exercise the GUI workflow inside `fluent_gui.MainWindow`.
- **Configuration tests** (`test_waveform_config.py`) validate configuration defaults and the settings UI.
- **Shared fixtures** (`conftest.py`) provide reusable helpers for Qt applications, configuration isolation, and sample media assets.

## Running Tests

Execute the entire test suite:

```bash
pytest
```

Run a specific file:

```bash
pytest tests/test_waveform_viewer.py
```

Filter by marker:

```bash
pytest -m unit
```

Generate coverage:

```bash
pytest --cov=. --cov-report=html
```

Enable verbose output:

```bash
pytest -v
```

## Fixtures

- **`qapp`**: Session-scoped `QApplication` instance for Qt tests.
- **`isolated_config`**: Temporary configuration using in-memory QSettings.
- **`mock_wav_zip`**: Creates a ZIP archive containing a valid WAV sine wave for playback tests.
- **`empty_zip`** / **`invalid_wav_zip`**: Provide error-condition archives for robustness scenarios.

## Writing New Tests

- Use pytest-qt's `qtbot` fixture to interact with widgets and simulate user actions.
- Patch Qt signals or multimedia APIs with `unittest.mock` for deterministic behaviour.
- Group related tests inside `Test*` classes and follow the `test_*` naming convention.

## Troubleshooting

- Set `QT_QPA_PLATFORM=offscreen` when running headless (e.g. CI servers).
- Ensure optional dependencies (`pyqtgraph`, `soundfile`, Qt multimedia) are installed for waveform tests.
- If tests hang, verify a single global `QApplication` instance is active.

## Coverage Goals

- Target 80%+ coverage for `waveform_viewer.py`.
- Critical paths to exercise:
  - Both `WaveformViewerDialog` and `WaveformEditorDialog` initialization flows
  - Audio extraction from ZIP archives
  - Waveform rendering and downsampling logic
  - Playback controls (play, pause, stop, seek)
  - Region selection and snapping (editor only)
  - PDF marker visualization (editor only)
  - Volume control interactions
- Error handling for missing or invalid files
- Resource cleanup on dialog close

## Known Issues (Fixed)

The following issues were identified during code review and have been fixed:

1. **Missing `Dict` import**: Added to typing imports in `waveform_viewer.py`.
2. **Duplicate `_temp_wav` definition**: Removed the redundant assignment in `WaveformEditorDialog`.
3. **`_format_time()` inconsistency**: Standardized to use milliseconds in `WaveformViewerDialog` while keeping seconds in the editor.
4. **Position line detection bug**: Replaced the overview line search with a dedicated instance reference.
5. **Unused variables**: Removed unused `time_axis` calculations in detail view updates.
6. **Magic numbers**: Promoted waveform-related constants to named module-level values.
