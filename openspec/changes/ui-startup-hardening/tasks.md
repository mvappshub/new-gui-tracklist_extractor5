## Tasks

- [ ] F-UIH1: Startup/DI smoke (headless) – tests/test_startup_smoke.py
- [ ] F-UIH2: PDF Viewer BDD – tests/test_pdf_viewer_bdd.py (valid/invalid/empty PDF, next/prev/first/last, caplog WARN/ERROR)
- [ ] F-UIH3: Theme & Delegates – tests/test_theme_and_delegates.py (Display/Decoration/ToolTip/Foreground, fallbacky, HiDPI)
- [ ] F-UIH4: ResultsTableModel roles – tests/test_results_table_model_roles.py (parametrizace sloupce×role)
- [ ] F-UIH4: TracksTableModel roles – tests/test_tracks_table_model_roles.py (parametrizace sloupce×role)
- [ ] F-UIH5: Unicode v UI – tests/test_ui_unicode.py (diakritika/emoji v názvech souborů/tracků)
- [ ] F-UIH6: Logging assertions – rozšířit caplog aserty v negativních cestách (pdf_extractor, AI fallback)
- [ ] F-UIH7: CI per-module coverage gate – ui/dialogs/settings_dialog.py ≥ 60 %
- [ ] F-UIH7: CI per-module coverage gate – ui/main_window.py ≥ 40 %
- [ ] F-UIH7: CI per-module coverage gate – ui/models/*.py ≥ 70 %

## Validation

- [ ] pytest zelené (role-tests a PDF viewer BDD)
- [ ] Per-module coverage prahy splněny
- [ ] Žádné GUI testy nepoužívají QApplication/app.exec()
