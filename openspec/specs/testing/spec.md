# testing Specification

## Purpose
Ensures anti-reward-hacking test coverage across AI adapters, PDF extraction, parser tolerance, GUI hygiene, architecture guard-rails, QSettings isolation, and worker/export flows.

## Requirements
### Requirement: Mandatory Test Safeguards
The test environment MUST be isolated from external dependencies, especially network access and real API keys, to guarantee deterministic and reliable execution.

#### Scenario: Network access disabled
- **GIVEN** jakıkoli test je spuštìn
- **WHEN** test se pokusí o síové volání
- **THEN** síové volání je blokováno (napø. `socket.socket` vyhodí chybu)

#### Scenario: AI API keys unset
- **GIVEN** jakıkoli test je spuštìn
- **WHEN** kód se pokusí získat `OPENAI_API_KEY` nebo `OPENROUTER_API_KEY`
- **THEN** klíèe jsou `None` nebo prázdné øetìzce, co zabraòuje reálnım API voláním

### Requirement: AI Adapter Contract Testing
AI adapters (`VlmClient`, `ai_helpers`) MUST be verified with contract tests that cover real wire-format structures (messages, `response_format`, image encoding) without calling live APIs.

#### Scenario: VlmClient message format verification
- **GIVEN** `VlmClient` instance s mockovanım OpenAI klientem
- **WHEN** `get_json_response` je zavolána s promptem a obrázky
- **THEN** mockovanı klient zachytí parametry volání
- **AND** `model`, `messages` (role/content s image_url), `response_format={"type": "json_object"}`, `temperature=0.0` jsou ovìøeny

#### Scenario: VlmClient image encoding
- **GIVEN** 1×1 PNG obrázek vytvoøenı pomocí PIL
- **WHEN** `_to_data_url` je zavolána
- **THEN** návrat zaèíná `data:image/png;base64,`
- **AND** base64 èást je dekódovatelná

#### Scenario: VlmClient error handling
- **GIVEN** mockovaná response s `content=None`
- **WHEN** `get_json_response` je zavolána
- **THEN** vyhodí `ValueError("AI returned an empty response.")`

#### Scenario: ai_parse_batch request format
- **GIVEN** fake OpenAI klient co loguje parametry
- **WHEN** `ai_parse_batch` je zavolána s filenames
- **THEN** system prompt obsahuje "STRICT JSON"
- **AND** filenames jsou pøedány jako JSON v user content

### Requirement: PDF Extraction Integration Testing (No-Network)
`extract_pdf_tracklist` MUST be tested end-to-end without network access using mocked `PdfImageRenderer` and `VlmClient`, covering valid responses, empty payloads, and exceptions.

#### Scenario: Valid tracklist extraction
- **GIVEN** mockovanı renderer vrací jeden obrázek
- **AND** mockovanı `VlmClient` vrací validní `{"tracks": [...]}`
- **WHEN** `extract_pdf_tracklist` je zavolána
- **THEN** vrací dict seskupenı podle side
- **AND** poèty záznamù odpovídají

#### Scenario: Empty AI response
- **GIVEN** mockovanı `VlmClient` vrací prázdnı `{}`
- **WHEN** `extract_pdf_tracklist` je zavolána
- **THEN** vrací prázdnı dict `{}`
- **AND** warning log je zaznamenán

#### Scenario: AI exception handling
- **GIVEN** mockovanı `VlmClient` vyhodí vıjimku pøi jedné stránce
- **WHEN** `extract_pdf_tracklist` je zavolána s více stránkami
- **THEN** pøeskoèí chybnou stránku
- **AND** pokraèuje s dalšími stránkami

### Requirement: Parser Robustness Testing
`StrictFilenameParser` and `TracklistParser` MUST include targeted negative tests for conflicting patterns, malformed input, and edge cases, including doctests.

#### Scenario: Conflicting filename patterns
- **GIVEN** filename s konfliktními side patterny (napø. `"Side_A_B1_track.wav"`)
- **WHEN** `StrictFilenameParser.parse` je zavolána
- **THEN** vrací deterministickı vısledek (první match vyhrává)

#### Scenario: Malformed duration handling
- **GIVEN** track data s `duration_formatted="invalid"`
- **WHEN** `TracklistParser.parse` je zavolána
- **THEN** track je pøeskoèen (ne crash)
- **AND** warning log je zaznamenán

#### Scenario: Doctests for parsing logic
- **GIVEN** doctesty definované pøímo v modulu parseru
- **WHEN** doctesty jsou spuštìny
- **THEN** všechny doctesty projdou, ovìøující chování pro konfliktní a negativní pøípady

### Requirement: Comparison Tolerance Edge Cases
`compare_data` MUST be exercised with differences that sit exactly on the warn/fail tolerance boundaries.

