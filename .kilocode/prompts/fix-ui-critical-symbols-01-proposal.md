References:

- openspec\\AGENTS.md

# Kilo-Code Prompt: fix-ui-critical-symbols (Fáze 1: Proposal)

## Kontext

Aplikace "Final Cue Sheet Checker" trpí kritickým UI problémem: ve sloupcích "Match" a "Waveform" dolní tabulky se místo očekávaných symbolů (✓/✗ a play ikona) zobrazují černé šipky (►).

**Příčina:**
- Font Poppins není fyzicky přítomen (pouze DejaVu fonty), což způsobuje font fallback
- Unicode symboly ✓/✗ se renderují jako šipky v fallback fontu
- Windows systémová ikona `QStyle.StandardPixmap.SP_MediaPlay` se vykresluje jako šipka

**Dopad:**
- Kritické snížení použitelnosti (Nielsen's Heuristic #1: Visibility of System Status)
- Uživatelé nerozumí významu symbolů
- Nekonzistentní vzhled napříč platformami

## Cíl

Vytvořit kompletní OpenSpec návrh pro zavedení vlastní ikonové infrastruktury s SVG ikonami, která zajistí konzistentní renderování napříč všemi platformami.

## Kroky

### 1. Vytvoření adresářové struktury

```bash
mkdir -p openspec/changes/fix-ui-critical-symbols/specs/ui
mkdir -p assets/icons
```

### 2. Vytvoření proposal.md

```bash
cat > openspec/changes/fix-ui-critical-symbols/proposal.md << 'EOF'
## Why

The UI currently displays incorrect symbols (black arrows ►) in the "Match" and "Waveform" columns of the tracks table. This is caused by:
1. Font fallback issue: Poppins font is referenced in QSS but not physically present (only DejaVu fonts available)
2. Unicode symbols ✓/✗ render as arrows in the fallback font
3. System icon `QStyle.StandardPixmap.SP_MediaPlay` renders as an arrow on Windows

This creates visual inconsistency and reduces usability, as the meaning of the symbols is not immediately clear. Users cannot distinguish between match/mismatch states or understand the waveform action.

## What Changes

- **Introduce custom icon infrastructure**: Create `ui/theme.py::get_custom_icon()` function to load and cache SVG icons from `assets/icons/`
- **Create SVG icons**: Add three custom icons aligned with GZ Media branding:
  - `check.svg` (16x16, green #10B981) for successful matches
  - `cross.svg` (16x16, red #EF4444) for failed matches
  - `play.svg` (16x16, blue #3B82F6) for waveform view action
- **Replace text symbols with icons**: Modify `TracksTableModel` to return icons via `DecorationRole` instead of text via `DisplayRole`
- **Update tests**: Modify tests to check for `QIcon` in `DecorationRole` instead of text in `DisplayRole`
- **Deprecate old constants**: Mark `SYMBOL_CHECK` and `SYMBOL_CROSS` as deprecated

## Impact

- **Affected specs**: `specs/ui/spec.md` (new requirement: Custom Iconography)
- **Affected code**:
  - `ui/theme.py` - New function `get_custom_icon()`
  - `ui/models/tracks_table_model.py` - Icon rendering in columns 6 and 7
  - `ui/constants.py` - Deprecation comments
  - `tests/test_tracks_table_model.py` - Test updates
- **New files**:
  - `assets/icons/check.svg`
  - `assets/icons/cross.svg`
  - `assets/icons/play.svg`
- **User Experience**: **Critical improvement**. Replaces ambiguous arrows with clear, universally understood icons. Improves clarity, aesthetics, and cross-platform consistency.
- **Breaking changes**: None (backward compatible via deprecated constants)
EOF
```

### 3. Vytvoření tasks.md

```bash
cat > openspec/changes/fix-ui-critical-symbols/tasks.md << 'EOF'
## P0: Critical Icon and Symbol Fixes

### 1. Asset Creation
- [ ] 1.1 Create `assets/icons/` directory
- [ ] 1.2 Create `assets/icons/check.svg` (16x16, green #10B981)
- [ ] 1.3 Create `assets/icons/cross.svg` (16x16, red #EF4444)
- [ ] 1.4 Create `assets/icons/play.svg` (16x16, blue #3B82F6)

### 2. Theme and Configuration Update
- [ ] 2.1 Modify `ui/theme.py`: Create function `get_custom_icon(icon_name: str) -> QIcon`
  - Load SVG icons from `assets/icons/`
  - Implement icon caching for performance
  - Add error handling with fallback to system icons
  - Support icons: 'check', 'cross', 'play'

### 3. Model Implementation
- [ ] 3.1 Modify `ui/models/tracks_table_model.py`:
  - Import `get_custom_icon` from `ui.theme`
  - Column 6 (Match): Return icon via `DecorationRole`, empty string via `DisplayRole`
  - Column 7 (Waveform): Replace `get_system_file_icon('play')` with `get_custom_icon('play')`
  - Preserve match calculation logic (tolerance check)

### 4. Test Updates
- [ ] 4.1 Modify `tests/test_tracks_table_model.py`:
  - Update `test_track_match_symbol_ok`: Check `DecorationRole` for valid `QIcon`
  - Update `test_track_match_symbol_fail`: Check `DecorationRole` for valid `QIcon`
  - Add `test_track_match_display_empty`: Verify `DisplayRole` returns empty string for column 6

### 5. Cleanup
- [ ] 5.1 Modify `ui/constants.py`: Add deprecation comment above `SYMBOL_CHECK` and `SYMBOL_CROSS`
EOF
```

### 4. Vytvoření delta spec

```bash
cat > openspec/changes/fix-ui-critical-symbols/specs/ui/spec.md << 'EOF'
## ADDED Requirements

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

### 5. Vytvoření SVG ikon

#### 5.1 Check icon (zelená, 16x16)

```bash
cat > assets/icons/check.svg << 'EOF'
<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M13.5 4L6 11.5L2.5 8" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
EOF
```

#### 5.2 Cross icon (červená, 16x16)

```bash
cat > assets/icons/cross.svg << 'EOF'
<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 4L4 12" stroke="#EF4444" stroke-width="2" stroke-linecap="round"/>
  <path d="M4 4L12 12" stroke="#EF4444" stroke-width="2" stroke-linecap="round"/>
</svg>
EOF
```

#### 5.3 Play icon (modrá, 16x16)

```bash
cat > assets/icons/play.svg << 'EOF'
<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 3L13 8L5 13V3Z" fill="#3B82F6"/>
</svg>
EOF
```

### 6. Validace návrhu

```bash
openspec validate fix-ui-critical-symbols --strict
```

**Očekávaný výstup:**
```
✓ Change 'fix-ui-critical-symbols' is valid
✓ All delta specs are properly formatted
✓ All requirements have at least one scenario
✓ No validation errors found
```

### 7. Git commit

```bash
git add openspec/changes/fix-ui-critical-symbols/ assets/icons/
git commit -m "feat(openspec): propose fix-ui-critical-symbols for critical icon issues

- Add OpenSpec proposal for custom SVG icon infrastructure
- Create check.svg, cross.svg, play.svg icons (GZ Media branding)
- Define requirements for consistent iconography
- Addresses critical UI/UX audit findings (P0)"
```

## Očekávaný výstup

✅ **Struktura vytvořena:**
```
openspec/changes/fix-ui-critical-symbols/
├── proposal.md
├── tasks.md
└── specs/
    └── ui/
        └── spec.md

assets/icons/
├── check.svg
├── cross.svg
└── play.svg
```

✅ **Validace prošla:** `openspec validate` bez chyb

✅ **Git commit vytvořen:** Změna je verzována

✅ **Připraveno k implementaci:** Můžeme pokračovat promptem 02-apply

## Verifikace

```bash
# Zkontrolovat strukturu
ls -la openspec/changes/fix-ui-critical-symbols/
ls -la assets/icons/

# Zkontrolovat obsah proposal
cat openspec/changes/fix-ui-critical-symbols/proposal.md

# Zkontrolovat SVG ikony
cat assets/icons/check.svg

# Ověřit git status
git log -1 --oneline