## 0. F-PRE0: Mandatory Test Safeguards
- [ ] 0.0.1 **Automatické verzování:** Commit a push aktuálního stavu kódu s popisem "Pre-F-PRE0: Stabilní stav před implementací anti-reward-hacking testů."
- [x] 0.1 Vytvořit `tests/conftest.py` fixture `disable_network_access` (autouse, session scope) pro blokování síťových volání (např. `socket.socket`).
- [x] 0.2 Vytvořit `tests/conftest.py` fixture `unset_ai_api_keys` (autouse, session scope) pro nastavení `OPENAI_API_KEY=None` a `OPENROUTER_API_KEY=None` v testovacím prostředí.

## 1. F-PRE1: VlmClient Contract Tests
- [ ] 1.1 Vytvořit `tests/test_ai_contracts.py` s pytest strukturou.
- [ ] 1.2 Test `test_to_data_url_encoding`: vytvořit 1×1 PNG pomocí `PIL.Image`, zavolat `VlmClient._to_data_url()`, ověřit prefix `data:image/png;base64,` a decodovatelnost base64.
- [ ] 1.3 Test `test_get_json_response_message_format`: monkeypatchovat `OpenAI.chat.completions.create` aby zachytil parametry, ověřit `model`, `messages` strukturu (role/content s image_url), `response_format={"type": "json_object"}`, **MUST ověřit `temperature=0.0`**.
- [ ] 1.4 Test `test_get_json_response_empty_content`: mockovat response s `content=None`, ověřit `ValueError("AI returned an empty response.")`.
- [ ] 1.5 Test `test_get_json_response_backtick_wrapped`: mockovat response s `content="```json\n{...}\n```"`, ověřit že stripování backticků funguje a `json.loads` uspěje.
- [ ] 1.6 Test `test_get_json_response_no_api_key`: nastavit `OPENROUTER_API_KEY=None`, ověřit že `get_json_response` vrací prázdný dict `{}`.

## 2. F-PRE2: ai_helpers Contract Tests
- [ ] 2.1 Přidat testy do `tests/test_ai_contracts.py`.
- [ ] 2.2 Test `test_ai_parse_batch_request_format`: patchnout `_load_ai_client` aby vrátil fake klient s `create(...)` co loguje parametry, ověřit system prompt ("STRICT JSON"), messages strukturu, že filenames jdou jako **JSON v user content**.
- [ ] 2.3 Test `test_ai_parse_batch_valid_response`: mockovat validní JSON mapu `{"file.wav": {"side": "A", "position": 1}}`, ověřit korektní dict `{"file.wav": ("A", 1)}`.
- [ ] 2.4 Test `test_ai_parse_batch_empty_response`: mockovat prázdný JSON `{}`, ověřit prázdný dict bez výjimky.
- [ ] 2.5 Test `test_ai_parse_batch_invalid_json`: mockovat malformed JSON, ověřit prázdný dict (graceful fallback).
- [ ] 2.6 Test `test_ai_parse_batch_empty_filenames`: zavolat s `filenames=[]`, ověřit prázdný dict (časné ukončení).
- [ ] 2.7 Test `test_merge_ai_results_side_position_update`: vytvořit `WavInfo` s `side=None, position=None`, zavolat `merge_ai_results` s AI mapou, ověřit že `side` a `position` jsou nastaveny.

## 3. F-PRE3: PDF Extractor Integration Tests
- [ ] 3.1 Vytvořit `tests/test_pdf_extractor_contract.py`.
- [ ] 3.2 Test `test_extract_pdf_tracklist_valid_response`: mockovat `PdfImageRenderer.render` aby vrátil jeden `PIL.Image`, mockovat `VlmClient.get_json_response` s validním `{"tracks": [{"title": "Track 1", "side": "A", "position": 1, "duration_formatted": "3:45"}]}`, zavolat `extract_pdf_tracklist`, ověřit seskupení podle side a počty záznamů.
- [ ] 3.3 Test `test_extract_pdf_tracklist_empty_response`: mockovat `VlmClient.get_json_response` s prázdným `{}`, ověřit že vrací `{}` s warning logem.
- [ ] 3.4 Test `test_extract_pdf_tracklist_no_pages`: mockovat `PdfImageRenderer.render` aby vrátil prázdný list, ověřit že vrací `{}` s warning logem.
- [ ] 3.5 Test `test_extract_pdf_tracklist_ai_exception`: mockovat `VlmClient.get_json_response` aby vyhodil výjimku při jedné stránce, ověřit že přeskočí stránku a pokračuje (nebo vrací `{}` pokud všechny selžou).
- [ ] 3.6 Test `test_extract_pdf_tracklist_multiple_pages`: mockovat renderer s 2 stránkami, každá vrací jiné tracky, ověřit že `all_raw_tracks` agreguje všechny.

