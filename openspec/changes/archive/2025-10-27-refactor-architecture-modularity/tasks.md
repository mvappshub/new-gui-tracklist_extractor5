## Phase 1 - Legacy Wrapper Removal
- [x] 1.1 List every import of `fluent_gui.py` (app entry points, scripts, tests, tooling).
- [x] 1.2 Update `app.py`, `scripts/smoke_test.py`, GUI tests, and any helpers to import authoritative modules directly.
- [x] 1.3 Remove `fluent_gui.py`, drop the characterization tests, clean up mypy config, and run smoke/GUI checks to confirm the main window still launches.

## Phase 2 - Modular Config Loader
- [x] 2.1 Add scoped dataclasses in `core/models/settings.py` (`LlmSettings`, `UiSettings`, `AnalysisSettings`, `PathSettings`, plus shared enums as needed).
- [x] 2.2 Define single-source constants for LLM model options, DPI scales, and related lists inside `config.py`.
- [x] 2.3 Implement `ConfigLoader` that reads `QSettings`, builds the new dataclasses, and exposes factory methods while leaving `AppConfig` marked deprecated.
- [x] 2.4 Refactor `ui/config_models.py`, CLI scripts, and tests to obtain settings via `ConfigLoader`; ensure old code paths continue working during migration.

## Phase 3 - Settings UI Decoupling
- [x] 3.1 Add `settingChanged(key, value)` (or equivalent) signals to `FolderSettingCard` and other widgets currently mutating `cfg`.
- [x] 3.2 Split the large `_build_*` helpers into focused widget factories, injecting scoped dataclasses instead of the whole `AppConfig`.
- [x] 3.3 Update `SettingsDialog` to coordinate persistence through `ConfigLoader`, wire signals, and adjust Qt tests for the new observer workflow.

## Phase 4 - Audio Helper Encapsulation
- [x] 4.1 Introduce `WavInfo.apply_parsed_info` (name finalised during implementation) to own side/position updates and normalization.
- [x] 4.2 Update `ai_helpers`, detection steps (`StrictParserStep`, `AiParserStep`, `DeterministicFallbackStep`, fake detector), and chained detector normalization to call the new method.
- [x] 4.3 Refresh unit tests for detectors and parsing to assert encapsulated behaviour rather than direct attribute mutation.

## Phase 5 - Analysis Status Enum
- [x] 5.1 Create `AnalysisStatus` enum with severity ordering, icon lookup, color helpers, and string conversion.
- [x] 5.2 Replace literals in `core/domain/comparison.py`, UI table models, exports, filters, and tests with the enum API.
- [x] 5.3 Ensure serialization (Pydantic + JSON exports) produces the expected strings and extend tests to cover regression scenarios.

## Phase 6 - Validation & Communication
- [x] 6.1 Update documentation (README, PM ticket) with the new config workflow, signal pattern, and enum usage.
- [x] 6.2 Run full quality gates (`black`, `ruff`, `mypy`, `pytest --cov`) after each phase before moving forward.
- [x] 6.3 Publish migration guidance for any consumers that previously depended on `fluent_gui.py` or direct `cfg` access.
