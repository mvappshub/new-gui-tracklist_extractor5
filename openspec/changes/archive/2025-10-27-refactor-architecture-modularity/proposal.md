## Why
The UI refactor stalled because of coupling to legacy wrappers, a monolithic configuration object, and ad hoc status strings. The codebase is carrying divergent-change hotspots (`fluent_gui.py`, `config.AppConfig`) that force shotgun edits and make new features risky. Configuration logic is impossible to test in isolation because UI widgets manipulate `AppConfig` directly. Audio helpers mutate `WavInfo` records from the outside, and analysis status strings are duplicated across services and UI models. Together these issues increase cycle time, break encapsulation, and leave maintainability debt documented in PM notes.

## What Changes
Work will proceed in five deliberate phases so we can validate each milestone without rolling back:

1. **Legacy wrapper removal** – Redirect every import away from `fluent_gui.py`, update entry points, scripts, and tests, then delete the wrapper and retire characterization tests.
2. **Modular configuration loader** – Introduce dataclasses (`LlmSettings`, `UiSettings`, `AnalysisSettings`, `PathSettings`, etc.), extract shared option lists (LLM models, DPI scales) into single sources of truth, and add a `ConfigLoader` factory that reads `QSettings` once. Existing loader helpers in `ui/config_models.py` will call into the factory while `AppConfig` remains temporarily for compatibility.
3. **Settings UI decoupling** – Replace direct `cfg.set()` calls with `settingChanged`-style signals, inject scoped settings objects into widgets, and split long builder methods into smaller components. `SettingsDialog` becomes the coordinator that persists changes through the loader.
4. **Encapsulation in audio models** – Add `WavInfo.apply_parsed_info` (name TBD) so detector helpers and steps stop mutating attributes directly. Update AI helpers, strict/deterministic steps, and tests to rely on the new API.
5. **Enum-backed analysis status** – Introduce `AnalysisStatus` enum with severity, icon, and color helpers. Replace string literals throughout comparison services, UI models, exports, and tests, ensuring JSON output remains stable via enum serialization.

## Impact
- Refactoring touches configuration initialization, UI wiring, adapters, and services; regression risk is high without phased delivery. Each phase will ship behind targeted review gates before removing fallback paths.
- Expect churn in tests and fixtures: configuration loaders and status comparisons will need updates, and new unit coverage is required for the loader, enum behaviors, and UI signal flow.
- Build and deploy scripts (`tools/`, PyInstaller spec) must keep working; we will validate CLI entry points (`app.py`) after deleting `fluent_gui.py`.
- No user-facing workflow changes are intended, but transient instability is possible until all substeps ship; thorough CI (pytest + static checks) is mandatory per milestone.
