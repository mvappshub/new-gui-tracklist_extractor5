from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToleranceSettings:
    """Duration comparison thresholds controlling WARN and FAIL classifications."""

    warn_tolerance: int
    fail_tolerance: int


@dataclass
class ExportSettings:
    """Settings defining automatic export behaviour."""

    auto_export: bool
    export_dir: Path


@dataclass
class IdExtractionSettings:
    """Settings controlling numeric ID extraction from filenames."""

    min_digits: int
    max_digits: int
    ignore_numbers: list[str]


@dataclass
class LlmSettings:
    """LLM configuration shared across adapters and UI."""

    base_url: str
    model: str
    temperature: float
    alt_models: list[str] = field(default_factory=list)


@dataclass
class AnalysisSettings:
    """Aggregated analysis configuration for tolerance and identifier parsing."""

    tolerance_warn: int
    tolerance_fail: int
    min_id_digits: int
    max_id_digits: int
    ignore_numbers: list[str] = field(default_factory=list)


@dataclass
class PathSettings:
    """Filesystem locations used by the application pipeline."""

    pdf_dir: Path
    wav_dir: Path
    export_dir: Path


@dataclass
class UiSettings:
    """UI configuration that informs theme loading and runtime behaviour."""

    dpi_scale: str | float
    theme: str
    window_geometry: str
    base_font_family: str
    base_font_size: int
    heading_font_size: int
    treeview_row_height: int
    status_colors: dict[str, str] = field(default_factory=dict)
    action_row_bg_color: str = "#E0E7FF"
    total_row_bg_color: str = "#F3F4F6"
    claim_visible: bool = True
    claim_text: str = "Emotions. Materialized."
    logo_path: Path = Path("assets/gz_logo_white.png")


@dataclass
class PromptSettings:
    """Prompt text blocks used by PDF + VLM extraction."""

    primary: str
    user_instructions: str = ""


@dataclass
class WorkerSettings:
    """Worker configuration injected into background analysis threads."""

    pdf_dir: Path
    wav_dir: Path


@dataclass
class ThemeSettings:
    """Theme configuration consumed by Qt widgets."""

    font_family: str
    font_size: int
    stylesheet_path: Path
    status_colors: dict[str, str]
    logo_path: Path
    claim_visible: bool
    claim_text: str
    action_bg_color: str
    total_row_bg_color: str
