## ADDED Requirements

### Requirement: Legacy Wrapper Removed
All production entry points MUST stop importing `fluent_gui.py`, and the wrapper MUST be removed from the codebase.

#### Scenario: No fluent_gui Imports
- **GIVEN** the repository after the change is merged  
- **WHEN** searching for `fluent_gui` across source, tests, and tooling  
- **THEN** no imports or references are present  
- **AND** application entry points run successfully via `app.py`.

### Requirement: Modular Configuration Loader
Configuration MUST be composed of scoped dataclasses produced by a central `ConfigLoader`, eliminating direct dependence on the monolithic `AppConfig`.

#### Scenario: Typed Settings Construction
- **GIVEN** `ConfigLoader` is initialized with `QSettings` data  
- **WHEN** clients request settings for LLM, UI, analysis, or paths  
- **THEN** they receive strongly typed dataclass instances  
- **AND** shared option lists (e.g., LLM models, DPI scale choices) are defined in exactly one place.

### Requirement: Decoupled Settings UI
Settings UI widgets MUST communicate changes via observer signals/callbacks instead of mutating configuration classes directly.

#### Scenario: Folder Setting Emits Change
- **GIVEN** a `FolderSettingCard` instance bound to a config key  
- **WHEN** the user edits the folder path or chooses a directory  
- **THEN** the widget emits a `settingChanged` (or equivalent) event containing the key and new value  
- **AND** persistence is handled by the parent controller using injected settings objects.

### Requirement: Encapsulated WavInfo Updates
Updates derived from AI parsing MUST be applied through methods on `WavInfo`, not by mutating attributes externally.

#### Scenario: Apply Parsed Info
- **GIVEN** a `WavInfo` instance and parsed AI metadata for side/position  
- **WHEN** `WavInfo.apply_parsed_info(parsed)` is called  
- **THEN** the instance updates its own `side` and `position` fields according to normalization rules  
- **AND** helper modules no longer assign those attributes directly.

### Requirement: Analysis Status Enum
Analysis status MUST be represented by a dedicated `AnalysisStatus` enum that encapsulates severity and presentation details.

#### Scenario: Status Drives UI State
- **GIVEN** a `SideResult` produced by the comparison service  
- **WHEN** UI models render the status column  
- **THEN** they use `AnalysisStatus` members to resolve severity, colors, and icons  
- **AND** no code compares raw string literals like `"OK"` or `"FAIL"`.
