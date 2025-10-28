## ADDED Requirements

### Requirement: File discovery on Windows/Unicode/long-path
File discovery MUST handle diacritics, hidden/system files, and Windows long paths without crashes.
#### Scenario: Unicode and hidden files
GIVEN directories with diacritics and hidden/system files
WHEN discovering pairs
THEN Unicode paths are handled, hidden/system files follow policy, and no crash occurs
#### Scenario: Long paths with \\?\\ prefix
GIVEN Windows long-path prefixed paths
WHEN discovering and exporting
THEN operations succeed or fail with explicit error, not crash

### Requirement: Export permission/lock handling
Exports MUST fail cleanly on permission/lock errors with no partial outputs and proper logging.
#### Scenario: Locked destination file
GIVEN destination file locked by another process
WHEN export runs
THEN export fails with PermissionError/WinError and no partial output remains; error is logged

### Requirement: WAV corruption handling
WAV/ZIP corruption MUST have a defined contract (skip+WARN or explicit exception) without XFAIL masking.
#### Scenario: Corrupted WAV/ZIP
GIVEN a corrupted WAV and a ZIP with CRC failure
WHEN reading
THEN system either skips with WARN or raises a defined exception type; behavior is asserted in tests

### Requirement: Config migration & compatibility
Config loading/saving MUST support defaults, ignore unknown keys with WARN, and use atomic writes with rollback.
#### Scenario: Missing/unknown keys and type changes
GIVEN an older config missing new keys, extra unknown keys, and values with changed types
WHEN loading and saving
THEN defaults are applied, unknown keys ignored with WARN, type conversion is applied or a clear error is raised, and save is atomic with rollback

### Requirement: Worker lifecycle & race safety
Workers MUST avoid race conditions across double-start, cancel-restart, and window close during running.
#### Scenario: Double-start and cancel-restart
GIVEN a worker
WHEN started twice or canceled then started again
THEN states transition consistently; no zombie threads; is_running()/state() remain coherent

### Requirement: Temp cleanup robustness
Test/CI temp cleanup MUST continue despite locked files, logging WARN and leaving no residual dirs otherwise.
#### Scenario: Locked temp file during cleanup
GIVEN a locked temp file
WHEN pytest cleanup runs
THEN a WARN is logged, suite continues, and temp dirs are otherwise clean