## 4. F-PRE4: Parser/Comparison Sanity Tests
- [ ] 4.1 Vytvořit `tests/test_parser_sanity.py`.
- [ ] 4.2 Test `test_strict_filename_parser_conflicting_patterns`: testovat filenames jako `"Side_A_B1_track.wav"` (konfliktní side), `"AA01BB02.wav"` (multiple matches), ověřit deterministické chování (první match vyhrává).
- [ ] 4.3 Test `test_strict_filename_parser_negative_cases`: testovat `"no_side_info.wav"`, `"random123.wav"`, ověřit že vrací `ParsedFileInfo(side=None, position=None)`.
- [ ] 4.4 Test `test_compare_data_tolerance_edge_cases`: vytvořit `pdf_data` a `wav_data` s rozdílem přesně `warn_tolerance` (2s), ověřit status `WARN`; rozdíl přesně `fail_tolerance` (5s), ověřit status `FAIL`; rozdíl `warn_tolerance - 0.1`, ověřit status `OK`.
- [ ] 4.5 Test `test_compare_data_negative_difference`: testovat kdy WAV je kratší než PDF (negativní rozdíl), ověřit že `abs(difference)` se používá pro tolerance check.
- [ ] 4.6 Test `test_tracklist_parser_malformed_duration`: testovat `duration_formatted` jako `"invalid"`, `"99:99"`, `""`, ověřit že tracky jsou přeskočeny (ne crash).
- [ ] 4.7 Přidat doctesty do `core/domain/parsing.py` pro `StrictFilenameParser` a `TracklistParser` pokrývající konfliktní patterny a malformed input.

## 5. F-PRE5: GUI Test Hygiena
- [ ] 5.1 Otevřít `tests/test_gui_simple.py`.
- [ ] 5.2 Odstranit ruční `QApplication(sys.argv)` z `test_basic_gui`.
- [ ] 5.3 Přidat `qapp` fixture jako parametr: `def test_basic_gui(qapp):`.
- [ ] 5.4 Odstranit `return app.exec()` (pytest-qt spravuje event loop).
- [ ] 5.5 Použít `qtbot` fixture pro interakci s widgety (pokud potřeba): `def test_basic_gui(qapp, qtbot):`.
- [ ] 5.6 Ověřit že test stále projde s `pytest tests/test_gui_simple.py`.

## 6. F-PRE6: Architecture & CI Guard-rails
- [ ] 6.1 Vytvořit `tests/test_architecture.py` pro ověření architektonických vrstev pomocí `pytest-arch`.
- [ ] 6.2 Konfigurovat `import-linter` pro vynucení architektonických pravidel (např. `adapters` nesmí importovat `core.domain`).
- [ ] 6.3 Implementovat CI krok pro `radon cc` s prahovou hodnotou **FAIL ≥ 15 per-function** a **WARN > 10**.
- [ ] 6.4 Vytvořit CI krok pro grepy klíčových invariantů: `QApplication(`, `qapp.exec(`, `print(` v testech, `from .* import _privát`, `SYMBOL_` v `ui/` – ověřit **0 nálezů**.
- [ ] 6.5 Vytvořit `tests/snapshots/test_analysis_status_snapshot.py` pro snapshot testování `AnalysisStatus` (obsah: `(name, value, severity, icon_name, color_key)`).
- [ ] 6.6 Vytvořit `tests/snapshots/test_results_table_model_snapshot.py` pro snapshot testování `ResultsTableModel` (obsah: `(header, renderer_id)`).

