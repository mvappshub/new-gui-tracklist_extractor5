## Why
Chybí testy a zábradlí pro start aplikace (DI/wiring), PDF Viewer, theme/delegates rendering, role-driven chování tabulkových modelů, lokalizace/Unicode v UI, logging aserty a modulové coverage prahy. To jsou místa, kde refaktor snadno zavede tiché regresní chyby.

## What Changes
- **F-UIH1 — Startup/DI smoke test (headless)**
- **F-UIH2 — PDF Viewer BDD**
- **F-UIH3 — Theme & Delegates rendering**
- **F-UIH4 — Table models role tests (Results/Tracks)**
- **F-UIH5 — Lokalizace/Unicode v UI a datech**
- **F-UIH6 — Logging/Observability assertions**
- **F-UIH7 — Modulové coverage prahy (CI)**

## Impact
Start aplikace a klíčové UI chování budou chráněné. Regrese v renderování/sloupcích/rolích nebo v PDF vieweru vyletí hned v CI. Lokalizace a log aserty sníží „tiše zelené“ pády.
