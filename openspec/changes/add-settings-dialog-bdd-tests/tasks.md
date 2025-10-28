## F-SET1 — BDD smoke & snapshoty
- [ ] 1.1 Vytvoř 	ests/test_settings_dialog_bdd.py (pytest, BDD Given/When/Then).
- [ ] 1.2 Open & defaults: GIVEN qapp + isolated_qsettings → WHEN otevřu SettingsDialog → THEN výchozí hodnoty přes veřejný model.
- [ ] 1.3 Snapshot „schema“: export dict veřejných config hodnot, approval snapshot (vědomý update při změně).

## F-SET2 — Round-trip perzistence
- [ ] 2.1 Změň víc polí (LLM model, auto-export, cesty).
- [ ] 2.2 Ulož (OK/Save).
- [ ] 2.3 QSettings obsahuje změny a po re-open jsou hodnoty identické.

## F-SET3 — Validace & chybové stavy
- [ ] 3.1 Nevalidní/prázdná hodnota → ulož → indikace chyby.
- [ ] 3.2 QSettings zůstane beze změny; dialog necrashne.

## F-SET4 — Signály & veřejný kontrakt
- [ ] 4.1 (Pokud chybí) přidej public getter na hodnoty/model + signál settings_saved(payload).
- [ ] 4.2 QSignalSpy/qtbot.waitSignal: přesně 1× emit s očekávaným payloadem.

## F-SET5 — Kritické přepínače a hrany
- [ ] 5.1 Auto-export toggle: UI→model→persist→re-open.
- [ ] 5.2 Hraniční tolerance (min/max, edge) → round-trip beze změny.

## F-SET6 — CI invariants & hygiena
- [ ] 6.1 Grep: QApplication( == 0, pp.exec( == 0 v 	ests/.
- [ ] 6.2 Všechny UI testy používají qapp/qtbot.
- [ ] 6.3 	ests/README.md: jak spustit BDD UI testy + snapshot update.

## Validation
- [ ] pytest -q tests/test_settings_dialog_bdd.py zelené.
- [ ] Snapshot verify (bez auto-update).
- [ ] Diff-coverage ≥ 85 %.
- [ ] Grep invarianty = 0.

