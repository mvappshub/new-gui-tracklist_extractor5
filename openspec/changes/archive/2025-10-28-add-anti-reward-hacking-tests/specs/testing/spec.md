## ADDED Requirements

### Requirement: Mandatory Test Safeguards
The test environment MUST be isolated from external dependencies, especially network access and real API keys, to guarantee deterministic and reliable execution.

#### Scenario: Network access disabled
- **GIVEN** jakýkoli test je spuštěn
- **WHEN** test se pokusí o síťové volání
- **THEN** síťové volání je blokováno (např. `socket.socket` vyhodí chybu)

#### Scenario: AI API keys unset
- **GIVEN** jakýkoli test je spuštěn
- **WHEN** kód se pokusí získat `OPENAI_API_KEY` nebo `OPENROUTER_API_KEY`
- **THEN** klíče jsou `None` nebo prázdné řetězce, což zabraňuje reálným API voláním

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
- **AND** pokračuje s dalšími stránkami

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
- **WHEN** doctesty jsou spuštěny
- **THEN** všechny doctesty projdou, ověřující chování pro konfliktní a negativní případy

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
- **GIVEN** WAV kratší než PDF (negativní rozdíl)
- **WHEN** `compare_data` je zavolána
- **THEN** `abs(difference)` se používá pro tolerance check

### Requirement: GUI Test Hygiene
GUI tests MUST use the shared `qapp` fixture from `tests/conftest.py` instead of manually instantiating `QApplication`, and MUST drive the event loop explicitly.

#### Scenario: Unified QApplication fixture
- **GIVEN** GUI test potřebující QApplication
- **WHEN** test je definován
- **THEN** používá `qapp` fixture jako parametr
- **AND** neobsahuje ruční `QApplication(sys.argv)`
- **AND** pytest-qt spravuje event loop

#### Scenario: Explicit event loop control
- **GIVEN** GUI test, který potřebuje čekat na události
- **WHEN** test je definován
- **THEN** používá `qtbot.waitUntil` nebo podobné mechanismy
- **AND** neobsahuje `app.exec()`

### Requirement: Architecture & CI Guard-rails
The project MUST enforce architectural and CI guard-rails to uphold layering, limit complexity, verify invariants, and detect regressions via snapshot tests.

#### Scenario: Layered architecture enforcement
- **GIVEN** kód, který porušuje definované architektonické vrstvy (např. `adapters` importuje `core.domain`)
- **WHEN** architektonické testy jsou spuštěny
- **THEN** testy selžou a nahlásí porušení

#### Scenario: Cyclomatic complexity gate
- **GIVEN** funkce s cyklomatickou komplexitou ≥ 15
- **WHEN** CI krok pro `radon cc` je spuštěn
- **THEN** CI pipeline selže

#### Scenario: Invariant violation detection
- **GIVEN** kód, který obsahuje zakázané invarianty (např. `QApplication(` v testech, `print(` v produkčním kódu)
- **WHEN** CI krok pro grepy invariantů je spuštěn
- **THEN** CI pipeline selže

#### Scenario: Snapshot test for AnalysisStatus
- **GIVEN** `AnalysisStatus` objekt s definovanými atributy
- **WHEN** snapshot test je spuštěn
- **THEN** serializovaný stav `AnalysisStatus` odpovídá uloženému snapshotu `(name, value, severity, icon_name, color_key)`

#### Scenario: Snapshot test for ResultsTableModel
- **GIVEN** `ResultsTableModel` objekt s definovanými atributy
- **WHEN** snapshot test je spuštěn
- **THEN** serializovaný stav `ResultsTableModel` odpovídá uloženému snapshotu `(header, renderer_id)`

### Requirement: QSettings Isolation & Resources Build
`QSettings` MUST be isolated during tests and the resource build process MUST fail loudly in CI instead of silently falling back.

#### Scenario: Isolated QSettings in tests
- **GIVEN** test, který používá `QSettings`
- **WHEN** test je spuštěn
- **THEN** `QSettings` instance je izolovaná pro daný test (session-scoped fixture, per-test files)
- **AND** změny v nastavení neovlivňují jiné testy

#### Scenario: Resources build gate in CI
- **GIVEN** chybějící nebo chybně zkompilovaný `_icons_rc.py`
- **WHEN** CI krok pro kontrolu resources je spuštěn
- **THEN** CI pipeline selže
- **AND** nedojde k tichému fallbacku na chybějící resources

### Requirement: Worker Contract & Export Negative I/O
Workers MUST have their public API covered by tests and export routines MUST handle negative I/O scenarios robustly.

#### Scenario: Worker public API contract
- **GIVEN** instance workeru
- **WHEN** jsou volány metody `is_running()`, `state()` nebo je připojen slot k signálu `state_changed(WorkerState)`
- **THEN** metody vracejí očekávané typy (`bool`, `Enum`) a signál je emitován s korektním typem

#### Scenario: Export to non-existent directory
- **GIVEN** exportní operace s cílovým adresářem, který neexistuje
- **WHEN** export je spuštěn
- **THEN** cílový adresář je automaticky vytvořen
- **AND** export proběhne úspěšně

#### Scenario: Export write error handling
- **GIVEN** exportní operace, kde dojde k `IOError` nebo `PermissionError` při zápisu souboru
- **WHEN** export je spuštěn
- **THEN** exportní funkce vyhodí příslušnou výjimku
- **AND** aplikace necrashne
