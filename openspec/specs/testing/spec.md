# testing Specification

## Purpose
Ensures anti-reward-hacking test coverage across AI adapters, PDF extraction, parser tolerance, GUI hygiene, architecture guard-rails, QSettings isolation, and worker/export flows.

## Requirements
### Requirement: Mandatory Test Safeguards
The test environment MUST be isolated from external dependencies, especially network access and real API keys, to guarantee deterministic and reliable execution.

#### Scenario: Network access disabled
- **GIVEN** jakýkoli test je sputěn
- **WHEN** test se pokusí o síové volání
- **THEN** síové volání je blokováno (např. `socket.socket` vyhodí chybu)

#### Scenario: AI API keys unset
- **GIVEN** jakýkoli test je sputěn
- **WHEN** kód se pokusí získat `OPENAI_API_KEY` nebo `OPENROUTER_API_KEY`
- **THEN** klíče jsou `None` nebo prázdné řetězce, co zabraňuje reálným API voláním

### Requirement: AI Adapter Contract Testing
AI adapters (`VlmClient`, `ai_helpers`) MUST be verified with contract tests that cover real wire-format structures (messages, `response_format`, image encoding) without calling live APIs.

#### Scenario: VlmClient message format verification
- **GIVEN** `VlmClient` instance s mockovaným OpenAI klientem
- **WHEN** `get_json_response` je zavolána s promptem a obrázky
- **THEN** mockovaný klient zachytí parametry volání
- **AND** `model`, `messages` (role/content s image_url), `response_format={"type": "json_object"}`, `temperature=0.0` jsou ověřeny

#### Scenario: VlmClient image encoding
- **GIVEN** 1×1 PNG obrázek vytvořený pomocí PIL
- **WHEN** `_to_data_url` je zavolána
- **THEN** návrat začíná `data:image/png;base64,`
- **AND** base64 část je dekódovatelná

#### Scenario: VlmClient error handling
- **GIVEN** mockovaná response s `content=None`
- **WHEN** `get_json_response` je zavolána
- **THEN** vyhodí `ValueError("AI returned an empty response.")`

#### Scenario: ai_parse_batch request format
- **GIVEN** fake OpenAI klient co loguje parametry
- **WHEN** `ai_parse_batch` je zavolána s filenames
- **THEN** system prompt obsahuje "STRICT JSON"
- **AND** filenames jsou předány jako JSON v user content

### Requirement: PDF Extraction Integration Testing (No-Network)
`extract_pdf_tracklist` MUST be tested end-to-end without network access using mocked `PdfImageRenderer` and `VlmClient`, covering valid responses, empty payloads, and exceptions.

#### Scenario: Valid tracklist extraction
- **GIVEN** mockovaný renderer vrací jeden obrázek
- **AND** mockovaný `VlmClient` vrací validní `{"tracks": [...]}`
- **WHEN** `extract_pdf_tracklist` je zavolána
- **THEN** vrací dict seskupený podle side
- **AND** počty záznamů odpovídají

#### Scenario: Empty AI response
- **GIVEN** mockovaný `VlmClient` vrací prázdný `{}`
- **WHEN** `extract_pdf_tracklist` je zavolána
- **THEN** vrací prázdný dict `{}`
- **AND** warning log je zaznamenán

#### Scenario: AI exception handling
- **GIVEN** mockovaný `VlmClient` vyhodí výjimku při jedné stránce
- **WHEN** `extract_pdf_tracklist` je zavolána s více stránkami
- **THEN** přeskočí chybnou stránku
- **AND** pokračuje s dalími stránkami

### Requirement: Parser Robustness Testing
`StrictFilenameParser` and `TracklistParser` MUST include targeted negative tests for conflicting patterns, malformed input, and edge cases, including doctests.

#### Scenario: Conflicting filename patterns
- **GIVEN** filename s konfliktními side patterny (např. `"Side_A_B1_track.wav"`)
- **WHEN** `StrictFilenameParser.parse` je zavolána
- **THEN** vrací deterministický výsledek (první match vyhrává)

#### Scenario: Malformed duration handling
- **GIVEN** track data s `duration_formatted="invalid"`
- **WHEN** `TracklistParser.parse` je zavolána
- **THEN** track je přeskočen (ne crash)
- **AND** warning log je zaznamenán