#### Scenario: Exact warn tolerance boundary
- **GIVEN** PDF a WAV data s rozdílem pøesnì `warn_tolerance` (2s)
- **WHEN** `compare_data` je zavolána
- **THEN** status je `WARN`

#### Scenario: Exact fail tolerance boundary
- **GIVEN** PDF a WAV data s rozdílem pøesnì `fail_tolerance` (5s)
- **WHEN** `compare_data` je zavolána
- **THEN** status je `FAIL`

#### Scenario: Negative difference handling
- **GIVEN** WAV kratší ne PDF (negativní rozdíl)
- **WHEN** `compare_data` je zavolána
- **THEN** `abs(difference)` se pouívá pro tolerance check

### Requirement: GUI Test Hygiene
GUI tests MUST use the shared `qapp` fixture from `tests/conftest.py` instead of manually instantiating `QApplication`, and MUST drive the event loop explicitly.

#### Scenario: Unified QApplication fixture
- **GIVEN** GUI test potøebující QApplication
- **WHEN** test je definován
- **THEN** pouívá `qapp` fixture jako parametr
- **AND** neobsahuje ruèní `QApplication(sys.argv)`
- **AND** pytest-qt spravuje event loop

#### Scenario: Explicit event loop control
- **GIVEN** GUI test, kterı potøebuje èekat na události
- **WHEN** test je definován
- **THEN** pouívá `qtbot.waitUntil` nebo podobné mechanismy
- **AND** neobsahuje `app.exec()`

### Requirement: Architecture & CI Guard-rails
The project MUST enforce architectural and CI guard-rails to uphold layering, limit complexity, verify invariants, and detect regressions via snapshot tests.

#### Scenario: Layered architecture enforcement
- **GIVEN** kód, kterı porušuje definované architektonické vrstvy (napø. `adapters` importuje `core.domain`)
- **WHEN** architektonické testy jsou spuštìny
- **THEN** testy selou a nahlásí porušení

#### Scenario: Cyclomatic complexity gate
- **GIVEN** funkce s cyklomatickou komplexitou ? 15
- **WHEN** CI krok pro `radon cc` je spuštìn
- **THEN** CI pipeline sele

#### Scenario: Invariant violation detection
- **GIVEN** kód, kterı obsahuje zakázané invarianty (napø. `QApplication(` v testech, `print(` v produkèním kódu)
- **WHEN** CI krok pro grepy invariantù je spuštìn
- **THEN** CI pipeline sele

#### Scenario: Snapshot test for AnalysisStatus
- **GIVEN** `AnalysisStatus` objekt s definovanımi atributy
- **WHEN** snapshot test je spuštìn
- **THEN** serializovanı stav `AnalysisStatus` odpovídá uloenému snapshotu `(name, value, severity, icon_name, color_key)`

#### Scenario: Snapshot test for ResultsTableModel
- **GIVEN** `ResultsTableModel` objekt s definovanımi atributy
- **WHEN** snapshot test je spuštìn
- **THEN** serializovanı stav `ResultsTableModel` odpovídá uloenému snapshotu `(header, renderer_id)`

### Requirement: QSettings Isolation & Resources Build
`QSettings` MUST be isolated during tests and the resource build process MUST fail loudly in CI instead of silently falling back.

#### Scenario: Isolated QSettings in tests
- **GIVEN** test, kterı pouívá `QSettings`
- **WHEN** test je spuštìn
- **THEN** `QSettings` instance je izolovaná pro danı test (session-scoped fixture, per-test files)
- **AND** zmìny v nastavení neovlivòují jiné testy

#### Scenario: Resources build gate in CI
- **GIVEN** chybìjící nebo chybnì zkompilovanı `_icons_rc.py`
- **WHEN** CI krok pro kontrolu resources je spuštìn
- **THEN** CI pipeline sele
- **AND** nedojde k tichému fallbacku na chybìjící resources

### Requirement: Worker Contract & Export Negative I/O
Workers MUST have their public API covered by tests and export routines MUST handle negative I/O scenarios robustly.

#### Scenario: Worker public API contract
- **GIVEN** instance workeru
- **WHEN** jsou volány metody `is_running()`, `state()` nebo je pøipojen slot k signálu `state_changed(WorkerState)`
- **THEN** metody vracejí oèekávané typy (`bool`, `Enum`) a signál je emitován s korektním typem

#### Scenario: Export to non-existent directory
- **GIVEN** exportní operace s cílovım adresáøem, kterı neexistuje
- **WHEN** export je spuštìn
- **THEN** cílovı adresáø je automaticky vytvoøen
- **AND** export probìhne úspìšnì

#### Scenario: Export write error handling
- **GIVEN** exportní operace, kde dojde k `IOError` nebo `PermissionError` pøi zápisu souboru
- **WHEN** export je spuštìn
- **THEN** exportní funkce vyhodí pøíslušnou vıjimku
- **AND** aplikace necrashne