## 7. F-PRE7: GUI Tests Unify (no event loop)
- [ ] 7.1 Pro všechny GUI testy, které dříve používaly `app.exec()`, nahradit volání za `qtbot.waitUntil(lambda: condition, timeout=...)` nebo podobné mechanismy z `pytest-qt` pro explicitní řízení event loopu a čekání na stavy.
- [ ] 7.2 Ověřit, že žádný GUI test neobsahuje `app.exec()` nebo `QApplication(sys.argv)`.

## 8. F-PRE8: QSettings Isolation & Resources Build
- [ ] 8.1 Vytvořit `tests/conftest.py` fixture `isolated_qsettings` (session-scoped) pro poskytování izolovaných `QSettings` instancí pro každý test, s použitím dočasných souborů.
- [ ] 8.2 Zajistit, že všechny testy používající `QSettings` přebírají tuto fixture.
- [ ] 8.3 Implementovat CI krok, který ověří existenci a správnou kompilaci `_icons_rc.py` a zabrání tichému fallbacku na chybějící resources.

## 9. F-PRE9: Worker Contract & Export Negative I/O
- [ ] 9.1 Vytvořit `tests/test_worker_contracts.py` pro testování veřejného API workeru (`is_running() -> bool`, `state() -> Enum(IDLE,RUNNING,FINISHED,FAILED)`, signál `state_changed(WorkerState)`).
- [ ] 9.2 Test `test_export_missing_directory`: zavolat export s neexistujícím cílovým adresářem, ověřit, že adresář je vytvořen.
- [ ] 9.3 Test `test_export_write_error`: mockovat `open()` nebo `shutil.copy()` tak, aby vyhodily `IOError` nebo `PermissionError` během exportu, ověřit, že export vyhodí příslušnou výjimku a necrashne.
- [ ] 9.4 **Automatické verzování:** Po úspěšném dokončení a ověření všech testů pro F-PRE0 až F-PRE9, commit a push s popisem "Post-F-PRE9: Všechny anti-reward-hacking testy implementovány a ověřeny."

## 6. Testing Strategy Spec
- [ ] 6.1 Vytvořit `openspec/changes/add-anti-reward-hacking-tests/specs/testing/spec.md`.
- [ ] 6.2 Dokumentovat anti-reward-hacking principy (contract testy, wire-format ověření, negativní scénáře, mutation-like sanity).
- [ ] 6.3 Definovat requirements pro AI adapter testing, PDF extraction testing, parser robustness, GUI test hygiene, architektonické guard-rails, QSettings/resources a worker/export testování.

## 7. Validation & Documentation
- [ ] 7.1 Spustit `pytest tests/test_ai_contracts.py tests/test_pdf_extractor_contract.py tests/test_parser_sanity.py tests/test_gui_simple.py tests/test_architecture.py tests/test_worker_contracts.py tests/snapshots/test_analysis_status_snapshot.py tests/snapshots/test_results_table_model_snapshot.py` a ověřit že všechny testy projdou.
- [ ] 7.2 Spustit `openspec validate add-anti-reward-hacking-tests --strict` a opravit případné chyby.
- [ ] 7.3 Aktualizovat `tests/README.md` s odkazem na nové contract/sanity testy a vysvětlením nových kategorií testů.
- [ ] 7.4 Požádat o review proposal před implementací.
- [ ] 7.5 Implementovat CI kroky v pořadí "fail-fast":
    - [ ] Invarianty grepy (0 nálezů)
    - [ ] Kontrola resources (`_icons_rc.py` kompilace)
    - [ ] Radon (komplexita: FAIL ≥ 15 per-function, WARN > 10)
    - [ ] Doctesty (všechny projdou)
    - [ ] Unit testy + coverage (celková coverage)
    - [ ] Diff-coverage (≥ 85 % na změněném kódu)
    - [ ] Snapshot verify (ověření, že snapshoty odpovídají, bez automatického update).
- [ ] 7.6 Dokumentovat, že aktualizace snapshotů vyžaduje vědomý zásah v PR (např. `pytest --snapshot-update`).
