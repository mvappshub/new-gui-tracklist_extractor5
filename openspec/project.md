# Project Context

## Purpose
Tracklist Extractor is a desktop quality-control tool for the GZ Media mastering team. It pairs cue sheet PDFs with ZIP bundles of WAV masters, uses a vision language model to read the cue sheet, and produces structured track data that is compared against audio durations. Operators review mismatches, filter by severity, inspect individual tracks, and export JSON summaries for downstream reporting.

## Tech Stack
- Python 3.11 with extensive type hints, pydantic models, and dataclasses for domain entities.
- PyQt6 plus a custom Qt stylesheet (`gz_media.qss`) for the desktop UI; resource helpers under `ui/_icons_rc.py` register fonts and icons, with PyQtGraph reserved for waveform work.
- PyMuPDF (`fitz`) and Pillow for rendering PDF pages to images prior to AI analysis.
- `openai` client targeting OpenRouter-hosted vision models; `python-dotenv` for loading `.env`.
- `soundfile`/Libsndfile with built-in `wave` fallback for WAV duration probing; `numpy` supports generated fixtures.
- Tooling: `black`, `ruff`, `mypy`, `pytest`, `pytest-qt`, `coverage`, and packaging helpers (PyInstaller scripts and Qt resource builder) in `tools/`.

## Project Conventions

### Code Style
- Format Python with `black` (default settings) and lint with `ruff` (line length 120, `E501` ignored) plus `mypy`; the `.githooks/pre-commit` script enforces this trio, and `tools/check.sh` runs the same suite.
- Prefer fully type-annotated functions; share data via pydantic models (`core.models.analysis`) or dataclasses (`core.models.settings`), and avoid touching the global `cfg` outside entry points; load typed settings via `ui.config_models`.
- Write actionable English log messages; legacy Czech strings remain until retired, but new code should use English wording.
- Keep the UI responsive by delegating long-running work to `ui/workers` or `services` instead of blocking the main thread.

### Architecture Patterns
- Hexagonal layout: `core` contains domain logic and ports, `adapters` implement infrastructure for AI, PDF, audio, filesystem, and UI concerns, `services` orchestrate domain workflows, and `ui` renders the PyQt6 interface via injected dependencies.
- `app.py` is the primary entry point; `fluent_gui.py` persists only as a legacy wrapper and should not receive new development.
- Configuration lives in `config.AppConfig` (Qt `QSettings`); helpers in `ui/config_models.py` convert persisted values into typed settings consumed by services and widgets.
- Background analysis flows through `AnalysisWorkerManager`/`AnalysisWorker` (QThread) to keep the GUI responsive; results and exports are mediated by `services.analysis_service` and `services.export_service`.

### Testing Strategy
- Pytest with `pytest-qt` powers GUI coverage; `tests/conftest.py` supplies a session-wide `QApplication`, isolated QSettings, and synthetic ZIP/WAV archives.
- Unit tests focus on detectors, services, config loaders, and table models; golden JSON fixtures under `tests/data/golden/` anchor regression characterization.
- CI (`.github/workflows/test.yml`) runs on pushes to `main` and all PRs using Ubuntu with `QT_QPA_PLATFORM=offscreen` and `xvfb-run pytest --cov`.
- Aim for 80%+ coverage on new work, especially around waveform integration, exports, and tolerance handling; prefer deterministic fixtures over live API calls.

### Git Workflow
- Trunk-based development on `main`; create feature branches and submit pull requests. GitHub Actions enforces the test suite before merge.
- Run `black`, `ruff`, `mypy`, and `pytest` (or `tools/check.sh`) locally before pushing; keep lint/type debt confined to legacy allowlists.
- Follow OpenSpec guidance: author a proposal before implementing new capabilities, architectural shifts, or non-trivial refactors; manage specs with the `openspec` CLI.
- Commit messages use concise imperative verbs and reference the relevant OpenSpec change when applicable.

## Domain Context
- Input discovery scans configured PDF and ZIP directories, extracts numeric IDs (`adapters.filesystem.file_discovery`), and pairs files one-to-one, skipping ambiguous matches; pairs become `core.models.analysis.FilePair` instances.
- PDF parsing pipeline: `adapters.pdf.renderer.PdfImageRenderer` rasterizes pages via PyMuPDF, `adapters.ai.vlm.VlmClient` (OpenRouter) returns structured track JSON, and `core.domain.parsing.TracklistParser` normalizes data into `TrackInfo` grouped by side/position.
- Audio pipeline: `adapters.audio.wav_reader.ZipWavFileReader` materializes WAV entries to read durations, while `adapters.audio.chained_detector.ChainedAudioModeDetector` chains strict filename parsing, optional AI hints, and deterministic fallback to assign sides and normalized positions.
- `core.domain.comparison.compare_data` merges PDF and WAV data into `SideResult` objects, applying warn/fail tolerances, and the UI presents the two-level table (`ResultsTableModel` and `TracksTableModel`) with filtering, status coloring, exports, and hooks for PDF/waveform viewers.
- Exports use `services.export_service.export_results_to_json` to write timestamped JSON summaries, preserving file paths and per-side metrics for downstream reporting.

## Important Constraints
- Vision model calls require `OPENROUTER_API_KEY`; without it the VLM adapter operates in a no-op mode and yields empty results, so callers must handle the empty-track path gracefully.
- WAV archives must be ZIP files with safe member names; entries containing empty parts or traversal segments are skipped to avoid unsafe extraction.
- Tolerance thresholds (`ToleranceSettings`) drive warn/fail status in both services and UI; defaults are 2 seconds (warn) and 5 seconds (fail) and should remain configurable via settings.
- Qt assets (fonts/icons) must be registered through the resource helper (`ui._icons_rc`); missing brand fonts fall back to system defaults but should be bundled for production.
- Automated environments run headless; set `QT_QPA_PLATFORM=offscreen` and avoid modal dialogs that block when no display server exists.

## External Dependencies
- OpenRouter API (via the `openai` client) for vision-language track extraction.
- PyMuPDF (`fitz`) and Pillow for PDF rasterization.
- SoundFile/Libsndfile with built-in `wave` fallback for audio duration probing.
- PyQt6 (plus PyQtGraph for waveform features), Qt runtime libraries, and supporting system packages such as `xvfb`/`libgl` for Linux CI.
- `python-dotenv` for environment loading, `numpy` for synthesized audio fixtures, and `pytest-qt`/`pytest-mock` for testing utilities.
