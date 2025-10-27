# GZ Media Assets

Tento adresář obsahuje grafické assety pro GZ Media branding aplikace Final Cue Sheet Checker.

## Požadované logo soubory

### `gz_logo_white.png`
- **Formát:** PNG s průhledným pozadím
- **Barva:** Bílá varianta GZ Media loga
- **Rozměry:** Doporučeno 128x32 pixelů (4:1 poměr)
- **Umístění:** Levý horní roh hlavního okna
- **Pozadí:** Průhledné pro správné zobrazení na různých barvách

### `gz_logo_dark.png` (volitelné)
- **Formát:** PNG s průhledným pozadím
- **Barva:** Tmavá varianta pro světlé pozadí
- **Rozměry:** Stejné jako bílá varianta
- **Použití:** Automatické přepínání podle theme modu

## UI Icons

### `icons/check.svg`
- **Formát:** SVG
- **Rozměry:** 16x16 pixelů
- **Barva:** Zelená (#10B981)
- **Použití:** Indikace úspěšného match v tabulce (sloupec Match)
- **Design:** Checkmark symbol s kulatými konci

### `icons/cross.svg`
- **Formát:** SVG
- **Rozměry:** 16x16 pixelů
- **Barva:** Červená (#EF4444)
- **Použití:** Indikace neúspěšného match v tabulce (sloupec Match)
- **Design:** Cross symbol s kulatými konci

### `icons/play.svg`
- **Formát:** SVG
- **Rozměry:** 16x16 pixelů
- **Barva:** Modrá (#3B82F6)
- **Použití:** Tlačítko pro zobrazení waveform (sloupec Waveform)
- **Design:** Play triangle symbol

## Fallback chování pro Ikony

Pokud se vlastní SVG ikony (`check.svg`, `cross.svg`, `play.svg`) nepodaří načíst z Qt resources ani ze souborového systému, aplikace se pokusí použít ikony poskytované systémovým tématem. Toto zajišťuje, že aplikace zůstane funkční i v případě chybějících assetů.

Konkrétní mapování fallbacků je následující:
- **`check`**: `QStyle.StandardPixmap.SP_DialogApplyButton` (obvykle ikona zaškrtnutí)
- **`cross`**: `QStyle.StandardPixmap.SP_DialogCancelButton` (obvykle ikona křížku)
- **`play`**: `QStyle.StandardPixmap.SP_MediaPlay` (standardní ikona pro přehrávání)

Aplikace zaznamená varování do logu, pokud dojde k použití fallbacku.

## Technické požadavky

- **Formát:** PNG s průhledností (RGBA)
- **Velikost:** Optimalizované pro rychlé načítání (< 50KB)
- **Rozměry:** Šířka max 200px, výška max 40px
- **Kvalita:** Ostré hrany, žádné kompresní artefakty

## Fallback chování pro Logo

Pokud logo soubory nejsou nalezeny, aplikace zobrazí textový fallback:
- **Text:** "GZ Media"
- **Font:** Poppins Bold
- **Barva:** GZ Primary Blue (#1E3A8A)

## Claim

Claim "Emotions. Materialized." se zobrazuje v pravém dolním rohu okna:
- **Font:** Poppins Italic
- **Velikost:** 8pt
- **Barva:** GZ Gray (#6B7280)
- **Konfigurace:** Lze zapnout/vypnout v settings

## Packaging

Custom SVG icons are bundled using Qt's resource search path system for cross-platform compatibility.

### Qt Resource Approach (Recommended)

Icons are made available via Qt's resource system:

1. **Resource File**: `assets/icons.qrc` declares the SVG files under the `/icons` prefix
2. **Resource Module**: `ui/_icons_rc.py` registers the assets directory as a Qt resource search path
   - **Development**: Loads icons directly from filesystem via `QResource.addSearchPath()`
   - **PyInstaller**: Automatically handles bundled assets via `sys._MEIPASS`
3. **Import**: The module is imported at startup in `app.py` (line 30)
4. **Loading**: `get_custom_icon()` in `ui/theme.py` attempts to load from `:/icons/<name>.svg` (Qt resources) with filesystem fallback

### Build/Compilation

**Option A: Using pyrcc6 (Standard Qt Tool)**
```bash
pyrcc6 assets/icons.qrc -o ui/_icons_rc.py
```

**Option B: Using the Build Script (Fallback)**
```bash
python tools/build_resources.py
```

This generates `ui/_icons_rc.py` which registers resource search paths for both development and packaged builds.

### PyInstaller Bundling

For PyInstaller, ensure assets are included:

**Option 1: Data files (via `.spec` or CLI)**
```bash
pyinstaller --add-data "assets/icons;assets/icons" app.py
```

**Option 2: Include in analysis**
Add to `.spec` file:
```python
datas=[('assets/icons', 'assets/icons')]
```

The resource search path system handles both approaches automatically through `sys._MEIPASS` detection.

## Přidání nových assetů

1. Uložte logo soubory do tohoto adresáře
2. Aktualizujte `config.py` - `gz_logo_path` konfiguraci
3. Restartujte aplikaci pro načtení nových assetů

## Brand Guidelines

Všechny assety musí být v souladu s GZ Media brand guidelines:
- ✅ Pouze oficiální GZ Media logo
- ✅ Správné proporce a barevnost
- ✅ Profesionální kvalita
- ❌ Žádné modifikace nebo úpravy loga