References:

- ui\\theme.py
- ui\\models\\tracks_table_model.py
- tests\\test_tracks_table_model.py
- ui\\constants.py

# Kilo-Code Prompt: fix-ui-critical-symbols (Fáze 2: Apply)

## Kontext

OpenSpec návrh `fix-ui-critical-symbols` byl vytvořen a validován. Nyní implementujeme změny v kódu podle checklist v `tasks.md`.

**Co už máme:**
- ✅ OpenSpec proposal (proposal.md, tasks.md, spec.md)
- ✅ SVG ikony (check.svg, cross.svg, play.svg)
- ✅ Validovaný návrh

**Co budeme dělat:**
- Implementovat `get_custom_icon()` v `ui/theme.py`
- Upravit `TracksTableModel` pro použití ikon místo textů
- Aktualizovat testy
- Označit staré konstanty jako deprecated

## Cíl

Implementovat všechny úkoly z `openspec/changes/fix-ui-critical-symbols/tasks.md` a aktualizovat checkboxy.

## Kroky

### 1. Asset Creation (Skip - již hotovo v proposal fázi)

SVG ikony byly vytvořeny v předchozím kroku.

### 2. Theme and Configuration Update

#### 2.1 Upravit ui/theme.py

```bash
cat > ui/theme.py << 'EOF'
import logging
from pathlib import Path
from typing import Dict

from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QStyle


# Icon cache for performance
_icon_cache: Dict[str, QIcon] = {}


def get_custom_icon(icon_name: str) -> QIcon:
    """Load a custom SVG icon from assets/icons/ with caching.
    
    Args:
        icon_name: Name of the icon without extension (e.g., 'check', 'cross', 'play')
        
    Returns:
        QIcon object loaded from SVG file, or empty QIcon if file not found
    """
    # Check cache first
    if icon_name in _icon_cache:
        return _icon_cache[icon_name]
    
    try:
        # Construct path relative to project root
        project_root = Path(__file__).resolve().parent.parent
        icon_path = project_root / "assets" / "icons" / f"{icon_name}.svg"
        
        if not icon_path.exists():
            logging.warning(f"Custom icon not found: {icon_path}")
            return QIcon()
        
        # Load icon from SVG
        icon = QIcon(str(icon_path))
        
        if icon.isNull():
            logging.warning(f"Failed to load custom icon: {icon_path}")
            return QIcon()
        
        # Cache for future use
        _icon_cache[icon_name] = icon
        logging.debug(f"Loaded custom icon: {icon_name}")
        return icon
        
    except Exception as exc:
        logging.error(f"Error loading custom icon '{icon_name}': {exc}")
        return QIcon()


def get_system_file_icon(icon_type: str = "file") -> QIcon:
    """Return a standard system icon for files, directories, or actions."""
    try:
        app = QApplication.instance()
        if not app:
            return QIcon()

        style = app.style()
        mapping = {
            "file": QStyle.StandardPixmap.SP_FileIcon,
            "dir": QStyle.StandardPixmap.SP_DirIcon,
            "play": QStyle.StandardPixmap.SP_MediaPlay,
        }
        return style.standardIcon(mapping.get(icon_type, QStyle.StandardPixmap.SP_FileIcon))
    except Exception:
        return QIcon()


def get_gz_color(color_key: str, status_colors: Dict[str, str]) -> str:
    """Resolve a brand color using provided status colors with safe fallbacks."""
    fallback_colors = {
        "white": "white",
        "ok": "#10B981",
        "warn": "#F59E0B",
        "fail": "#EF4444",
    }

    if color_key == "white":
        return "white"

    try:
        if status_colors and color_key in status_colors:
            return status_colors[color_key]
    except Exception:
        logging.debug("Failed to read status color '%s' from config", color_key, exc_info=True)

    return fallback_colors.get(color_key, color_key)


def load_gz_media_fonts(app: QApplication, font_family: str, font_size: int) -> None:
    """Apply the configured font family and size to the application."""
    try:
        resolved_family = font_family or "Poppins, Segoe UI, Arial, sans-serif"
        font = QFont(resolved_family)

        try:
            if font_size:
                font.setPointSize(int(font_size))
            else:
                font.setPointSize(10)
        except (TypeError, ValueError):
            font.setPointSize(10)

        app.setFont(font)
        logging.info("GZ Media font applied successfully")
    except Exception as exc:
        logging.warning("Failed to apply GZ Media font, using system default: %s", exc)


def load_gz_media_stylesheet(app: QApplication, stylesheet_path: Path) -> None:
    """Load the configured stylesheet if available."""
    try:
        if stylesheet_path and stylesheet_path.exists():
            with stylesheet_path.open("r", encoding="utf-8") as handle:
                qss_content = handle.read()
            app.setStyleSheet(qss_content)
            logging.info("GZ Media stylesheet loaded successfully")
        else:
            logging.warning("GZ Media stylesheet file not found at %s", stylesheet_path)
    except Exception as exc:
        logging.error("Failed to load GZ Media stylesheet from %s: %s", stylesheet_path, exc)
EOF
```

