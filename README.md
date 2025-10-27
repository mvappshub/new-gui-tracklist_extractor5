# Tracklist Extractor

Desktop quality-control tool for pairing cue sheet PDFs with WAV masters. The application renders PDFs, invokes a vision-language model to extract structured track metadata, compares durations against WAV bundles, and surfaces discrepancies inside a PyQt6 UI.

## Key Components

- **Domain & Services**: `core/` encapsulates models and comparison logic, `services/` orchestrate end-to-end analysis and exports.
- **Adapters**: `adapters/` provide infrastructure for AI calls, PDF rendering, filesystem discovery, and audio probing. Waveform helpers now rely on `WavInfo.apply_parsed_info()` for encapsulated updates.
- **UI**: `ui/` contains the PyQt6 interface. `MainWindow` receives typed settings and worker dependencies; settings widgets emit `settingChanged`/`saveRequested` signals instead of mutating configuration directly.
- **Configuration**: `ConfigLoader` in `config.py` is the authoritative factory for typed settings (`LlmSettings`, `UiSettings`, `AnalysisSettings`, `PathSettings`, etc.). Global `cfg` remains for legacy access but new code should consume loader outputs or dataclasses.
- **Status Handling**: Comparison results use `core.domain.analysis_status.AnalysisStatus` (`OK`, `WARN`, `FAIL`) with helpers for severity, icon, and theme lookup. UI models render enum values and colors accordingly.

## Development Workflow

1. Install dependencies (`pip install -r requirements.txt`).
2. Run lint and tests via `tools/check.sh` or manually (`black`, `ruff`, `mypy`, `pytest`).
3. Use `openspec` to author proposals and keep specs up to date (`openspec validate <change-id> --strict`).
4. Launch the app with `python app.py` (Qt will look for `settings.json` in the working directory).

## Configuration Notes

- Persisted settings live in Qt `QSettings` (`GZMedia/TracklistExtractor`). `ConfigLoader` reads them and constructs typed dataclasses shared across the app.
- Settings UI is signal-driven; parent dialogs handle persistence via `ConfigLoader` and `AppConfig.set`.
- Auto-export paths and tolerances are configurable; JSON exports include enum-backed statuses serialized as strings.

## Tests

- Unit and integration tests reside in `tests/`. GUI tests use `pytest-qt` fixtures (`qapp`, `qtbot`).
- Golden comparison fixtures in `tests/data/golden/` validate analyzer behaviour.

## Changelog Highlights

- Removed legacy `fluent_gui.py` wrapper; all imports now target authoritative modules.
- Introduced modular config dataclasses, `ConfigLoader`, and signal-based settings UI.
- Added `WavInfo.apply_parsed_info()` to enforce encapsulation in audio helpers.
- Replaced status string literals with `AnalysisStatus` enum across domain, UI, and exports.
