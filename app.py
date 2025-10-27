import json
import sys
import os
from pathlib import Path
from typing import Optional

# Debug: Print the Python executable path to validate which Python is being used
print(f"Debug: Python executable: {sys.executable}")

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

from config import cfg, load_config, ConfigLoader
from ui.main_window import MainWindow
from ui.config_models import (
    load_tolerance_settings,
    load_id_extraction_settings,
    load_export_settings,
    load_theme_settings,
    load_worker_settings,
)
from ui.workers.worker_manager import AnalysisWorkerManager
from ui.theme import load_gz_media_fonts, load_gz_media_stylesheet
import ui._icons_rc  # Import Qt resources for icons (registers search paths)
from ui.constants import SETTINGS_FILENAME
from adapters.ui.null_waveform_viewer import NullWaveformViewer

if os.environ.get("QT_QPA_PLATFORM") in {"offscreen", "minimal"}:
    fonts_dir = Path(__file__).resolve().parent / "fonts"
    if fonts_dir.exists():
        for font_path in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_path))


def main(config_path: Optional[Path] = None):
    """
    Entry point for the application. Assembles and launches the UI with dependency injection.
    """
    if config_path is None:
        env_path = os.getenv("TRACKLIST_CONFIG")
        config_path = Path(env_path) if env_path else SETTINGS_FILENAME
    else:
        config_path = Path(config_path)

    scale_value = None
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            ui_section = data.get("ui", {})
            scale_value = ui_section.get("dpi_scale", "AUTO")
        except Exception:
            scale_value = None

    if hasattr(Qt, "ApplicationAttribute") and hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "ApplicationAttribute") and hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    if isinstance(scale_value, (int, float)) and float(scale_value) not in (0.0, 1.0):
        os.environ.setdefault("QT_SCALE_FACTOR", str(scale_value))
    elif isinstance(scale_value, str):
        value = scale_value.strip()
        if value and value.upper() != "AUTO":
            os.environ.setdefault("QT_SCALE_FACTOR", value)

    app = QApplication(sys.argv)

    load_config(config_path)
    config_loader = ConfigLoader(cfg.settings)

    tolerance_settings = load_tolerance_settings(loader=config_loader)
    id_extraction_settings = load_id_extraction_settings(loader=config_loader)
    export_settings = load_export_settings(loader=config_loader)
    theme_settings = load_theme_settings(loader=config_loader)
    worker_settings = load_worker_settings(loader=config_loader)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )
    load_gz_media_fonts(app, font_family=theme_settings.font_family, font_size=theme_settings.font_size)
    load_gz_media_stylesheet(app, stylesheet_path=theme_settings.stylesheet_path)

    window = MainWindow(
        tolerance_settings=tolerance_settings,
        export_settings=export_settings,
        theme_settings=theme_settings,
        waveform_viewer=NullWaveformViewer(),
        worker_manager=worker_manager,
        settings_filename=config_path,
        app_config=cfg,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