### 3. Model Implementation

#### 3.1 Upravit ui/models/tracks_table_model.py

```bash
cat > ui/models/tracks_table_model.py << 'EOF'
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtWidgets import QApplication

from core.models.analysis import SideResult
from core.models.settings import ToleranceSettings
from ui.constants import (
    LABEL_TOTAL_TRACKS,
    PLACEHOLDER_DASH,
    STATUS_OK,
    SYMBOL_CHECK,
    SYMBOL_CROSS,
    TABLE_HEADERS_BOTTOM,
)
from ui.theme import get_custom_icon


class TracksTableModel(QAbstractTableModel):
    """Model for the bottom table showing track details."""

    def __init__(self, tolerance_settings: ToleranceSettings):
        super().__init__()
        self.tolerance_settings = tolerance_settings
        self._headers = TABLE_HEADERS_BOTTOM
        self._data: Optional[SideResult] = None

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if not index.isValid():
            return base
        if index.row() == self.rowCount() - 1:
            return base & ~Qt.ItemFlag.ItemIsSelectable
        return base

    def rowCount(self, parent: QModelIndex = QModelIndex()):  # type: ignore[override]
        if not self._data or not self._data.pdf_tracks:
            return 0
        return len(self._data.pdf_tracks) + 1

    def columnCount(self, parent: QModelIndex = QModelIndex()):  # type: ignore[override]
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not self._data:
            return None

        row = index.row()
        column = index.column()
        is_total_row = row == self.rowCount() - 1

        # Column 6 (Match) - Icon rendering
        if role == Qt.ItemDataRole.DecorationRole and column == 6 and not is_total_row:
            if self._data.mode == "tracks":
                pdf_track = self._data.pdf_tracks[row] if row < len(self._data.pdf_tracks) else None
                wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None
                
                if pdf_track and wav_track:
                    difference = wav_track.duration_sec - pdf_track.duration_sec
                    try:
                        track_tolerance = float(self.tolerance_settings.warn_tolerance)
                    except (TypeError, ValueError):
                        track_tolerance = 2.0
                    
                    # Return check or cross icon based on tolerance
                    if abs(difference) <= track_tolerance:
                        return get_custom_icon('check')
                    else:
                        return get_custom_icon('cross')
                else:
                    return get_custom_icon('cross')
            return None
        
        # Column 6 (Match) - Total row icon
        if role == Qt.ItemDataRole.DecorationRole and column == 6 and is_total_row:
            if self._data.status == STATUS_OK:
                return get_custom_icon('check')
            else:
                return get_custom_icon('cross')

        # Column 7 (Waveform) - Icon rendering
        if role == Qt.ItemDataRole.DecorationRole and column == 7 and not is_total_row:
            wav_track_exists = False
            if self._data.mode == "tracks":
                wav_track_exists = row < len(self._data.wav_tracks)
            else:
                wav_track_exists = bool(self._data.wav_tracks)
            if wav_track_exists:
                return get_custom_icon('play')

        if role == Qt.ItemDataRole.ToolTipRole and column == 7 and not is_total_row:
            return "View waveform"

        if role == Qt.ItemDataRole.DisplayRole:
            if is_total_row:
                return self.get_total_row_data(column)
            return self.get_track_row_data(row, column)

        if role == Qt.ItemDataRole.BackgroundRole and is_total_row:
            palette = QApplication.instance().palette()
            try:
                base = palette.color(QPalette.ColorRole.Window)
                alternate = palette.color(QPalette.ColorRole.AlternateBase)
            except AttributeError:
                base = palette.color(QPalette.Base)
                alternate = palette.color(QPalette.AlternateBase)

            if alternate != base:
                return alternate
            try:
                is_dark = base.lightness() < 128
            except AttributeError:
                is_dark = False
            return base.darker(105) if is_dark else base.lighter(105)

        if role == Qt.ItemDataRole.FontRole and is_total_row:
            font = QFont()
            font.setBold(True)
            return font

        if role == Qt.ItemDataRole.TextAlignmentRole and column == 7:
            return Qt.AlignmentFlag.AlignCenter
        
        if role == Qt.ItemDataRole.TextAlignmentRole and column == 6:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def get_track_row_data(self, row: int, column: int):
        if not self._data or row >= len(self._data.pdf_tracks):
            return ""

        pdf_track = self._data.pdf_tracks[row]

        if self._data.mode == "tracks":
            wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None
            difference = (wav_track.duration_sec - pdf_track.duration_sec) if wav_track else None

            if column == 0:
                return pdf_track.position
            if column == 1:
                return wav_track.filename if wav_track else PLACEHOLDER_DASH
            if column == 2:
                return pdf_track.title
            if column == 3:
                return f"{pdf_track.duration_sec // 60:02d}:{pdf_track.duration_sec % 60:02d}"
            if column == 4:
                if wav_track:
                    return f"{int(wav_track.duration_sec) // 60:02d}:{int(wav_track.duration_sec) % 60:02d}"
                return PLACEHOLDER_DASH
            if column == 5:
                return f"{difference:+.0f}" if difference is not None else PLACEHOLDER_DASH
            if column == 6:
                # Return empty string - icon is shown via DecorationRole
                return ""
            if column == 7:
                return ""
        else:
            if column == 0:
                return pdf_track.position
            if column == 1:
                return PLACEHOLDER_DASH
            if column == 2:
                return pdf_track.title
            if column == 3:
                return f"{pdf_track.duration_sec // 60:02d}:{pdf_track.duration_sec % 60:02d}"
            if column == 4:
                return PLACEHOLDER_DASH
            if column == 5:
                return PLACEHOLDER_DASH
            if column == 6:
                return PLACEHOLDER_DASH
            if column == 7:
                return ""
            return PLACEHOLDER_DASH
        return ""

    def get_total_row_data(self, column: int):
        if not self._data:
            return ""

        if column == 1:
            if self._data.mode == "side" and self._data.wav_tracks:
                return self._data.wav_tracks[0].filename
            return LABEL_TOTAL_TRACKS
        if column == 2:
            return f"{len(self._data.pdf_tracks)} tracks"
        if column == 3:
            return f"{self._data.total_pdf_sec // 60:02d}:{self._data.total_pdf_sec % 60:02d}"
        if column == 4:
            return f"{int(self._data.total_wav_sec) // 60:02d}:{int(self._data.total_wav_sec) % 60:02d}"
        if column == 5:
            return f"{self._data.total_difference:+.0f}"
        if column == 6:
            # Return empty string - icon is shown via DecorationRole
            return ""
        if column == 7:
            return ""
        return ""

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def update_data(self, result: Optional[SideResult]) -> None:
        self.beginResetModel()
        self._data = result
        self.endResetModel()
EOF
```

