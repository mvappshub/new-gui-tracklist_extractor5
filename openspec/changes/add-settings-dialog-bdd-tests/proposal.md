## Why
Nastavovací dialog je kritický pro chování aplikace (LLM model, auto-export, cesty, tolerance). Aktuální pokrytí UI je nízké (settings dialog ~20 %), testy nehlídají validaci, perzistenci do QSettings, signály ani změny „schématu“ hodnot. To vede k riziku tichých regresí a falešně zelených buildů.

## What Changes
- **F-SET1 — BDD smoke & snapshoty (SettingsDialog)**
  - BDD testy otevření dialogu (Given/When/Then), kontrola výchozích hodnot přes model (ne jen widgety).
  - Snapshot „schématu“ klíčových hodnot (approval).
- **F-SET2 — Round-trip perzistence do QSettings**
  - Změna několika polí + uložení; opětovné otevření dialogu musí načíst stejné hodnoty; kontrola QSettings.
- **F-SET3 — Validace a chybové stavy**
  - Nevalidní cesta/prázdná hodnota → vizuální indikace, uložení blokováno / hodnoty se nezmění.
- **F-SET4 — Signály a veřejný kontrakt**
  - settings_saved emituje přesně jednou s očekávanými daty.
  - Pokud chybí minimální veřejné API (getter modelu, signál), doplní se tenká vrstva bez změny UX.
- **F-SET5 — Kritické přepínače a hraniční hodnoty**
  - Auto-export on/off, hrany tolerancí apod. – BDD scénáře a round-trip.
- **F-SET6 — CI a invarianty pro UI testy**
  - Zákaz QApplication( a pp.exec() v GUI testech (grep invariants).
  - Povinné použití qapp/qtbot; testy bez vlastního event loopu.

## Impact
Nové BDD testy pro Settings dialog zvýší pokrytí klíčové UI části (cíleně >60 %). Snapshot „schématu“ zabrání tichým rozbitím konfigurace. Validace a signály budou ověřené end-to-end.

