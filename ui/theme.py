import logging
import sys
from pathlib import Path
from typing import Dict

from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QStyle


# Icon cache for performance
_icon_cache: Dict[str, QIcon] = {}


def get_asset_path(relative_path: Path) -> Path:
    """Get absolute path to asset, supporting both development and bundled app (PyInstaller)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in a normal Python environment
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path


def get_custom_icon(icon_name: str) -> QIcon:
    """Load a custom SVG icon with caching, resource lookup, and system fallback.

    Args:
        icon_name: Name of the icon without extension (e.g., 'check', 'cross', 'play')

    Returns:
        QIcon object, system fallback, or empty QIcon if not found.
    """
    if icon_name in _icon_cache:
        return _icon_cache[icon_name]

    # 1. Try loading from filesystem (dev or bundled app)
    try:
        icon_path = get_asset_path(Path("assets") / "icons" / f"{icon_name}.svg")
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                logging.debug(f"Loaded icon '{icon_name}' from filesystem: {icon_path}")
                _icon_cache[icon_name] = icon
                return icon

        logging.warning(f"Custom icon file not found at: {icon_path}, using fallback.")

    except Exception as exc:
        logging.error(f"Error loading custom icon '{icon_name}' from filesystem: {exc}")

    # 2. If filesystem fails, use a system fallback icon
    fallback_icon = _get_fallback_icon(icon_name)
    if not fallback_icon.isNull():
        logging.warning(f"Using fallback for icon '{icon_name}'.")
        _icon_cache[icon_name] = fallback_icon  # Cache the fallback too
        return fallback_icon

    logging.error(f"Failed to load icon or find fallback for '{icon_name}'.")
    _icon_cache[icon_name] = QIcon()  # Cache the empty icon to prevent repeated lookups
    return _icon_cache[icon_name]


def _get_fallback_icon(icon_name: str) -> QIcon:
    """Get fallback system icon for the given icon name."""
    try:
        app = QApplication.instance()
        if not app:
            return QIcon()

        style = app.style()

        # Map icon names to system pixmaps
        fallback_mapping = {
            "check": QStyle.StandardPixmap.SP_DialogApplyButton,
            "cross": QStyle.StandardPixmap.SP_DialogCancelButton,
            "play": QStyle.StandardPixmap.SP_MediaPlay,
        }

        if icon_name in fallback_mapping:
            fallback_icon = style.standardIcon(fallback_mapping[icon_name])
            if not fallback_icon.isNull():
                logging.debug(f"Using fallback icon for: {icon_name}")
                return fallback_icon

        logging.warning(f"No fallback available for icon: {icon_name}")
        return QIcon()

    except Exception as exc:
        logging.error(f"Error getting fallback icon for '{icon_name}': {exc}")
        return QIcon()


def get_system_file_icon(icon_type: str = "file") -> QIcon:
    """Return a standard system icon for files, directories, or actions, with support for custom SVG icons."""
    # Support custom SVG icons for specific types
    if icon_type in ["check", "cross", "play"]:
        return get_custom_icon(icon_type)

    # Fallback to system icons for backward compatibility
    try:
        app = QApplication.instance()
        if not app:
            return QIcon()

        style = app.style()
        mapping = {
            "file": QStyle.StandardPixmap.SP_FileIcon,
            "dir": QStyle.StandardPixmap.SP_DirIcon,
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
