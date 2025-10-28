## F-IOEC1 — FS hrany
- [ ] 1.1 	ests/test_file_discovery_fs_edges.py:
  - Unicode/diakritika v cestách → správná detekce párů
  - hidden/system files → ignorovat (nebo jasná policy)
  - \\?\ long-path (Windows) → bez crash
  - duplicitní basenames v ZIP → deterministické chování
- [ ] 1.2 	ests/test_export_fs_edges.py: read-only cíle → srozumitelná výjimka + log, žádný poloviční soubor

## F-IOEC2 — Lock/permission
- [ ] 2.1 Locked file (WinError 5/32) → export selže s výjimkou; caplog ERROR
- [ ] 2.2 Po selhání neexistuje částečný výstup

## F-IOEC3 — WAV korupce
- [ ] 3.1 	ests/test_wav_reader_corruption.py:
  - poškozený WAV (invalid RIFF/data chunk)
  - poškozený ZIP (CRC fail)
  - kontrakt: skip+warn (preferováno) nebo jednotná výjimka
- [ ] 3.2 Zruš xfail a uprav kód/testy na jasný PASS/FAIL

## F-IOEC4 — Config migrace
- [ ] 4.1 	ests/test_config_migrations.py:
  - chybějící klíč → default
  - neznámý klíč → ignorovat s WARN
  - změna typu → konverze nebo jasný error s logem
  - atomický zápis (temp→rename) a rollback při chybě

## F-IOEC5 — Worker lifecycle
- [ ] 5.1 	ests/test_worker_lifecycle.py:
  - double-start → druhý start se odmítne / hlásí RUNNING
  - start→cancel→start → žádné zombie vlákno, konzistentní state()
  - zavření okna během běhu → korektní ukončení, žádné pozdní signály

## F-IOEC6 — TMP cleanup
- [ ] 6.1 CI: pytest --basetemp=.pytest_tmp
- [ ] 6.2 	ests/test_tmp_cleanup.py:
  - simulace locked temp souboru → WARN + pokračování
  - po testu dočasné adresáře uklizené

## Validation
- [ ] pytest -q zelené
- [ ] caplog aserty pokrývají ERROR/WARN cesty
- [ ] diff-coverage ≥ 85 %
- [ ] Windows job v CI (matrix)