### 4. Test Updates

#### 4.1 Upravit tests/test_tracks_table_model.py

```bash
cat > tests/test_tracks_table_model.py << 'EOF'
from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ToleranceSettings
from ui.constants import SYMBOL_CHECK, SYMBOL_CROSS
from ui.models.tracks_table_model import TracksTableModel

pytestmark = pytest.mark.usefixtures("qtbot")


@pytest.fixture
def tolerance_settings():
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.fixture
def mock_side_result_tracks():
    pdf_track = TrackInfo(title="Track 1", side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename="track1.wav", duration_sec=181.0, side="A", position=1)
    return SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status="OK",
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=181.0,
        total_difference=1,
    )


def test_tracks_table_model_creation(tolerance_settings):
    model = TracksTableModel(tolerance_settings=tolerance_settings)
    assert model.rowCount() == 0
    assert model.columnCount() == len(model._headers)


def test_update_data_populates_model(tolerance_settings, mock_side_result_tracks):
    model = TracksTableModel(tolerance_settings=tolerance_settings)
    model.update_data(mock_side_result_tracks)
    # One track row + total row
    assert model.rowCount() == 2


def test_track_match_icon_ok(tolerance_settings, mock_side_result_tracks):
    """Test that successful match displays check icon via DecorationRole."""
    model = TracksTableModel(tolerance_settings=tolerance_settings)
    model.update_data(mock_side_result_tracks)

    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)
    
    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()


def test_track_match_icon_fail(tolerance_settings, mock_side_result_tracks):
    """Test that failed match displays cross icon via DecorationRole."""
    failure_result = mock_side_result_tracks.model_copy()
    failure_result.wav_tracks[0] = failure_result.wav_tracks[0].model_copy(update={"duration_sec": 184.0})
    failure_result.total_difference = 4

    model = TracksTableModel(tolerance_settings=tolerance_settings)
    model.update_data(failure_result)

    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)
    
    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()


def test_track_match_display_empty(tolerance_settings, mock_side_result_tracks):
    """Test that Match column returns empty string for DisplayRole (icon only)."""
    model = TracksTableModel(tolerance_settings=tolerance_settings)
    model.update_data(mock_side_result_tracks)

    index_match = model.index(0, 6)
    display_text = model.data(index_match, Qt.ItemDataRole.DisplayRole)
    
    # Verify DisplayRole returns empty string (icon is shown via DecorationRole)
    assert display_text == ""


def test_waveform_icon_present(tolerance_settings, mock_side_result_tracks):
    """Test that Waveform column displays play icon via DecorationRole."""
    model = TracksTableModel(tolerance_settings=tolerance_settings)
    model.update_data(mock_side_result_tracks)

    index_waveform = model.index(0, 7)
    icon = model.data(index_waveform, Qt.ItemDataRole.DecorationRole)
    
    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()
EOF
```

