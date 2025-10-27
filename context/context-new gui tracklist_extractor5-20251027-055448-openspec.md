## Project Context

- Root Path: D:\moje-nove-projekty\new gui tracklist_extractor5
- Timestamp: 20251027-055448
- Total Files: 12
- Total Size: 45108 bytes

## Summary Table

| Relative Path | Bytes | Lines |
|---------------|-------|-------|
| AGENTS.md | 660 | 18 |
| assets\README.md | 4791 | 134 |
| CLAUDE.md | 660 | 18 |
| docs\pm\fluent_gui-removal.md | 788 | 13 |
| fonts\dejavu-fonts-ttf-2.37\README.md | 2556 | 68 |
| openspec\AGENTS.md | 14982 | 457 |
| openspec\changes\refactor-architecture-modularity\proposal.md | 2868 | 18 |
| openspec\changes\refactor-architecture-modularity\specs\architecture\spec.md | 2526 | 47 |
| openspec\changes\refactor-architecture-modularity\tasks.md | 2796 | 31 |
| openspec\project.md | 6581 | 60 |
| README.md | 2709 | 37 |
| tests\README.md | 3191 | 88 |

## File Contents

### AGENTS.md

``n<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->
``n
### assets\README.md

``n# GZ Media Assets

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
``n
### CLAUDE.md

``n<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->
``n
### docs\pm\fluent_gui-removal.md

``n# PM Ticket: Plan for fluent_gui.py Removal

- Context: fluent_gui.py served as the compatibility layer around the new UI package. All production entry points now use `app.py` and modular imports.
- Decision: Removal executed as part of change `refactor-architecture-modularity`.
- Steps:
  1) Inventory imports (completed 2025-10-26).
  2) Update entry points, scripts, and tests to reference authoritative modules (completed).
  3) Delete `fluent_gui.py`, retire characterization tests, and document migration path (completed).
- Owner: maintainers
- Status: completed
- Notes: External consumers should import symbols directly from `ui/`, `services/`, `core/`, or `adapters/`. Legacy exports are no longer available.
- Related change: openspec/changes/refactor-architecture-modularity

``n
### fonts\dejavu-fonts-ttf-2.37\README.md

