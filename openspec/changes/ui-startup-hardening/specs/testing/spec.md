## ADDED Requirements

### Requirement: Headless startup (DI wiring)
The app MUST start headless (offscreen), construct MainWindow, load resources, and exit cleanly without leaks.
#### Scenario: Start in offscreen mode
GIVEN QT_QPA_PLATFORM=offscreen
WHEN application starts and MainWindow is created
THEN no exception is raised AND resources/icons are available AND window can be shown and closed cleanly

### Requirement: PDF Viewer navigation & errors
The PDF viewer MUST navigate within bounds and surface errors for invalid/empty PDFs without crashing.
#### Scenario: Valid PDF navigation
GIVEN a valid multi-page PDF
WHEN user clicks next/prev/first/last
THEN current page changes accordingly and stays within bounds
#### Scenario: Invalid/empty PDF handling
GIVEN an invalid or empty PDF
WHEN opened in viewer
THEN a visible error is shown AND no crash occurs AND WARN/ERROR is logged

### Requirement: Theme & Delegates rendering
Delegates MUST return correct types/semantics for roles (text/icon/tooltip/foreground) per AnalysisStatus and HiDPI.
#### Scenario: Roles return proper types and values
GIVEN AnalysisStatus in {OK,WARN,FAIL}
WHEN data is requested for Display/Decoration/ToolTip/Foreground
THEN text/icon/tooltip/color match status semantics AND no None where a value is expected
#### Scenario: HiDPI icon rendering
GIVEN devicePixelRatio > 1
WHEN an icon is requested
THEN a valid (renderable) icon is returned

### Requirement: Table models role coverage
Results/Tracks models MUST provide consistent values across (column × role), with defined empties.
#### Scenario: ResultsTableModel roles matrix
GIVEN a populated ResultsTableModel
WHEN iterating (column × role)
THEN Display/Decoration/ToolTip/Foreground return expected semantics; empty cells return None/QVariant
#### Scenario: TracksTableModel roles matrix
GIVEN a populated TracksTableModel
WHEN iterating (column × role)
THEN the same guarantees hold

### Requirement: Unicode in UI
UI MUST correctly render diacritics/emoji across widgets and processing paths without crashes.
#### Scenario: Diacritics and emoji round-trip
GIVEN names with diacritics and emoji
WHEN displayed in tables and passed through parsers
THEN strings render correctly (no replacement char) AND no crashes occur

### Requirement: Logging assertions
Negative paths MUST produce WARN/ERROR logs that tests assert explicitly.
#### Scenario: Error/Warn logs on negative paths
GIVEN negative scenarios (invalid PDF, AI fallback, parser skips)
WHEN executed
THEN WARN/ERROR entries are logged and asserted in tests

### Requirement: Per-module coverage gates (CI)
CI MUST enforce per-module coverage thresholds to protect critical UI modules.
#### Scenario: Enforce module thresholds
GIVEN a CI run with coverage
WHEN thresholds are evaluated
THEN ui/dialogs/settings_dialog.py ≥ 60 %, ui/main_window.py ≥ 40 %, ui/models/*.py ≥ 70 %