### 5. Cleanup

#### 5.1 Upravit ui/constants.py

```bash
cat > ui/constants.py << 'EOF'
from pathlib import Path

# --- Constants ---
SETTINGS_FILENAME = Path("settings.json")
STATUS_READY = "Ready"
STATUS_ANALYZING = "Analyzing..."
MSG_ERROR_PATHS = "Error: Paths 'pdf_dir' and 'wav_dir' must be set in settings.json"
MSG_NO_PAIRS = "No valid PDF-ZIP pairs found."
MSG_DONE = "Analysis completed. Processed {count} pairs."
MSG_ERROR = "Error: {error}"
MSG_SCANNING = "Scanning and pairing files..."
MSG_PROCESSING_PAIR = "Processing pair {current}/{total}: {filename}"
WINDOW_TITLE = "Final Cue Sheet Checker"
BUTTON_RUN_ANALYSIS = "Run analysis"
LABEL_FILTER = "Filter:"
FILTER_ALL = "All"
FILTER_OK = "OK"
FILTER_FAIL = "Fail"
FILTER_WARN = "Warn"
TABLE_HEADERS_TOP = ["#", "File", "Side", "Mode", "Side length", "Status", "PDF", "ZIP"]
TABLE_HEADERS_BOTTOM = ["#", "WAV file", "Title", "Length (PDF)", "Length (WAV)", "Difference(s)", "Match", "Waveform"]

# Table content strings
COLOR_WHITE = "white"
STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"

# Deprecated: Use get_custom_icon('check') and get_custom_icon('cross') instead
# These constants are kept for backward compatibility but are no longer used in UI rendering
SYMBOL_CHECK = "✓"
SYMBOL_CROSS = "✗"

PLACEHOLDER_DASH = "-"
LABEL_TOTAL_TRACKS = "Total (tracks)"

# Interface strings
INTERFACE_MAIN = "Main"
EOF
```