#### Scenario: Doctests for parsing logic
- **GIVEN** doctesty definované přímo v modulu parseru
- **WHEN** doctesty jsou sputěny
- **THEN** vechny doctesty projdou, ověřující chování pro konfliktní a negativní případy

### Requirement: Comparison Tolerance Edge Cases
`compare_data` MUST be exercised with differences that sit exactly on the warn/fail tolerance boundaries.

#### Scenario: Exact warn tolerance boundary
- **GIVEN** PDF a WAV data s rozdílem přesně `warn_tolerance` (2s)
- **WHEN** `compare_data` je zavolána
- **THEN** status je `WARN`

#### Scenario: Exact fail tolerance boundary
- **GIVEN** PDF a WAV data s rozdílem přesně `fail_tolerance` (5s)
- **WHEN** `compare_data` je zavolána
- **THEN** status je `FAIL`

#### Scenario: Negative difference handling
- **GIVEN** WAV kratí ne PDF (negativní rozdíl)
- **WHEN** `compare_data` je zavolána
- **THEN** `abs(difference)` se pouívá pro tolerance check

### Requirement: GUI Test Hygiene
GUI tests MUST use the shared `qapp` fixture from `tests/conftest.py` instead of manually instantiating `QApplication`, and MUST drive the event loop explicitly.

#### Scenario: Unified QApplication fixture
- **GIVEN** GUI test potřebující QApplication
- **WHEN** test je definován
- **THEN** pouívá `qapp` fixture jako parametr
- **AND** neobsahuje ruční `QApplication(sys.argv)`
- **AND** pytest-qt spravuje event loop

#### Scenario: Explicit event loop control
- **GIVEN** GUI test, který potřebuje čekat na události
- **WHEN** test je definován
- **THEN** pouívá `qtbot.waitUntil` nebo podobné mechanismy
- **AND** neobsahuje `app.exec()`

### Requirement: Architecture & CI Guard-rails
The project MUST enforce architectural and CI guard-rails to uphold layering, limit complexity, verify invariants, and detect regressions via snapshot tests.

#### Scenario: Layered architecture enforcement
- **GIVEN** kód, který poruuje definované architektonické vrstvy (např. `adapters` importuje `core.domain`)
- **WHEN** architektonické testy jsou sputěny
- **THEN** testy selou a nahlásí poruení

#### Scenario: Cyclomatic complexity gate
- **GIVEN** funkce s cyklomatickou komplexitou ? 15
- **WHEN** CI krok pro `radon cc` je sputěn
- **THEN** CI pipeline sele

#### Scenario: Invariant violation detection
- **GIVEN** kód, který obsahuje zakázané invarianty (např. `QApplication(` v testech, `print(` v produkčním kódu)
- **WHEN** CI krok pro grepy invariantů je sputěn
- **THEN** CI pipeline sele

#### Scenario: Snapshot test for AnalysisStatus
- **GIVEN** `AnalysisStatus` objekt s definovanými atributy
- **WHEN** snapshot test je sputěn
- **THEN** serializovaný stav `AnalysisStatus` odpovídá uloenému snapshotu `(name, value, severity, icon_name, color_key)`

#### Scenario: Snapshot test for ResultsTableModel
- **GIVEN** `ResultsTableModel` objekt s definovanými atributy
- **WHEN** snapshot test je sputěn
- **THEN** serializovaný stav `ResultsTableModel` odpovídá uloenému snapshotu `(header, renderer_id)`

### Requirement: QSettings Isolation & Resources Build
`QSettings` MUST be isolated during tests and the resource build process MUST fail loudly in CI instead of silently falling back.

#### Scenario: Isolated QSettings in tests
- **GIVEN** test, který pouívá `QSettings`
- **WHEN** test je sputěn
- **THEN** `QSettings` instance je izolovaná pro daný test (session-scoped fixture, per-test files)
- **AND** změny v nastavení neovlivňují jiné testy

#### Scenario: Resources build gate in CI
- **GIVEN** chybějící nebo chybně zkompilovaný `_icons_rc.py`
- **WHEN** CI krok pro kontrolu resources je sputěn
- **THEN** CI pipeline sele
- **AND** nedojde k tichému fallbacku na chybějící resources

