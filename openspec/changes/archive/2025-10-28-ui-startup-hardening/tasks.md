## Tasks

- [x] F-UIH1: Startup/DI smoke (headless) – tests/test_startup_smoke.py
- [x] F-UIH2: PDF Viewer BDD – tests/test_pdf_viewer_bdd.py (valid/invalid/empty PDF, next/prev/first/last, caplog WARN/ERROR)
- [x] F-UIH3: Theme & Delegates – tests/test_theme_and_delegates.py (Display/Decoration/ToolTip/Foreground, fallbacky, HiDPI)
- [x] F-UIH4: ResultsTableModel roles – tests/test_results_table_model_roles.py (parametrizace sloupce×role)
- [x] F-UIH4: TracksTableModel roles – tests/test_tracks_table_model_roles.py (parametrizace sloupce×role)
- [x] F-UIH5: Unicode v UI – tests/test_ui_unicode.py (diakritika/emoji v názvech souborů/tracků)
- [x] F-UIH6: Logging assertions – rozšířit caplog aserty v negativních cestách (pdf_extractor, AI fallback)
- [x] F-UIH7: CI per-module coverage gate – ui/dialogs/settings_dialog.py ≥ 60 %
- [x] F-UIH7: CI per-module coverage gate – ui/main_window.py ≥ 40 %
- [x] F-UIH7: CI per-module coverage gate – ui/models/*.py ≥ 70 %

## Validation

- [x] pytest zelené (role-tests a PDF viewer BDD)
- [x] Per-module coverage prahy splněny
- [x] Žádné GUI testy nepoužívají QApplication/app.exec()
