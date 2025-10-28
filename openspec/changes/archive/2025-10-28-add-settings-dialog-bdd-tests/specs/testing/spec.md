## ADDED Requirements

### Requirement: Open & Defaults (BDD)
SettingsDialog MUST expose business-meaningful defaults via a public model, not only widget texts, and allow exporting a stable schema snapshot.
#### Scenario: Open dialog shows expected defaults
GIVEN isolated QSettings and qapp
WHEN I open SettingsDialog
THEN default values match the public model (business-meaningful), not only widget texts
AND exporting a schema dict of public keys matches the snapshot

### Requirement: Round-trip Persistence
SettingsDialog MUST persist changed values to QSettings and load them identically on reopen.
#### Scenario: Save + reopen preserves values
GIVEN I change LLM model, auto-export and paths
WHEN I click Save/OK
THEN QSettings contains new values AND reopening the dialog shows the same values

### Requirement: Validation & Error Handling
Invalid required inputs MUST block saving and surface a clear visual error without writing to QSettings.
#### Scenario: Invalid input is blocked and signaled
GIVEN an invalid or empty required field
WHEN I try to save
THEN an error indication is visible and no persistence occurs (QSettings unchanged)

### Requirement: Signals & Public Contract
The dialog MUST emit a single settings_saved(payload) on valid save and expose a public getter of values/model.
#### Scenario: settings_saved emitted once with payload
GIVEN a listener on settings_saved
WHEN I save valid changes
THEN settings_saved(payload) is emitted exactly once and payload is a serializable dict
AND dialog exposes a public getter for values/model

### Requirement: Critical Toggles & Boundaries
Critical toggles (e.g. auto-export) and boundary numeric values MUST round-trip exactly through save/reopen.
#### Scenario: Auto-export toggle and tolerance edges
GIVEN auto-export toggle and boundary values (min/max)
WHEN I change and save
THEN model and QSettings reflect the change and reopening preserves values

### Requirement: GUI Test Hygiene
All UI tests MUST use pytest-qt fixtures (qapp/qtbot) and MUST NOT run their own event loop.
#### Scenario: No manual event loop in tests
GIVEN new UI tests
WHEN they run
THEN they use qapp/qtbot (pytest-qt) and do not call QApplication(...) or app.exec()
