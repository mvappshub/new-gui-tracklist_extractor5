from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from config import AppConfig, ConfigLoader
from core.models.settings import (
    ExportSettings,
    IdExtractionSettings,
    PathSettings,
    ThemeSettings,
    ToleranceSettings,
    WorkerSettings,
)

# NOTE: Only application entry points should import the global cfg object.
# Other layers construct settings via these dataclasses and receive them via DI.


def _ensure_loader(cfg: Optional[AppConfig] = None, loader: Optional[ConfigLoader] = None) -> ConfigLoader:
    if loader is not None:
        return loader
    if cfg is not None:
        return ConfigLoader(cfg.settings)
    return ConfigLoader()


def load_tolerance_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> ToleranceSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_tolerance_settings()


def load_export_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> ExportSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_export_settings()


def load_path_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> PathSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_path_settings()


def load_id_extraction_settings(
    cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None
) -> IdExtractionSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_id_extraction_settings()


def load_theme_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> ThemeSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_theme_settings()


def load_worker_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> WorkerSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_worker_settings()