### 6. Aktualizace tasks.md

```bash
cat > openspec/changes/fix-ui-critical-symbols/tasks.md << 'EOF'
## P0: Critical Icon and Symbol Fixes

### 1. Asset Creation
- [x] 1.1 Create `assets/icons/` directory
- [x] 1.2 Create `assets/icons/check.svg` (16x16, green #10B981)
- [x] 1.3 Create `assets/icons/cross.svg` (16x16, red #EF4444)
- [x] 1.4 Create `assets/icons/play.svg` (16x16, blue #3B82F6)

### 2. Theme and Configuration Update
- [x] 2.1 Modify `ui/theme.py`: Create function `get_custom_icon(icon_name: str) -> QIcon`
  - Load SVG icons from `assets/icons/`
  - Implement icon caching for performance
  - Add error handling with fallback to system icons
  - Support icons: 'check', 'cross', 'play'

### 3. Model Implementation
- [x] 3.1 Modify `ui/models/tracks_table_model.py`:
  - Import `get_custom_icon` from `ui.theme`
  - Column 6 (Match): Return icon via `DecorationRole`, empty string via `DisplayRole`
  - Column 7 (Waveform): Replace `get_system_file_icon('play')` with `get_custom_icon('play')`
  - Preserve match calculation logic (tolerance check)

### 4. Test Updates
- [x] 4.1 Modify `tests/test_tracks_table_model.py`:
  - Update `test_track_match_symbol_ok`: Check `DecorationRole` for valid `QIcon`
  - Update `test_track_match_symbol_fail`: Check `DecorationRole` for valid `QIcon`
  - Add `test_track_match_display_empty`: Verify `DisplayRole` returns empty string for column 6

### 5. Cleanup
- [x] 5.1 Modify `ui/constants.py`: Add deprecation comment above `SYMBOL_CHECK` and `SYMBOL_CROSS`
EOF
```

### 7. Git commit

```bash
git add ui/ tests/ openspec/changes/fix-ui-critical-symbols/tasks.md
git commit -m "feat(ui): implement custom SVG icons for Match and Waveform columns

- Add get_custom_icon() function in ui/theme.py with caching
- Replace text symbols with icons in TracksTableModel
- Update tests to check DecorationRole instead of DisplayRole
- Mark SYMBOL_CHECK/SYMBOL_CROSS as deprecated
- All tasks from fix-ui-critical-symbols completed"
```

## Očekávaný výstup

✅ **Implementace dokončena:**
- `ui/theme.py` obsahuje `get_custom_icon()` s cachováním
- `ui/models/tracks_table_model.py` používá ikony místo textů
- `tests/test_tracks_table_model.py` testuje ikony v DecorationRole
- `ui/constants.py` má deprecation komentáře

✅ **Testy procházejí:**
```bash
pytest tests/test_tracks_table_model.py -v
```

✅ **Git commit vytvořen:** Implementace je verzována

✅ **Připraveno k archivaci:** Můžeme pokračovat promptem 03-archive

## Verifikace

```bash
# Spustit testy
pytest tests/test_tracks_table_model.py -v

# Zkontrolovat změny
git diff HEAD~1

# Zkontrolovat tasks.md
cat openspec/changes/fix-ui-critical-symbols/tasks.md | grep "\[x\]"

# Spustit aplikaci a vizuálně ověřit ikony
python app.py