## Why
Souborový systém (Windows hrany, diakritika, long paths), exportní I/O (read-only cíle, locked files), WAV korupce/XFAILy, migrace a zpětná kompatibilita configu, worker závody a cleanup tempů/handle jsou stále rizikové.

## What Changes
- **F-IOEC1 — FS hrany: Windows/Unicode/long-path**
- **F-IOEC2 — Export locked/permission errors**
- **F-IOEC3 — WAV korupce: od-XFAIL-ovat s jasným kontraktem**
- **F-IOEC4 — Config migrace & kompatibilita**
- **F-IOEC5 — Worker concurrency & lifecycle**
- **F-IOEC6 — TMP cleanup & --basetemp v CI**

## Impact
Stabilnější práce s FS (zejména Windows), jasné chování při chybách WAV, předvídatelná konfigurace i při změnách, méně flaků kvůli handle/cleanup.
