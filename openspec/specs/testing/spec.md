# testing Specification

## Purpose
Ensures anti-reward-hacking test coverage across AI adapters, PDF extraction, parser tolerance, GUI hygiene, architecture guard-rails, QSettings isolation, and worker/export flows.

## Requirements
### Requirement: Mandatory Test Safeguards
The test environment MUST be isolated from external dependencies, especially network access and real API keys, to guarantee deterministic and reliable execution.

#### Scenario: Network access disabled
- **GIVEN** jak�koli test je spu�t�n
- **WHEN** test se pokus� o s�ov� vol�n�
- **THEN** s�ov� vol�n� je blokov�no (nap�. `socket.socket` vyhod� chybu)

#### Scenario: AI API keys unset
- **GIVEN** jak�koli test je spu�t�n
- **WHEN** k�d se pokus� z�skat `OPENAI_API_KEY` nebo `OPENROUTER_API_KEY`
- **THEN** kl��e jsou `None` nebo pr�zdn� �et�zce, co� zabra�uje re�ln�m API vol�n�m

### Requirement: AI Adapter Contract Testing
AI adapters (`VlmClient`, `ai_helpers`) MUST be verified with contract tests that cover real wire-format structures (messages, `response_format`, image encoding) without calling live APIs.

#### Scenario: VlmClient message format verification
- **GIVEN** `VlmClient` instance s mockovan�m OpenAI klientem
- **WHEN** `get_json_response` je zavol�na s promptem a obr�zky
- **THEN** mockovan� klient zachyt� parametry vol�n�
- **AND** `model`, `messages` (role/content s image_url), `response_format={"type": "json_object"}`, `temperature=0.0` jsou ov��eny

#### Scenario: VlmClient image encoding
- **GIVEN** 1�1 PNG obr�zek vytvo�en� pomoc� PIL
- **WHEN** `_to_data_url` je zavol�na
- **THEN** n�vrat za��n� `data:image/png;base64,`
- **AND** base64 ��st je dek�dovateln�

#### Scenario: VlmClient error handling
- **GIVEN** mockovan� response s `content=None`
- **WHEN** `get_json_response` je zavol�na
- **THEN** vyhod� `ValueError("AI returned an empty response.")`

#### Scenario: ai_parse_batch request format
- **GIVEN** fake OpenAI klient co loguje parametry
- **WHEN** `ai_parse_batch` je zavol�na s filenames
- **THEN** system prompt obsahuje "STRICT JSON"
- **AND** filenames jsou p�ed�ny jako JSON v user content

### Requirement: PDF Extraction Integration Testing (No-Network)
`extract_pdf_tracklist` MUST be tested end-to-end without network access using mocked `PdfImageRenderer` and `VlmClient`, covering valid responses, empty payloads, and exceptions.

#### Scenario: Valid tracklist extraction
- **GIVEN** mockovan� renderer vrac� jeden obr�zek
- **AND** mockovan� `VlmClient` vrac� validn� `{"tracks": [...]}`
- **WHEN** `extract_pdf_tracklist` je zavol�na
- **THEN** vrac� dict seskupen� podle side
- **AND** po�ty z�znam� odpov�daj�

#### Scenario: Empty AI response
- **GIVEN** mockovan� `VlmClient` vrac� pr�zdn� `{}`
- **WHEN** `extract_pdf_tracklist` je zavol�na
- **THEN** vrac� pr�zdn� dict `{}`
- **AND** warning log je zaznamen�n

#### Scenario: AI exception handling
- **GIVEN** mockovan� `VlmClient` vyhod� v�jimku p�i jedn� str�nce
- **WHEN** `extract_pdf_tracklist` je zavol�na s v�ce str�nkami
- **THEN** p�esko�� chybnou str�nku
- **AND** pokra�uje s dal��mi str�nkami

### Requirement: Parser Robustness Testing
`StrictFilenameParser` and `TracklistParser` MUST include targeted negative tests for conflicting patterns, malformed input, and edge cases, including doctests.

#### Scenario: Conflicting filename patterns
- **GIVEN** filename s konfliktn�mi side patterny (nap�. `"Side_A_B1_track.wav"`)
- **WHEN** `StrictFilenameParser.parse` je zavol�na
- **THEN** vrac� deterministick� v�sledek (prvn� match vyhr�v�)

#### Scenario: Malformed duration handling
- **GIVEN** track data s `duration_formatted="invalid"`
- **WHEN** `TracklistParser.parse` je zavol�na
- **THEN** track je p�esko�en (ne crash)
- **AND** warning log je zaznamen�n

#### Scenario: Doctests for parsing logic
- **GIVEN** doctesty definovan� p��mo v modulu parseru
- **WHEN** doctesty jsou spu�t�ny
- **THEN** v�echny doctesty projdou, ov��uj�c� chov�n� pro konfliktn� a negativn� p��pady

### Requirement: Comparison Tolerance Edge Cases
`compare_data` MUST be exercised with differences that sit exactly on the warn/fail tolerance boundaries.