### Requirement: Worker Contract & Export Negative I/O
Workers MUST have their public API covered by tests and export routines MUST handle negative I/O scenarios robustly.

#### Scenario: Worker public API contract
- **GIVEN** instance workeru
- **WHEN** jsou volány metody `is_running()`, `state()` nebo je připojen slot k signálu `state_changed(WorkerState)`
- **THEN** metody vracejí očekávané typy (`bool`, `Enum`) a signál je emitován s korektním typem

#### Scenario: Export to non-existent directory
- **GIVEN** exportní operace s cílovým adresářem, který neexistuje
- **WHEN** export je sputěn
- **THEN** cílový adresář je automaticky vytvořen
- **AND** export proběhne úspěně

#### Scenario: Export write error handling
- **GIVEN** exportní operace, kde dojde k `IOError` nebo `PermissionError` při zápisu souboru
- **WHEN** export je sputěn
- **THEN** exportní funkce vyhodí příslunou výjimku
- **AND** aplikace necrashne

### Requirement: Headless startup (DI wiring)
The app MUST start headless (offscreen), construct MainWindow, load resources, and exit cleanly without leaks.
#### Scenario: Start in offscreen mode
- **GIVEN** QT_QPA_PLATFORM=offscreen
- **WHEN** application starts and MainWindow is created
- **THEN** no exception is raised AND resources/icons are available AND window can be shown and closed cleanly

### Requirement: PDF Viewer navigation & errors
The PDF viewer MUST navigate within bounds and surface errors for invalid/empty PDFs without crashing.
#### Scenario: Valid PDF navigation
- **GIVEN** a valid multi-page PDF
- **WHEN** user clicks next/prev/first/last
- **THEN** current page changes accordingly and stays within bounds
#### Scenario: Invalid/empty PDF handling
- **GIVEN** an invalid or empty PDF
- **WHEN** opened in viewer
- **THEN** a visible error is shown AND no crash occurs AND WARN/ERROR is logged

### Requirement: Theme & Delegates rendering
Delegates MUST return correct types/semantics for roles (text/icon/tooltip/foreground) per AnalysisStatus and HiDPI.
#### Scenario: Roles return proper types and values
- **GIVEN** AnalysisStatus in {OK,WARN,FAIL}
- **WHEN** data is requested for Display/Decoration/ToolTip/Foreground
- **THEN** text/icon/tooltip/color match status semantics AND no None where a value is expected
#### Scenario: HiDPI icon rendering
- **GIVEN** devicePixelRatio > 1
- **WHEN** an icon is requested
- **THEN** a valid (renderable) icon is returned

### Requirement: Table models role coverage
Results/Tracks models MUST provide consistent values across (column × role), with defined empties.
#### Scenario: ResultsTableModel roles matrix
- **GIVEN** a populated ResultsTableModel
- **WHEN** iterating (column × role)
- **THEN** Display/Decoration/ToolTip/Foreground return expected semantics; empty cells return None/QVariant
#### Scenario: TracksTableModel roles matrix
- **GIVEN** a populated TracksTableModel
- **WHEN** iterating (column × role)
- **THEN** the same guarantees hold

### Requirement: Unicode in UI
UI MUST correctly render diacritics/emoji across widgets and processing paths without crashes.
#### Scenario: Diacritics and emoji round-trip
- **GIVEN** names with diacritics and emoji
- **WHEN** displayed in tables and passed through parsers
- **THEN** strings render correctly (no replacement char) AND no crashes occur

### Requirement: Logging assertions
Negative paths MUST produce WARN/ERROR logs that tests assert explicitly.
#### Scenario: Error/Warn logs on negative paths
- **GIVEN** negative scenarios (invalid PDF, AI fallback, parser skips)
- **WHEN** executed
- **THEN** WARN/ERROR entries are logged and asserted in tests

### Requirement: Per-module coverage gates (CI)
CI MUST enforce per-module coverage thresholds to protect critical UI modules.
#### Scenario: Enforce module thresholds
- **GIVEN** a CI run with coverage
- **WHEN** thresholds are evaluated
- **THEN** ui/dialogs/settings_dialog.py ≥ 60 %, ui/main_window.py ≥ 40 %, ui/models/*.py ≥ 70 %

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
