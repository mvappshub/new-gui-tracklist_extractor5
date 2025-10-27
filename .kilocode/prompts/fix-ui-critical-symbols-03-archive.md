References:

- openspec\\AGENTS.md

# Kilo-Code Prompt: fix-ui-critical-symbols (Fáze 3: Archive)

## Kontext

Implementace změny `fix-ui-critical-symbols` je dokončena a otestována. Všechny úkoly v `tasks.md` jsou označeny jako hotové (✓). Nyní archivujeme změnu a aktualizujeme master spec.

**Co už máme:**
- ✅ OpenSpec proposal (proposal.md, tasks.md, spec.md)
- ✅ SVG ikony (check.svg, cross.svg, play.svg)
- ✅ Implementaci `get_custom_icon()` v `ui/theme.py`
- ✅ Upravený `TracksTableModel` s ikonami
- ✅ Aktualizované testy
- ✅ Všechny testy procházejí

**Co budeme dělat:**
- Archivovat změnu pomocí `openspec archive`
- Aktualizovat master spec `openspec/specs/ui/spec.md`
- Vytvořit finální git commit

## Cíl

Archivovat změnu `fix-ui-critical-symbols` a aktualizovat master spec, aby odrážel nové požadavky na Custom Iconography.

## Kroky

### 1. Archivace změny

```bash
openspec archive fix-ui-critical-symbols --yes
```

**Co tento příkaz udělá:**
1. Přesune `openspec/changes/fix-ui-critical-symbols/` do `openspec/changes/archive/2025-10-22-fix-ui-critical-symbols/`
2. Aplikuje delta spec do `openspec/specs/ui/spec.md` (přidá ADDED Requirements)
3. Validuje výsledný stav
4. Vytvoří backup před změnami

**Očekávaný výstup:**
```
✓ Archiving change 'fix-ui-critical-symbols'
✓ Moving to archive/2025-10-22-fix-ui-critical-symbols/
✓ Applying deltas to specs/ui/spec.md
✓ Added 1 requirement(s)
✓ Validation passed
✓ Archive complete
```

### 2. Manuální verifikace (pokud openspec archive selže)

Pokud příkaz `openspec archive` selže nebo není dostupný, proveďte manuální archivaci:

#### 2.1 Přesunout změnu do archive

```bash
mkdir -p openspec/changes/archive
mv openspec/changes/fix-ui-critical-symbols openspec/changes/archive/2025-10-22-fix-ui-critical-symbols
```

#### 2.2 Aktualizovat master spec

Přidat nové Requirements do `openspec/specs/ui/spec.md`:

```bash
# Otevřít soubor v editoru a přidat na konec:
cat >> openspec/specs/ui/spec.md << 'EOF'

### Requirement: Custom Iconography
The application SHALL use custom SVG icons for key status indicators and actions to ensure visual consistency, brand alignment, and cross-platform compatibility.

#### Scenario: Consistent Match symbols
- **WHEN** the tracks table is displayed
- **THEN** the "Match" column (column 6) SHALL render a custom green SVG checkmark icon for successful matches
- **AND** SHALL render a custom red SVG cross icon for failed matches
- **AND** SHALL NOT display text symbols like '✓', '✗', or arrows
- **AND** the icons SHALL be loaded from `assets/icons/check.svg` and `assets/icons/cross.svg`

#### Scenario: Consistent Waveform action icon
- **WHEN** the tracks table is displayed
- **THEN** the "Waveform" column (column 7) SHALL render a custom blue SVG "play" icon for the view waveform action
- **AND** SHALL NOT display a generic system arrow or text symbol
- **AND** the icon SHALL be loaded from `assets/icons/play.svg`

#### Scenario: Icon caching for performance
- **WHEN** icons are loaded multiple times
- **THEN** the application SHALL cache loaded icons in memory
- **AND** SHALL NOT reload the same icon from disk repeatedly

#### Scenario: Graceful fallback
- **WHEN** a custom icon file is missing or cannot be loaded
- **THEN** the application SHALL log a warning
- **AND** SHALL fall back to system icons or empty icons
- **AND** SHALL NOT crash or display error dialogs
EOF
```

#### 2.3 Validovat master spec

```bash
openspec validate --strict
```

### 3. Git commit

```bash
git add openspec/
git commit -m "chore(openspec): archive fix-ui-critical-symbols after successful implementation

- Move change to archive/2025-10-22-fix-ui-critical-symbols/
- Update specs/ui/spec.md with Custom Iconography requirements
- All implementation tasks completed and tested
- Ready for next change: refine-ui-layout-and-consistency"
```

## Očekávaný výstup

✅ **Změna archivována:**
```
openspec/changes/archive/2025-10-22-fix-ui-critical-symbols/
├── proposal.md
├── tasks.md
└── specs/
    └── ui/
        └── spec.md
```

✅ **Master spec aktualizován:**
`openspec/specs/ui/spec.md` obsahuje nové Requirements pro Custom Iconography

✅ **Validace prošla:** `openspec validate --strict` bez chyb

✅ **Git commit vytvořen:** Archivace je verzována

✅ **Připraveno pro další změnu:** Můžeme začít s `refine-ui-layout-and-consistency`

## Verifikace

```bash
# Zkontrolovat archivovanou strukturu
ls -la openspec/changes/archive/2025-10-22-fix-ui-critical-symbols/

# Zkontrolovat master spec
grep -A 20 "Custom Iconography" openspec/specs/ui/spec.md

# Validovat celý OpenSpec stav
openspec validate --strict

# Zkontrolovat git log
git log -3 --oneline

# Spustit všechny testy
pytest tests/test_tracks_table_model.py -v

# Vizuálně ověřit v aplikaci
python app.py
```

## Poznámky

### Co bylo dosaženo

✅ **Kritický problém vyřešen**: Nesprávné ikony (šipky) nahrazeny jasnými SVG ikonami

✅ **Konzistence napříč platformami**: SVG ikony se renderují stejně na Windows, macOS, Linux

✅ **GZ Media branding**: Ikony používají brand barvy (#10B981, #EF4444, #3B82F6)

✅ **Výkon optimalizován**: Icon caching zabraňuje opakovanému načítání

✅ **Testovatelnost**: Testy ověřují přítomnost ikon v DecorationRole

✅ **Zpětná kompatibilita**: Staré konstanty jsou deprecated, ale ne odstraněny

### Další kroky

Po dokončení této archivace můžeme začít s druhou změnou:

**Změna 2: `refine-ui-layout-and-consistency`** (P1 - Střední)
- Toolbar odsazení a spacing
- Total row kontrast (WCAG 4.5:1)
- Progress bar branding

Tato změna bude mít stejný workflow:
1. Proposal (scaffold)
2. Apply (implement)
3. Archive (finalize)

### Metriky

- **Soubory změněny**: 4 (theme.py, tracks_table_model.py, constants.py, test_tracks_table_model.py)
- **Soubory přidány**: 3 (check.svg, cross.svg, play.svg)
- **Řádky kódu**: ~150 přidáno, ~20 upraveno
- **Testy**: 5 testů (všechny procházejí)
- **Čas implementace**: ~2 hodiny
- **Priorita**: P0 (Kritické)
- **Status**: ✅ Dokončeno