#### Scenario: Exact warn tolerance boundary
- **GIVEN** PDF a WAV data s rozd�lem p�esn� `warn_tolerance` (2s)
- **WHEN** `compare_data` je zavol�na
- **THEN** status je `WARN`

#### Scenario: Exact fail tolerance boundary
- **GIVEN** PDF a WAV data s rozd�lem p�esn� `fail_tolerance` (5s)
- **WHEN** `compare_data` je zavol�na
- **THEN** status je `FAIL`

#### Scenario: Negative difference handling
- **GIVEN** WAV krat�� ne� PDF (negativn� rozd�l)
- **WHEN** `compare_data` je zavol�na
- **THEN** `abs(difference)` se pou��v� pro tolerance check

### Requirement: GUI Test Hygiene
GUI tests MUST use the shared `qapp` fixture from `tests/conftest.py` instead of manually instantiating `QApplication`, and MUST drive the event loop explicitly.

#### Scenario: Unified QApplication fixture
- **GIVEN** GUI test pot�ebuj�c� QApplication
- **WHEN** test je definov�n
- **THEN** pou��v� `qapp` fixture jako parametr
- **AND** neobsahuje ru�n� `QApplication(sys.argv)`
- **AND** pytest-qt spravuje event loop

#### Scenario: Explicit event loop control
- **GIVEN** GUI test, kter� pot�ebuje �ekat na ud�losti
- **WHEN** test je definov�n
- **THEN** pou��v� `qtbot.waitUntil` nebo podobn� mechanismy
- **AND** neobsahuje `app.exec()`

### Requirement: Architecture & CI Guard-rails
The project MUST enforce architectural and CI guard-rails to uphold layering, limit complexity, verify invariants, and detect regressions via snapshot tests.

#### Scenario: Layered architecture enforcement
- **GIVEN** k�d, kter� poru�uje definovan� architektonick� vrstvy (nap�. `adapters` importuje `core.domain`)
- **WHEN** architektonick� testy jsou spu�t�ny
- **THEN** testy sel�ou a nahl�s� poru�en�

#### Scenario: Cyclomatic complexity gate
- **GIVEN** funkce s cyklomatickou komplexitou ? 15
- **WHEN** CI krok pro `radon cc` je spu�t�n
- **THEN** CI pipeline sel�e

#### Scenario: Invariant violation detection
- **GIVEN** k�d, kter� obsahuje zak�zan� invarianty (nap�. `QApplication(` v testech, `print(` v produk�n�m k�du)
- **WHEN** CI krok pro grepy invariant� je spu�t�n
- **THEN** CI pipeline sel�e

#### Scenario: Snapshot test for AnalysisStatus
- **GIVEN** `AnalysisStatus` objekt s definovan�mi atributy
- **WHEN** snapshot test je spu�t�n
- **THEN** serializovan� stav `AnalysisStatus` odpov�d� ulo�en�mu snapshotu `(name, value, severity, icon_name, color_key)`

#### Scenario: Snapshot test for ResultsTableModel
- **GIVEN** `ResultsTableModel` objekt s definovan�mi atributy
- **WHEN** snapshot test je spu�t�n
- **THEN** serializovan� stav `ResultsTableModel` odpov�d� ulo�en�mu snapshotu `(header, renderer_id)`

### Requirement: QSettings Isolation & Resources Build
`QSettings` MUST be isolated during tests and the resource build process MUST fail loudly in CI instead of silently falling back.

#### Scenario: Isolated QSettings in tests
- **GIVEN** test, kter� pou��v� `QSettings`
- **WHEN** test je spu�t�n
- **THEN** `QSettings` instance je izolovan� pro dan� test (session-scoped fixture, per-test files)
- **AND** zm�ny v nastaven� neovliv�uj� jin� testy

#### Scenario: Resources build gate in CI
- **GIVEN** chyb�j�c� nebo chybn� zkompilovan� `_icons_rc.py`
- **WHEN** CI krok pro kontrolu resources je spu�t�n
- **THEN** CI pipeline sel�e
- **AND** nedojde k tich�mu fallbacku na chyb�j�c� resources

### Requirement: Worker Contract & Export Negative I/O
Workers MUST have their public API covered by tests and export routines MUST handle negative I/O scenarios robustly.

#### Scenario: Worker public API contract
- **GIVEN** instance workeru
- **WHEN** jsou vol�ny metody `is_running()`, `state()` nebo je p�ipojen slot k sign�lu `state_changed(WorkerState)`
- **THEN** metody vracej� o�ek�van� typy (`bool`, `Enum`) a sign�l je emitov�n s korektn�m typem

#### Scenario: Export to non-existent directory
- **GIVEN** exportn� operace s c�lov�m adres��em, kter� neexistuje
- **WHEN** export je spu�t�n
- **THEN** c�lov� adres�� je automaticky vytvo�en
- **AND** export prob�hne �sp�n�

#### Scenario: Export write error handling
- **GIVEN** exportn� operace, kde dojde k `IOError` nebo `PermissionError` p�i z�pisu souboru
- **WHEN** export je spu�t�n
- **THEN** exportn� funkce vyhod� p��slu�nou v�jimku
- **AND** aplikace necrashne