``n[![Build Status](https://travis-ci.org/dejavu-fonts/dejavu-fonts.svg)](https://travis-ci.org/dejavu-fonts/dejavu-fonts)

DejaVu fonts 2.37 (c)2004-2016 DejaVu fonts team
------------------------------------------------

The DejaVu fonts are a font family based on the Bitstream Vera Fonts
(http://gnome.org/fonts/). Its purpose is to provide a wider range of
characters (see status.txt for more information) while maintaining the
original look and feel.

DejaVu fonts are based on Bitstream Vera fonts version 1.10.

Available fonts (Sans = sans serif, Mono = monospaced):

DejaVu Sans Mono
DejaVu Sans Mono Bold
DejaVu Sans Mono Bold Oblique
DejaVu Sans Mono Oblique
DejaVu Sans
DejaVu Sans Bold
DejaVu Sans Bold Oblique
DejaVu Sans Oblique
DejaVu Sans ExtraLight (experimental)
DejaVu Serif
DejaVu Serif Bold
DejaVu Serif Bold Italic (experimental)
DejaVu Serif Italic (experimental)
DejaVu Sans Condensed (experimental)
DejaVu Sans Condensed Bold (experimental)
DejaVu Sans Condensed Bold Oblique (experimental)
DejaVu Sans Condensed Oblique (experimental)
DejaVu Serif Condensed (experimental)
DejaVu Serif Condensed Bold (experimental)
DejaVu Serif Condensed Bold Italic (experimental)
DejaVu Serif Condensed Italic (experimental)
DejaVu Math TeX Gyre

All fonts are also available as derivative called DejaVu LGC with support
only for Latin, Greek and Cyrillic scripts.

For license information see LICENSE. What's new is described in NEWS. Known
bugs are in BUGS. All authors are mentioned in AUTHORS.

Fonts are published in source form as SFD files (Spline Font Database from
FontForge - http://fontforge.sf.net/) and in compiled form as TTF files
(TrueType fonts).

For more information go to http://dejavu.sourceforge.net/.

Characters from Arev fonts, Copyright (c) 2006 by Tavmjong Bah:
---------------------------
U+01BA, U+01BF, U+01F7, U+021C-U+021D, U+0220, U+0222-U+0223,
U+02B9, U+02BA, U+02BD, U+02C2-U+02C5, U+02d4-U+02D5,
U+02D7, U+02EC-U+02EE, U+0346-U+034E, U+0360, U+0362,
U+03E2-03EF, U+0460-0463, U+0466-U+0486, U+0488-U+0489, U+04A8-U+04A9,
U+0500-U+050F, U+2055-205E, U+20B0, U+20B2-U+20B3, U+2102, U+210D, U+210F,
U+2111, U+2113, U+2115, U+2118-U+211A, U+211C-U+211D, U+2124, U+2135,
U+213C-U+2140, U+2295-U+2298, U+2308-U+230B, U+26A2-U+26B1, U+2701-U+2704,
U+2706-U+2709, U+270C-U+274B, U+2758-U+275A, U+2761-U+2775, U+2780-U+2794,
U+2798-U+27AF, U+27B1-U+27BE, U+FB05-U+FB06

DejaVu Math TeX Gyre
--------------------
TeX Gyre DJV Math by B. Jackowski, P. Strzelczyk and P. Pianowski
(on behalf of TeX users groups).

$Id$

``n
### openspec\AGENTS.md

``n# OpenSpec Instructions

Instructions for AI coding assistants using OpenSpec for spec-driven development.

## TL;DR Quick Checklist

- Search existing work: `openspec spec list --long`, `openspec list` (use `rg` only for full-text search)
- Decide scope: new capability vs modify existing capability
- Pick a unique `change-id`: kebab-case, verb-led (`add-`, `update-`, `remove-`, `refactor-`)
- Scaffold: `proposal.md`, `tasks.md`, `design.md` (only if needed), and delta specs per affected capability
- Write deltas: use `## ADDED|MODIFIED|REMOVED|RENAMED Requirements`; include at least one `#### Scenario:` per requirement
- Validate: `openspec validate [change-id] --strict` and fix issues
- Request approval: Do not start implementation until proposal is approved

## Three-Stage Workflow

### Stage 1: Creating Changes
Create proposal when you need to:
- Add features or functionality
- Make breaking changes (API, schema)
- Change architecture or patterns  
- Optimize performance (changes behavior)
- Update security patterns

Triggers (examples):
- "Help me create a change proposal"
- "Help me plan a change"
- "Help me create a proposal"
- "I want to create a spec proposal"
- "I want to create a spec"

Loose matching guidance:
- Contains one of: `proposal`, `change`, `spec`
- With one of: `create`, `plan`, `make`, `start`, `help`

Skip proposal for:
- Bug fixes (restore intended behavior)
- Typos, formatting, comments
- Dependency updates (non-breaking)
- Configuration changes
- Tests for existing behavior

**Workflow**
1. Review `openspec/project.md`, `openspec list`, and `openspec list --specs` to understand current context.
2. Choose a unique verb-led `change-id` and scaffold `proposal.md`, `tasks.md`, optional `design.md`, and spec deltas under `openspec/changes/<id>/`.
3. Draft spec deltas using `## ADDED|MODIFIED|REMOVED Requirements` with at least one `#### Scenario:` per requirement.
4. Run `openspec validate <id> --strict` and resolve any issues before sharing the proposal.

### Stage 2: Implementing Changes
Track these steps as TODOs and complete them one by one.
1. **Read proposal.md** - Understand what's being built
2. **Read design.md** (if exists) - Review technical decisions
3. **Read tasks.md** - Get implementation checklist
4. **Implement tasks sequentially** - Complete in order
5. **Confirm completion** - Ensure every item in `tasks.md` is finished before updating statuses
6. **Update checklist** - After all work is done, set every task to `- [x]` so the list reflects reality
7. **Approval gate** - Do not start implementation until the proposal is reviewed and approved

### Stage 3: Archiving Changes
After deployment, create separate PR to:
- Move `changes/[name]/` → `changes/archive/YYYY-MM-DD-[name]/`
- Update `specs/` if capabilities changed
- Use `openspec archive [change] --skip-specs --yes` for tooling-only changes
- Run `openspec validate --strict` to confirm the archived change passes checks

## Before Any Task

**Context Checklist:**
- [ ] Read relevant specs in `specs/[capability]/spec.md`
- [ ] Check pending changes in `changes/` for conflicts
- [ ] Read `openspec/project.md` for conventions
- [ ] Run `openspec list` to see active changes
- [ ] Run `openspec list --specs` to see existing capabilities

**Before Creating Specs:**
- Always check if capability already exists
- Prefer modifying existing specs over creating duplicates
- Use `openspec show [spec]` to review current state
- If request is ambiguous, ask 1–2 clarifying questions before scaffolding

### Search Guidance
- Enumerate specs: `openspec spec list --long` (or `--json` for scripts)
- Enumerate changes: `openspec list` (or `openspec change list --json` - deprecated but available)
- Show details:
  - Spec: `openspec show <spec-id> --type spec` (use `--json` for filters)
  - Change: `openspec show <change-id> --json --deltas-only`
- Full-text search (use ripgrep): `rg -n "Requirement:|Scenario:" openspec/specs`

## Quick Start

### CLI Commands

```bash
# Essential commands
openspec list                  # List active changes
openspec list --specs          # List specifications
openspec show [item]           # Display change or spec
openspec diff [change]         # Show spec differences
openspec validate [item]       # Validate changes or specs
openspec archive [change] [--yes|-y]      # Archive after deployment (add --yes for non-interactive runs)

# Project management
openspec init [path]           # Initialize OpenSpec
openspec update [path]         # Update instruction files

# Interactive mode
openspec show                  # Prompts for selection
openspec validate              # Bulk validation mode

# Debugging
openspec show [change] --json --deltas-only
openspec validate [change] --strict
```

### Command Flags

- `--json` - Machine-readable output
- `--type change|spec` - Disambiguate items
- `--strict` - Comprehensive validation
- `--no-interactive` - Disable prompts
- `--skip-specs` - Archive without spec updates
- `--yes`/`-y` - Skip confirmation prompts (non-interactive archive)

## Directory Structure

```
openspec/
├── project.md              # Project conventions
├── specs/                  # Current truth - what IS built
│   └── [capability]/       # Single focused capability
│       ├── spec.md         # Requirements and scenarios
│       └── design.md       # Technical patterns
├── changes/                # Proposals - what SHOULD change
│   ├── [change-name]/
│   │   ├── proposal.md     # Why, what, impact
│   │   ├── tasks.md        # Implementation checklist
│   │   ├── design.md       # Technical decisions (optional; see criteria)
│   │   └── specs/          # Delta changes
│   │       └── [capability]/
│   │           └── spec.md # ADDED/MODIFIED/REMOVED
│   └── archive/            # Completed changes
```

## Creating Change Proposals

### Decision Tree

```
New request?
├─ Bug fix restoring spec behavior? → Fix directly
├─ Typo/format/comment? → Fix directly  
├─ New feature/capability? → Create proposal
├─ Breaking change? → Create proposal
├─ Architecture change? → Create proposal
└─ Unclear? → Create proposal (safer)
```

### Proposal Structure

1. **Create directory:** `changes/[change-id]/` (kebab-case, verb-led, unique)

2. **Write proposal.md:**
```markdown
## Why
[1-2 sentences on problem/opportunity]

## What Changes
- [Bullet list of changes]
- [Mark breaking changes with **BREAKING**]

## Impact
- Affected specs: [list capabilities]
- Affected code: [key files/systems]
```

3. **Create spec deltas:** `specs/[capability]/spec.md`
```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide...

#### Scenario: Success case
- **WHEN** user performs action
- **THEN** expected result

## MODIFIED Requirements
### Requirement: Existing Feature
[Complete modified requirement]

## REMOVED Requirements
### Requirement: Old Feature
**Reason**: [Why removing]
**Migration**: [How to handle]
```
If multiple capabilities are affected, create multiple delta files under `changes/[change-id]/specs/<capability>/spec.md`—one per capability.

4. **Create tasks.md:**
```markdown
## 1. Implementation
- [ ] 1.1 Create database schema
- [ ] 1.2 Implement API endpoint
- [ ] 1.3 Add frontend component
- [ ] 1.4 Write tests
```

5. **Create design.md when needed:**
Create `design.md` if any of the following apply; otherwise omit it:
- Cross-cutting change (multiple services/modules) or a new architectural pattern
- New external dependency or significant data model changes
- Security, performance, or migration complexity
- Ambiguity that benefits from technical decisions before coding

Minimal `design.md` skeleton:
```markdown
## Context
[Background, constraints, stakeholders]

## Goals / Non-Goals
- Goals: [...]
- Non-Goals: [...]

## Decisions
- Decision: [What and why]
- Alternatives considered: [Options + rationale]

## Risks / Trade-offs
- [Risk] → Mitigation

## Migration Plan
[Steps, rollback]

## Open Questions
- [...]
```

## Spec File Format

### Critical: Scenario Formatting

**CORRECT** (use #### headers):
```markdown
#### Scenario: User login success
- **WHEN** valid credentials provided
- **THEN** return JWT token
```

**WRONG** (don't use bullets or bold):
```markdown
- **Scenario: User login**  ❌
**Scenario**: User login     ❌
### Scenario: User login      ❌
```

Every requirement MUST have at least one scenario.

### Requirement Wording
- Use SHALL/MUST for normative requirements (avoid should/may unless intentionally non-normative)

### Delta Operations

- `## ADDED Requirements` - New capabilities
- `## MODIFIED Requirements` - Changed behavior
- `## REMOVED Requirements` - Deprecated features
- `## RENAMED Requirements` - Name changes

Headers matched with `trim(header)` - whitespace ignored.

#### When to use ADDED vs MODIFIED
- ADDED: Introduces a new capability or sub-capability that can stand alone as a requirement. Prefer ADDED when the change is orthogonal (e.g., adding "Slash Command Configuration") rather than altering the semantics of an existing requirement.
- MODIFIED: Changes the behavior, scope, or acceptance criteria of an existing requirement. Always paste the full, updated requirement content (header + all scenarios). The archiver will replace the entire requirement with what you provide here; partial deltas will drop previous details.
- RENAMED: Use when only the name changes. If you also change behavior, use RENAMED (name) plus MODIFIED (content) referencing the new name.

Common pitfall: Using MODIFIED to add a new concern without including the previous text. This causes loss of detail at archive time. If you aren’t explicitly changing the existing requirement, add a new requirement under ADDED instead.

Authoring a MODIFIED requirement correctly:
1) Locate the existing requirement in `openspec/specs/<capability>/spec.md`.
2) Copy the entire requirement block (from `### Requirement: ...` through its scenarios).
3) Paste it under `## MODIFIED Requirements` and edit to reflect the new behavior.
4) Ensure the header text matches exactly (whitespace-insensitive) and keep at least one `#### Scenario:`.

Example for RENAMED:
```markdown
## RENAMED Requirements
- FROM: `### Requirement: Login`
- TO: `### Requirement: User Authentication`
```

## Troubleshooting

### Common Errors

**"Change must have at least one delta"**
- Check `changes/[name]/specs/` exists with .md files
- Verify files have operation prefixes (## ADDED Requirements)

**"Requirement must have at least one scenario"**
- Check scenarios use `#### Scenario:` format (4 hashtags)
- Don't use bullet points or bold for scenario headers

**Silent scenario parsing failures**
- Exact format required: `#### Scenario: Name`
- Debug with: `openspec show [change] --json --deltas-only`

### Validation Tips

```bash
# Always use strict mode for comprehensive checks
openspec validate [change] --strict

# Debug delta parsing
openspec show [change] --json | jq '.deltas'

# Check specific requirement
openspec show [spec] --json -r 1
```

## Happy Path Script

```bash
# 1) Explore current state
openspec spec list --long
openspec list
# Optional full-text search:
# rg -n "Requirement:|Scenario:" openspec/specs
# rg -n "^#|Requirement:" openspec/changes

# 2) Choose change id and scaffold
CHANGE=add-two-factor-auth
mkdir -p openspec/changes/$CHANGE/{specs/auth}
printf "## Why\n...\n\n## What Changes\n- ...\n\n## Impact\n- ...\n" > openspec/changes/$CHANGE/proposal.md
printf "## 1. Implementation\n- [ ] 1.1 ...\n" > openspec/changes/$CHANGE/tasks.md

# 3) Add deltas (example)
cat > openspec/changes/$CHANGE/specs/auth/spec.md << 'EOF'
## ADDED Requirements
### Requirement: Two-Factor Authentication
Users MUST provide a second factor during login.

#### Scenario: OTP required
- **WHEN** valid credentials are provided
- **THEN** an OTP challenge is required
EOF

# 4) Validate
openspec validate $CHANGE --strict
```

## Multi-Capability Example

```
openspec/changes/add-2fa-notify/
├── proposal.md
├── tasks.md
└── specs/
    ├── auth/
    │   └── spec.md   # ADDED: Two-Factor Authentication
    └── notifications/
        └── spec.md   # ADDED: OTP email notification
```

auth/spec.md
```markdown
## ADDED Requirements
### Requirement: Two-Factor Authentication
...
```

notifications/spec.md
```markdown
## ADDED Requirements
### Requirement: OTP Email Notification
...
```

## Best Practices

### Simplicity First
- Default to <100 lines of new code
- Single-file implementations until proven insufficient
- Avoid frameworks without clear justification
- Choose boring, proven patterns

### Complexity Triggers
Only add complexity with:
- Performance data showing current solution too slow
- Concrete scale requirements (>1000 users, >100MB data)
- Multiple proven use cases requiring abstraction

### Clear References
- Use `file.ts:42` format for code locations
- Reference specs as `specs/auth/spec.md`
- Link related changes and PRs

### Capability Naming
- Use verb-noun: `user-auth`, `payment-capture`
- Single purpose per capability
- 10-minute understandability rule
- Split if description needs "AND"

### Change ID Naming
- Use kebab-case, short and descriptive: `add-two-factor-auth`
- Prefer verb-led prefixes: `add-`, `update-`, `remove-`, `refactor-`
- Ensure uniqueness; if taken, append `-2`, `-3`, etc.

## Tool Selection Guide

| Task | Tool | Why |
|------|------|-----|
| Find files by pattern | Glob | Fast pattern matching |
| Search code content | Grep | Optimized regex search |
| Read specific files | Read | Direct file access |
| Explore unknown scope | Task | Multi-step investigation |

## Error Recovery

### Change Conflicts
1. Run `openspec list` to see active changes
2. Check for overlapping specs
3. Coordinate with change owners
4. Consider combining proposals

### Validation Failures
1. Run with `--strict` flag
2. Check JSON output for details
3. Verify spec file format
4. Ensure scenarios properly formatted

### Missing Context
1. Read project.md first
2. Check related specs
3. Review recent archives
4. Ask for clarification

## Quick Reference

### Stage Indicators
- `changes/` - Proposed, not yet built
- `specs/` - Built and deployed
- `archive/` - Completed changes

### File Purposes
- `proposal.md` - Why and what
- `tasks.md` - Implementation steps
- `design.md` - Technical decisions
- `spec.md` - Requirements and behavior

### CLI Essentials
```bash
openspec list              # What's in progress?
openspec show [item]       # View details
openspec diff [change]     # What's changing?
openspec validate --strict # Is it correct?
openspec archive [change] [--yes|-y]  # Mark complete (add --yes for automation)
```

Remember: Specs are truth. Changes are proposals. Keep them in sync.

``n
### openspec\changes\refactor-architecture-modularity\proposal.md

``n## Why
The UI refactor stalled because of coupling to legacy wrappers, a monolithic configuration object, and ad hoc status strings. The codebase is carrying divergent-change hotspots (`fluent_gui.py`, `config.AppConfig`) that force shotgun edits and make new features risky. Configuration logic is impossible to test in isolation because UI widgets manipulate `AppConfig` directly. Audio helpers mutate `WavInfo` records from the outside, and analysis status strings are duplicated across services and UI models. Together these issues increase cycle time, break encapsulation, and leave maintainability debt documented in PM notes.

## What Changes
Work will proceed in five deliberate phases so we can validate each milestone without rolling back:

1. **Legacy wrapper removal** – Redirect every import away from `fluent_gui.py`, update entry points, scripts, and tests, then delete the wrapper and retire characterization tests.
2. **Modular configuration loader** – Introduce dataclasses (`LlmSettings`, `UiSettings`, `AnalysisSettings`, `PathSettings`, etc.), extract shared option lists (LLM models, DPI scales) into single sources of truth, and add a `ConfigLoader` factory that reads `QSettings` once. Existing loader helpers in `ui/config_models.py` will call into the factory while `AppConfig` remains temporarily for compatibility.
3. **Settings UI decoupling** – Replace direct `cfg.set()` calls with `settingChanged`-style signals, inject scoped settings objects into widgets, and split long builder methods into smaller components. `SettingsDialog` becomes the coordinator that persists changes through the loader.
4. **Encapsulation in audio models** – Add `WavInfo.apply_parsed_info` (name TBD) so detector helpers and steps stop mutating attributes directly. Update AI helpers, strict/deterministic steps, and tests to rely on the new API.
5. **Enum-backed analysis status** – Introduce `AnalysisStatus` enum with severity, icon, and color helpers. Replace string literals throughout comparison services, UI models, exports, and tests, ensuring JSON output remains stable via enum serialization.

## Impact
- Refactoring touches configuration initialization, UI wiring, adapters, and services; regression risk is high without phased delivery. Each phase will ship behind targeted review gates before removing fallback paths.
- Expect churn in tests and fixtures: configuration loaders and status comparisons will need updates, and new unit coverage is required for the loader, enum behaviors, and UI signal flow.
- Build and deploy scripts (`tools/`, PyInstaller spec) must keep working; we will validate CLI entry points (`app.py`) after deleting `fluent_gui.py`.
- No user-facing workflow changes are intended, but transient instability is possible until all substeps ship; thorough CI (pytest + static checks) is mandatory per milestone.

``n
### openspec\changes\refactor-architecture-modularity\specs\architecture\spec.md

``n## ADDED Requirements

### Requirement: Legacy Wrapper Removed
All production entry points MUST stop importing `fluent_gui.py`, and the wrapper MUST be removed from the codebase.

#### Scenario: No fluent_gui Imports
- **GIVEN** the repository after the change is merged  
- **WHEN** searching for `fluent_gui` across source, tests, and tooling  
- **THEN** no imports or references are present  
- **AND** application entry points run successfully via `app.py`.

### Requirement: Modular Configuration Loader
Configuration MUST be composed of scoped dataclasses produced by a central `ConfigLoader`, eliminating direct dependence on the monolithic `AppConfig`.

#### Scenario: Typed Settings Construction
- **GIVEN** `ConfigLoader` is initialized with `QSettings` data  
- **WHEN** clients request settings for LLM, UI, analysis, or paths  
- **THEN** they receive strongly typed dataclass instances  
- **AND** shared option lists (e.g., LLM models, DPI scale choices) are defined in exactly one place.

### Requirement: Decoupled Settings UI
Settings UI widgets MUST communicate changes via observer signals/callbacks instead of mutating configuration classes directly.

#### Scenario: Folder Setting Emits Change
- **GIVEN** a `FolderSettingCard` instance bound to a config key  
- **WHEN** the user edits the folder path or chooses a directory  
- **THEN** the widget emits a `settingChanged` (or equivalent) event containing the key and new value  
- **AND** persistence is handled by the parent controller using injected settings objects.

### Requirement: Encapsulated WavInfo Updates
Updates derived from AI parsing MUST be applied through methods on `WavInfo`, not by mutating attributes externally.

#### Scenario: Apply Parsed Info
- **GIVEN** a `WavInfo` instance and parsed AI metadata for side/position  
- **WHEN** `WavInfo.apply_parsed_info(parsed)` is called  
- **THEN** the instance updates its own `side` and `position` fields according to normalization rules  
- **AND** helper modules no longer assign those attributes directly.

### Requirement: Analysis Status Enum
Analysis status MUST be represented by a dedicated `AnalysisStatus` enum that encapsulates severity and presentation details.

#### Scenario: Status Drives UI State
- **GIVEN** a `SideResult` produced by the comparison service  
- **WHEN** UI models render the status column  
- **THEN** they use `AnalysisStatus` members to resolve severity, colors, and icons  
- **AND** no code compares raw string literals like `"OK"` or `"FAIL"`.

``n
### openspec\changes\refactor-architecture-modularity\tasks.md

``n## Phase 1 — Legacy Wrapper Removal
- [ ] 1.1 List every import of `fluent_gui.py` (app entry points, scripts, tests, tooling).
- [ ] 1.2 Update `app.py`, `scripts/smoke_test.py`, GUI tests, and any helpers to import authoritative modules directly.
- [ ] 1.3 Remove `fluent_gui.py`, drop the characterization tests, clean up mypy config, and run smoke/GUI checks to confirm the main window still launches.

## Phase 2 — Modular Config Loader
- [ ] 2.1 Add scoped dataclasses in `core/models/settings.py` (`LlmSettings`, `UiSettings`, `AnalysisSettings`, `PathSettings`, plus shared enums as needed).
- [ ] 2.2 Define single-source constants for LLM model options, DPI scales, and related lists inside `config.py`.
- [ ] 2.3 Implement `ConfigLoader` that reads `QSettings`, builds the new dataclasses, and exposes factory methods while leaving `AppConfig` marked deprecated.
- [ ] 2.4 Refactor `ui/config_models.py`, CLI scripts, and tests to obtain settings via `ConfigLoader`; ensure old code paths continue working during migration.

## Phase 3 — Settings UI Decoupling
- [ ] 3.1 Add `settingChanged(key, value)` (or equivalent) signals to `FolderSettingCard` and other widgets currently mutating `cfg`.
- [ ] 3.2 Split the large `_build_*` helpers into focused widget factories, injecting scoped dataclasses instead of the whole `AppConfig`.
- [ ] 3.3 Update `SettingsDialog` to coordinate persistence through `ConfigLoader`, wire signals, and adjust Qt tests for the new observer workflow.

## Phase 4 — Audio Helper Encapsulation
- [ ] 4.1 Introduce `WavInfo.apply_parsed_info` (name finalised during implementation) to own side/position updates and normalization.
- [ ] 4.2 Update `ai_helpers`, detection steps (`StrictParserStep`, `AiParserStep`, `DeterministicFallbackStep`, fake detector), and chained detector normalization to call the new method.
- [ ] 4.3 Refresh unit tests for detectors and parsing to assert encapsulated behaviour rather than direct attribute mutation.

## Phase 5 — Analysis Status Enum
- [ ] 5.1 Create `AnalysisStatus` enum with severity ordering, icon lookup, color helpers, and string conversion.
- [ ] 5.2 Replace literals in `core/domain/comparison.py`, UI table models, exports, filters, and tests with the enum API.
- [ ] 5.3 Ensure serialization (Pydantic + JSON exports) produces the expected strings and extend tests to cover regression scenarios.

## Phase 6 — Validation & Communication
- [ ] 6.1 Update documentation (README, PM ticket) with the new config workflow, signal pattern, and enum usage.
- [ ] 6.2 Run full quality gates (`black`, `ruff`, `mypy`, `pytest --cov`) after each phase before moving forward.
- [ ] 6.3 Publish migration guidance for any consumers that previously depended on `fluent_gui.py` or direct `cfg` access.

``n
### openspec\project.md

``n# Project Context

## Purpose
Tracklist Extractor is a desktop quality-control tool for the GZ Media mastering team. It pairs cue sheet PDFs with ZIP bundles of WAV masters, uses a vision language model to read the cue sheet, and produces structured track data that is compared against audio durations. Operators review mismatches, filter by severity, inspect individual tracks, and export JSON summaries for downstream reporting.

## Tech Stack
- Python 3.11 with extensive type hints, pydantic models, and dataclasses for domain entities.
- PyQt6 plus a custom Qt stylesheet (`gz_media.qss`) for the desktop UI; resource helpers under `ui/_icons_rc.py` register fonts and icons, with PyQtGraph reserved for waveform work.
- PyMuPDF (`fitz`) and Pillow for rendering PDF pages to images prior to AI analysis.
- `openai` client targeting OpenRouter-hosted vision models; `python-dotenv` for loading `.env`.
- `soundfile`/Libsndfile with built-in `wave` fallback for WAV duration probing; `numpy` supports generated fixtures.
- Tooling: `black`, `ruff`, `mypy`, `pytest`, `pytest-qt`, `coverage`, and packaging helpers (PyInstaller scripts and Qt resource builder) in `tools/`.

## Project Conventions

### Code Style
- Format Python with `black` (default settings) and lint with `ruff` (line length 120, `E501` ignored) plus `mypy`; the `.githooks/pre-commit` script enforces this trio, and `tools/check.sh` runs the same suite.
- Prefer fully type-annotated functions; share data via pydantic models (`core.models.analysis`) or dataclasses (`core.models.settings`), and avoid touching the global `cfg` outside entry points; load typed settings via `ui.config_models`.
- Write actionable English log messages; legacy Czech strings remain until retired, but new code should use English wording.
- Keep the UI responsive by delegating long-running work to `ui/workers` or `services` instead of blocking the main thread.

### Architecture Patterns
- Hexagonal layout: `core` contains domain logic and ports, `adapters` implement infrastructure for AI, PDF, audio, filesystem, and UI concerns, `services` orchestrate domain workflows, and `ui` renders the PyQt6 interface via injected dependencies.
- `app.py` is the primary entry point; `fluent_gui.py` persists only as a legacy wrapper and should not receive new development.
- Configuration lives in `config.AppConfig` (Qt `QSettings`); helpers in `ui/config_models.py` convert persisted values into typed settings consumed by services and widgets.
- Background analysis flows through `AnalysisWorkerManager`/`AnalysisWorker` (QThread) to keep the GUI responsive; results and exports are mediated by `services.analysis_service` and `services.export_service`.

### Testing Strategy
- Pytest with `pytest-qt` powers GUI coverage; `tests/conftest.py` supplies a session-wide `QApplication`, isolated QSettings, and synthetic ZIP/WAV archives.
- Unit tests focus on detectors, services, config loaders, and table models; golden JSON fixtures under `tests/data/golden/` anchor regression characterization.
- CI (`.github/workflows/test.yml`) runs on pushes to `main` and all PRs using Ubuntu with `QT_QPA_PLATFORM=offscreen` and `xvfb-run pytest --cov`.
- Aim for 80%+ coverage on new work, especially around waveform integration, exports, and tolerance handling; prefer deterministic fixtures over live API calls.

### Git Workflow
- Trunk-based development on `main`; create feature branches and submit pull requests. GitHub Actions enforces the test suite before merge.
- Run `black`, `ruff`, `mypy`, and `pytest` (or `tools/check.sh`) locally before pushing; keep lint/type debt confined to legacy allowlists.
- Follow OpenSpec guidance: author a proposal before implementing new capabilities, architectural shifts, or non-trivial refactors; manage specs with the `openspec` CLI.
- Commit messages use concise imperative verbs and reference the relevant OpenSpec change when applicable.

## Domain Context
- Input discovery scans configured PDF and ZIP directories, extracts numeric IDs (`adapters.filesystem.file_discovery`), and pairs files one-to-one, skipping ambiguous matches; pairs become `core.models.analysis.FilePair` instances.
- PDF parsing pipeline: `adapters.pdf.renderer.PdfImageRenderer` rasterizes pages via PyMuPDF, `adapters.ai.vlm.VlmClient` (OpenRouter) returns structured track JSON, and `core.domain.parsing.TracklistParser` normalizes data into `TrackInfo` grouped by side/position.
- Audio pipeline: `adapters.audio.wav_reader.ZipWavFileReader` materializes WAV entries to read durations, while `adapters.audio.chained_detector.ChainedAudioModeDetector` chains strict filename parsing, optional AI hints, and deterministic fallback to assign sides and normalized positions.
- `core.domain.comparison.compare_data` merges PDF and WAV data into `SideResult` objects, applying warn/fail tolerances, and the UI presents the two-level table (`ResultsTableModel` and `TracksTableModel`) with filtering, status coloring, exports, and hooks for PDF/waveform viewers.
- Exports use `services.export_service.export_results_to_json` to write timestamped JSON summaries, preserving file paths and per-side metrics for downstream reporting.

## Important Constraints
- Vision model calls require `OPENROUTER_API_KEY`; without it the VLM adapter operates in a no-op mode and yields empty results, so callers must handle the empty-track path gracefully.
- WAV archives must be ZIP files with safe member names; entries containing empty parts or traversal segments are skipped to avoid unsafe extraction.
- Tolerance thresholds (`ToleranceSettings`) drive warn/fail status in both services and UI; defaults are 2 seconds (warn) and 5 seconds (fail) and should remain configurable via settings.
- Qt assets (fonts/icons) must be registered through the resource helper (`ui._icons_rc`); missing brand fonts fall back to system defaults but should be bundled for production.
- Automated environments run headless; set `QT_QPA_PLATFORM=offscreen` and avoid modal dialogs that block when no display server exists.

## External Dependencies
- OpenRouter API (via the `openai` client) for vision-language track extraction.
- PyMuPDF (`fitz`) and Pillow for PDF rasterization.
- SoundFile/Libsndfile with built-in `wave` fallback for audio duration probing.
- PyQt6 (plus PyQtGraph for waveform features), Qt runtime libraries, and supporting system packages such as `xvfb`/`libgl` for Linux CI.
- `python-dotenv` for environment loading, `numpy` for synthesized audio fixtures, and `pytest-qt`/`pytest-mock` for testing utilities.

``n
### README.md

``n# Tracklist Extractor

Desktop quality-control tool for pairing cue sheet PDFs with WAV masters. The application renders PDFs, invokes a vision-language model to extract structured track metadata, compares durations against WAV bundles, and surfaces discrepancies inside a PyQt6 UI.

## Key Components

- **Domain & Services**: `core/` encapsulates models and comparison logic, `services/` orchestrate end-to-end analysis and exports.
- **Adapters**: `adapters/` provide infrastructure for AI calls, PDF rendering, filesystem discovery, and audio probing. Waveform helpers now rely on `WavInfo.apply_parsed_info()` for encapsulated updates.
- **UI**: `ui/` contains the PyQt6 interface. `MainWindow` receives typed settings and worker dependencies; settings widgets emit `settingChanged`/`saveRequested` signals instead of mutating configuration directly.
- **Configuration**: `ConfigLoader` in `config.py` is the authoritative factory for typed settings (`LlmSettings`, `UiSettings`, `AnalysisSettings`, `PathSettings`, etc.). Global `cfg` remains for legacy access but new code should consume loader outputs or dataclasses.
- **Status Handling**: Comparison results use `core.domain.analysis_status.AnalysisStatus` (`OK`, `WARN`, `FAIL`) with helpers for severity, icon, and theme lookup. UI models render enum values and colors accordingly.

## Development Workflow

1. Install dependencies (`pip install -r requirements.txt`).
2. Run lint and tests via `tools/check.sh` or manually (`black`, `ruff`, `mypy`, `pytest`).
3. Use `openspec` to author proposals and keep specs up to date (`openspec validate <change-id> --strict`).
4. Launch the app with `python app.py` (Qt will look for `settings.json` in the working directory).

## Configuration Notes

- Persisted settings live in Qt `QSettings` (`GZMedia/TracklistExtractor`). `ConfigLoader` reads them and constructs typed dataclasses shared across the app.
- Settings UI is signal-driven; parent dialogs handle persistence via `ConfigLoader` and `AppConfig.set`.
- Auto-export paths and tolerances are configurable; JSON exports include enum-backed statuses serialized as strings.

## Tests

- Unit and integration tests reside in `tests/`. GUI tests use `pytest-qt` fixtures (`qapp`, `qtbot`).
- Golden comparison fixtures in `tests/data/golden/` validate analyzer behaviour.

## Changelog Highlights

- Removed legacy `fluent_gui.py` wrapper; all imports now target authoritative modules.
- Introduced modular config dataclasses, `ConfigLoader`, and signal-based settings UI.
- Added `WavInfo.apply_parsed_info()` to enforce encapsulation in audio helpers.
- Replaced status string literals with `AnalysisStatus` enum across domain, UI, and exports.

``n
### tests\README.md

``n# Waveform Test Suite

## Overview

This directory contains the automated tests for the waveform viewer feature. The suite is organised into the following categories:

- **Unit tests** (`test_waveform_viewer.py`) verify the behaviour of `WaveformViewerDialog`.
- **Unit tests** (`test_waveform_editor.py`) cover `WaveformEditorDialog`, including region selection, snapping, and marker handling.
- **Integration tests** (`test_waveform_integration.py`) exercise the GUI workflow inside `fluent_gui.MainWindow`.
- **Configuration tests** (`test_waveform_config.py`) validate configuration defaults and the settings UI.
- **Shared fixtures** (`conftest.py`) provide reusable helpers for Qt applications, configuration isolation, and sample media assets.

## Running Tests

Execute the entire test suite:

```bash
pytest
```

Run a specific file:

```bash
pytest tests/test_waveform_viewer.py
```

Filter by marker:

```bash
pytest -m unit
```

Generate coverage:

```bash
pytest --cov=. --cov-report=html
```

Enable verbose output:

```bash
pytest -v
```

## Fixtures

- **`qapp`**: Session-scoped `QApplication` instance for Qt tests.
- **`isolated_config`**: Temporary configuration using in-memory QSettings.
- **`mock_wav_zip`**: Creates a ZIP archive containing a valid WAV sine wave for playback tests.
- **`empty_zip`** / **`invalid_wav_zip`**: Provide error-condition archives for robustness scenarios.

## Writing New Tests

- Use pytest-qt's `qtbot` fixture to interact with widgets and simulate user actions.
- Patch Qt signals or multimedia APIs with `unittest.mock` for deterministic behaviour.
- Group related tests inside `Test*` classes and follow the `test_*` naming convention.

## Troubleshooting

- Set `QT_QPA_PLATFORM=offscreen` when running headless (e.g. CI servers).
- Ensure optional dependencies (`pyqtgraph`, `soundfile`, Qt multimedia) are installed for waveform tests.
- If tests hang, verify a single global `QApplication` instance is active.

## Coverage Goals

- Target 80%+ coverage for `waveform_viewer.py`.
- Critical paths to exercise:
  - Both `WaveformViewerDialog` and `WaveformEditorDialog` initialization flows
  - Audio extraction from ZIP archives
  - Waveform rendering and downsampling logic
  - Playback controls (play, pause, stop, seek)
  - Region selection and snapping (editor only)
  - PDF marker visualization (editor only)
  - Volume control interactions
- Error handling for missing or invalid files
- Resource cleanup on dialog close

## Known Issues (Fixed)

The following issues were identified during code review and have been fixed:

1. **Missing `Dict` import**: Added to typing imports in `waveform_viewer.py`.
2. **Duplicate `_temp_wav` definition**: Removed the redundant assignment in `WaveformEditorDialog`.
3. **`_format_time()` inconsistency**: Standardized to use milliseconds in `WaveformViewerDialog` while keeping seconds in the editor.
4. **Position line detection bug**: Replaced the overview line search with a dedicated instance reference.
5. **Unused variables**: Removed unused `time_axis` calculations in detail view updates.
6. **Magic numbers**: Promoted waveform-related constants to named module-level values.

``n

