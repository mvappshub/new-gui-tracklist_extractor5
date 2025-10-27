# Kilo-Code Prompty pro UI/UX Vylepšení

Tento adresář obsahuje série promptů pro implementaci UI/UX vylepšení identifikovaných v kritickém auditu aplikace "Final Cue Sheet Checker".

## Struktura

Každá OpenSpec změna má tři prompty odpovídající workflow fázím:

1. `*-01-proposal.md` - **Proposal fáze**: Vytvoření OpenSpec návrhu (scaffold)
2. `*-02-apply.md` - **Apply fáze**: Implementace změn v kódu
3. `*-03-archive.md` - **Archive fáze**: Archivace po dokončení

## Změna 1: fix-ui-critical-symbols (P0 - Kritické)

### Problém
UI zobrazuje nesprávné symboly (černé šipky ►) v klíčových sloupcích:
- **Match sloupec**: Místo ✓/✗ se zobrazují šipky
- **Waveform sloupec**: Místo play ikony se zobrazuje šipka

### Příčina
- Font fallback (Poppins není fyzicky přítomen, pouze DejaVu fonty)
- Windows systémová ikona `SP_MediaPlay` se renderuje jako šipka

### Řešení
Zavedení vlastní ikonové infrastruktury s SVG ikonami pro konzistentní renderování napříč platformami.

### Prompty
- `fix-ui-critical-symbols-01-proposal.md` - Scaffold OpenSpec návrhu + vytvoření SVG ikon
- `fix-ui-critical-symbols-02-apply.md` - Implementace `get_custom_icon()` a úprava modelů
- `fix-ui-critical-symbols-03-archive.md` - Archivace a aktualizace master spec

## Změna 2: refine-ui-layout-and-consistency (P1 - Střední)

*Připraveno po dokončení změny 1*

### Problémy
- Inkonzistentní odsazení v toolbaru (nulové margins)
- Nízký kontrast total řádku (nesplňuje WCAG 4.5:1)
- Nekonzistentní branding progress baru

### Řešení
- Úprava toolbar margins a spacing
- Explicitní barva pro total řádek s vysokým kontrastem
- Vylepšení QSS stylů pro progress bar

## Použití

### Krok 1: Otevřít prompt
```bash
# V Kilo-Code nebo textovém editoru
code .kilocode/prompts/fix-ui-critical-symbols-01-proposal.md
```

### Krok 2: Zkopírovat obsah
Zkopírovat celý obsah promptu do chat okna Kilo-Code.

### Krok 3: Spustit příkazy
Spustit všechny příkazy v uvedeném pořadí. Prompt obsahuje:
- `mkdir` příkazy pro vytvoření struktury
- `cat` příkazy s heredoc syntaxí pro vytvoření souborů
- `openspec` příkazy pro validaci
- `git` příkazy pro verzování

### Krok 4: Ověřit výstupy
Každý prompt obsahuje sekci "Očekávaný výstup" s verifikačními kroky.

### Krok 5: Pokračovat dalším promptem
Po úspěšném dokončení jednoho promptu pokračovat dalším v sérii.

## Workflow

```
Proposal (scaffold) → Apply (implement) → Archive (finalize) → Next Change
```

## Důležité poznámky

### Git Commits
Každý prompt končí git commitem. Commit messages následují Conventional Commits:
- `feat(openspec):` - Nový OpenSpec návrh
- `feat(ui):` - Implementace UI změn
- `chore(openspec):` - Archivace změny

### OpenSpec Validace
Všechny změny jsou validovány pomocí `openspec validate --strict` před commitem.

### Testování
Po apply fázi spustit testy:
```bash
pytest tests/test_tracks_table_model.py -v
```

### Rollback
Pokud něco selže, použít git reset:
```bash
git reset --hard HEAD~1  # Vrátit poslední commit
```

## Kontakt

Pro otázky nebo problémy viz `openspec/AGENTS.md` nebo `openspec/project.md`.