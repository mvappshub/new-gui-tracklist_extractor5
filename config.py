from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from PyQt6.QtCore import QSettings

from core.models.settings import (
    AnalysisSettings,
    ExportSettings,
    IdExtractionSettings,
    LlmSettings,
    PathSettings,
    PromptSettings,
    ThemeSettings,
    ToleranceSettings,
    UiSettings,
    WorkerSettings,
)

DEFAULT_SETTINGS_ORG = "GZMedia"
DEFAULT_SETTINGS_APP = "TracklistExtractor"

DEFAULT_LLM_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_LLM_MODEL = "google/gemini-2.5-flash"
DEFAULT_LLM_TEMPERATURE = 0.0

AVAILABLE_LLM_MODELS = [
    "google/gemini-2.5-flash",
    "qwen/qwen2.5-vl-72b-instruct",
    "anthropic/claude-3-haiku",
    "qwen/qwen2.5-vl-3b-instruct",
    "nousresearch/nous-hermes-2-vision-7b",
    "moonshotai/kimi-vl-a3b-thinking",
    "google/gemini-flash-1.5",
    "qwen/qwen2.5-vl-32b-instruct",
    "opengvlab/internvl3-14b",
    "openai/gpt-4o",
    "mistralai/pixtral-12b",
    "microsoft/phi-4-multimodal-instruct",
    "meta-llama/llama-3.2-90b-vision-instruct",
    "meta-llama/llama-3.2-11b-vision-instruct",
    "google/gemini-pro-1.5",
    "google/gemini-2.5-pro",
    "google/gemini-2.0-flash-001",
    "fireworks/firellava-13b",
    "bytedance/ui-tars-1.5-7b",
    "bytedance-research/ui-tars-72b",
    "baidu/ernie-4.5-vl-424b-a47b",
    "baidu/ernie-4.5-vl-28b-a3b",
    "01-ai/yi-vision",
    "z-ai/glm-4.5v",
    "x-ai/grok-2-vision-1212",
]
DEFAULT_ALT_LLM_MODELS = AVAILABLE_LLM_MODELS[1:]

AVAILABLE_DPI_SCALES: List[Union[float, str]] = [1, 1.25, 1.5, 1.75, 2, "AUTO"]

DEFAULT_INPUT_DIR = "./data"
DEFAULT_PDF_DIR = "./data/pdf"
DEFAULT_WAV_DIR = "./data/wav"
DEFAULT_EXPORT_DIR = "exports"

DEFAULTS: Dict[str, Any] = {
    "llm/base_url": DEFAULT_LLM_BASE_URL,
    "llm/model": DEFAULT_LLM_MODEL,
    "llm/alt_models": DEFAULT_ALT_LLM_MODELS,
    "llm/temperature": DEFAULT_LLM_TEMPERATURE,
    "extract/render_dpi": 380,
    "extract/max_side_px": 2000,
    "extract/image_format": "jpeg",
    "extract/jpeg_quality": 85,
    "extract/use_unsharp": True,
    "extract/use_autocontrast": True,
    "prompts/primary": (
        "You are a tracklist extractor. Your single purpose is to return STRICT JSON.\n"
        'Schema: { "tracks": [ {"title": string, "side": string, "position": integer, '
        '"duration_seconds": integer, "duration_formatted": "MM:SS" } ] }.\n'
        "Your entire logic is governed by this unbreakable rule:\n"
        "A track is anchored by its duration value (e.g., 4:40, 5m10s). The title is ALL meaningful text visually "
        "associated with that single time value. Combine multi-line text into one title.\n"
        "Follow these steps:\n"
        "Analyze Visual Layout: First, scan the entire image for structure. Identify columns, sections, and distinct visual blocks. "
        "Process multi-column layouts as separate lists.\n"
        "Find the Duration: For each potential track, locate the duration. This might be under a header like Time, Duration, or Length. "
        "If both Start/End times and a Length column exist, always prioritize the Length column.\n"
        "Establish Context: Use headers like SIDE A, Side B:, TAPE FLIP: A, or multi-track prefixes (A1, B-02) to determine the side "
        "and position. The prefix (B-02) is the most reliable source and overrides other context. Position numbering MUST reset for each new side.\n"
        "Strictly Filter: If a block of text has no clear, parsable duration anchored to it, it IS NOT a track. Aggressively ignore "
        "non-track lines: notes, pauses, headers, ISRC codes, credits, empty rows, and total runtimes."
    ),
    "prompts/user_instructions": "",
    "input/default_dir": DEFAULT_INPUT_DIR,
    "input/pdf_dir": DEFAULT_PDF_DIR,
    "input/wav_dir": DEFAULT_WAV_DIR,
    "export/default_dir": DEFAULT_EXPORT_DIR,
    "export/auto": True,
    "analysis/tolerance_warn": 2,
    "analysis/tolerance_fail": 5,
    "analysis/min_id_digits": 3,
    "analysis/max_id_digits": 6,
    "analysis/ignore_numbers": [],
    "ui/dpi_scale": "AUTO",
    "ui/theme": "AUTO",
    "ui/window_geometry": "1720x1440",
    "ui/base_font_family": "Poppins, Segoe UI, Arial, sans-serif",
    "ui/base_font_size": 13,
    "ui/heading_font_size": 12,
    "ui/treeview_row_height": 28,
    "ui/update_interval_ms": 50,
    "ui/table_action_bg_color": "#E0E7FF",
    "ui/total_row_bg_color": "#F3F4F6",
    "gz_brand/primary_blue": "#1E3A8A",
    "gz_brand/light_blue": "#3B82F6",
    "gz_brand/dark": "#1F2937",
    "gz_brand/light_gray": "#757575",
    "gz_brand/gray": "#6B7280",
    "gz_brand/logo_path": "assets/gz_logo_white.png",
    "gz_brand/claim_visible": True,
    "gz_brand/claim_text": "Emotions. Materialized.",
    "gz_status/ok_color": "#10B981",
    "gz_status/warn_color": "#F59E0B",
    "gz_status/fail_color": "#EF4444",
    "dark_mode/background": "#1F2937",
    "dark_mode/surface": "#374151",
    "dark_mode/text": "#F9FAFB",
    "dark_mode/text_secondary": "#D1D5DB",
    "dark_mode/accent": "#3B82F6",
}

ATTRIBUTE_KEY_MAP: Dict[str, str] = {
    "llm_model": "llm/model",
    "llm_base_url": "llm/base_url",
    "llm_alt_models": "llm/alt_models",
    "llm_temperature": "llm/temperature",
    "input_pdf_dir": "input/pdf_dir",
    "input_wav_dir": "input/wav_dir",
    "export_default_dir": "export/default_dir",
    "export_auto": "export/auto",
    "analysis_tolerance_warn": "analysis/tolerance_warn",
    "analysis_tolerance_fail": "analysis/tolerance_fail",
    "analysis_min_id_digits": "analysis/min_id_digits",
    "analysis_max_id_digits": "analysis/max_id_digits",
    "analysis_ignore_numbers": "analysis/ignore_numbers",
    "ui_dpi_scale": "ui/dpi_scale",
    "ui_theme": "ui/theme",
    "ui_window_geometry": "ui/window_geometry",
    "ui_base_font_family": "ui/base_font_family",
    "ui_base_font_size": "ui/base_font_size",
    "ui_heading_font_size": "ui/heading_font_size",
    "ui_treeview_row_height": "ui/treeview_row_height",
    "ui_update_interval_ms": "ui/update_interval_ms",
    "ui_table_action_bg_color": "ui/table_action_bg_color",
    "ui_total_row_bg_color": "ui/total_row_bg_color",
    "gz_logo_path": "gz_brand/logo_path",
    "gz_claim_visible": "gz_brand/claim_visible",
    "gz_claim_text": "gz_brand/claim_text",
    "gz_status_ok_color": "gz_status/ok_color",
    "gz_status_warn_color": "gz_status/warn_color",
    "gz_status_fail_color": "gz_status/fail_color",
}

SETTINGS_FILENAME = Path("settings.json")


def resolve_path(path: Union[str, Path]) -> Path:
    """Resolve a path relative to the project root directory."""

    if not path:
        return Path()
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj.resolve()
    project_root = Path(__file__).resolve().parent
    return (project_root / path_obj).resolve()


class ConfigValue:
    """Wrapper class for configuration values returning consistent types."""

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __repr__(self) -> str:
        return f"ConfigValue({self.value!r})"

    def __iter__(self):
        if isinstance(self.value, Iterable) and not isinstance(self.value, (str, bytes)):
            return iter(self.value)
        raise TypeError("Value is not iterable")


class ConfigLoader:
    """Factory that builds typed configuration dataclasses from QSettings."""

    def __init__(self, settings: Optional[QSettings] = None):
        self._settings = settings or QSettings(DEFAULT_SETTINGS_ORG, DEFAULT_SETTINGS_APP)

    def _value(self, key: str, default: Any = None) -> Any:
        if default is None and key in DEFAULTS:
            default = DEFAULTS[key]
        value = self._settings.value(key, default)
        if value is None:
            return default

        if isinstance(default, bool):
            if isinstance(value, bool):
                return value
            return str(value).lower() in {"true", "1", "yes", "on"}

        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        if isinstance(default, float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        if isinstance(default, list):
            if isinstance(value, list):
                return list(value)
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, TypeError, ValueError):
                    candidates = [item.strip() for item in value.split(",") if item.strip()]
                    if candidates:
                        return candidates
            return list(default)

        return value

    def load_llm_settings(self) -> LlmSettings:
        base_url = self._value("llm/base_url", DEFAULT_LLM_BASE_URL)
        model = self._value("llm/model", DEFAULT_LLM_MODEL)
        temperature = self._value("llm/temperature", DEFAULT_LLM_TEMPERATURE)
        alt_models = self._value("llm/alt_models", list(DEFAULT_ALT_LLM_MODELS))
        return LlmSettings(
            base_url=str(base_url),
            model=str(model),
            temperature=float(temperature),
            alt_models=[str(item) for item in alt_models],
        )

    def load_prompt_settings(self) -> PromptSettings:
        primary = self._value("prompts/primary", DEFAULTS["prompts/primary"])
        user_instructions = self._value("prompts/user_instructions", "")
        return PromptSettings(primary=str(primary), user_instructions=str(user_instructions))

    def load_path_settings(self) -> PathSettings:
        pdf_dir = Path(self._value("input/pdf_dir", DEFAULT_PDF_DIR))
        wav_dir = Path(self._value("input/wav_dir", DEFAULT_WAV_DIR))
        export_dir = Path(self._value("export/default_dir", DEFAULT_EXPORT_DIR))
        return PathSettings(pdf_dir=pdf_dir, wav_dir=wav_dir, export_dir=export_dir)

    def load_worker_settings(self) -> WorkerSettings:
        pdf_dir = Path(self._value("input/pdf_dir", DEFAULT_PDF_DIR))
        wav_dir = Path(self._value("input/wav_dir", DEFAULT_WAV_DIR))
        return WorkerSettings(pdf_dir=pdf_dir, wav_dir=wav_dir)

    def load_export_settings(self) -> ExportSettings:
        export_dir = Path(self._value("export/default_dir", DEFAULT_EXPORT_DIR))
        auto_export = bool(self._value("export/auto", True))
        return ExportSettings(auto_export=auto_export, export_dir=export_dir)

    def load_tolerance_settings(self) -> ToleranceSettings:
        warn = int(self._value("analysis/tolerance_warn", 2))
        fail = int(self._value("analysis/tolerance_fail", 5))
        return ToleranceSettings(warn_tolerance=warn, fail_tolerance=fail)

    def load_id_extraction_settings(self) -> IdExtractionSettings:
        min_digits = int(self._value("analysis/min_id_digits", 3))
        max_digits = int(self._value("analysis/max_id_digits", 6))
        if min_digits > max_digits:
            min_digits, max_digits = max_digits, min_digits
        ignore = self._value("analysis/ignore_numbers", [])
        ignore_numbers: List[str] = []
        seen: set[str] = set()
        for item in ignore:
            candidate = str(item).strip()
            if not candidate:
                continue
            if candidate not in seen:
                seen.add(candidate)
                ignore_numbers.append(candidate)
            if candidate.isdigit():
                canonical = str(int(candidate))
                if canonical not in seen:
                    seen.add(canonical)
                    ignore_numbers.append(canonical)
        return IdExtractionSettings(
            min_digits=min_digits,
            max_digits=max_digits,
            ignore_numbers=ignore_numbers,
        )

    def load_analysis_settings(self) -> AnalysisSettings:
        tolerance = self.load_tolerance_settings()
        ids = self.load_id_extraction_settings()
        return AnalysisSettings(
            tolerance_warn=tolerance.warn_tolerance,
            tolerance_fail=tolerance.fail_tolerance,
            min_id_digits=ids.min_digits,
            max_id_digits=ids.max_digits,
            ignore_numbers=ids.ignore_numbers,
        )

    def load_ui_settings(self) -> UiSettings:
        dpi_scale = self._value("ui/dpi_scale", "AUTO")
        theme = self._value("ui/theme", "AUTO")
        geometry = self._value("ui/window_geometry", "1720x1440")
        base_font_family = self._value("ui/base_font_family", "Poppins, Segoe UI, Arial, sans-serif")
        base_font_size = int(self._value("ui/base_font_size", 13))
        heading_font_size = int(self._value("ui/heading_font_size", 12))
        treeview_row_height = int(self._value("ui/treeview_row_height", 28))
        action_bg = self._value("ui/table_action_bg_color", "#E0E7FF")
        total_row_bg = self._value("ui/total_row_bg_color", "#F3F4F6")
        claim_visible = bool(self._value("gz_brand/claim_visible", True))
        claim_text = self._value("gz_brand/claim_text", "Emotions. Materialized.")
        logo_path = Path(self._value("gz_brand/logo_path", "assets/gz_logo_white.png"))
        status_colors = {
            "ok": str(self._value("gz_status/ok_color", "#10B981")),
            "warn": str(self._value("gz_status/warn_color", "#F59E0B")),
            "fail": str(self._value("gz_status/fail_color", "#EF4444")),
        }
        return UiSettings(
            dpi_scale=dpi_scale,
            theme=str(theme),
            window_geometry=str(geometry),
            base_font_family=str(base_font_family),
            base_font_size=base_font_size,
            heading_font_size=heading_font_size,
            treeview_row_height=treeview_row_height,
            status_colors=status_colors,
            action_row_bg_color=str(action_bg),
            total_row_bg_color=str(total_row_bg),
            claim_visible=claim_visible,
            claim_text=str(claim_text),
            logo_path=logo_path,
        )

    def load_theme_settings(self) -> ThemeSettings:
        ui_settings = self.load_ui_settings()
        stylesheet_path = Path("gz_media.qss")
        return ThemeSettings(
            font_family=ui_settings.base_font_family,
            font_size=ui_settings.base_font_size,
            stylesheet_path=stylesheet_path,
            status_colors=ui_settings.status_colors,
            logo_path=ui_settings.logo_path,
            claim_visible=ui_settings.claim_visible,
            claim_text=ui_settings.claim_text,
            action_bg_color=ui_settings.action_row_bg_color,
            total_row_bg_color=ui_settings.total_row_bg_color,
        )


class AppConfig:
    """Application configuration backed by QSettings."""

    def __init__(self) -> None:
        self.settings = QSettings(DEFAULT_SETTINGS_ORG, DEFAULT_SETTINGS_APP)
        self._defaults: Dict[str, Any] = dict(DEFAULTS)
        self.file: Path = SETTINGS_FILENAME

    def _key(self, attr: str) -> str:
        if attr in ATTRIBUTE_KEY_MAP:
            return ATTRIBUTE_KEY_MAP[attr]
        raise AttributeError(attr)

    def get(self, key: str, default: Any = None) -> Any:
        if default is None and key in self._defaults:
            default = self._defaults[key]
        value = self.settings.value(key, default)
        if isinstance(default, bool):
            if isinstance(value, bool):
                return value
            return str(value).lower() in {"true", "1", "yes", "on"}
        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default
        if isinstance(default, float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
        if isinstance(default, list):
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, TypeError, ValueError):
                    candidates = [item.strip() for item in value.split(",") if item.strip()]
                    if candidates:
                        return candidates
            return list(default)
        return value

    def set(self, key: str, value: Any) -> None:
        self.settings.setValue(key, value)

    def get_value(self, key: str) -> ConfigValue:
        return ConfigValue(self.get(key))

    def get_all_keys(self) -> List[str]:
        keys = set(self._defaults.keys())
        keys.update(self.settings.allKeys())
        return sorted(keys)

    def reset_to_defaults(self) -> None:
        for key, value in self._defaults.items():
            self.set(key, value)
        self.settings.sync()

    def load(self, file_path: Union[str, Path]) -> None:
        path = Path(file_path)
        if not path.exists():
            self.file = path
            return
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        for key, value in _flatten_dict(data).items():
            self.set(key, value)
        self.settings.sync()
        self.file = path

    def save(self) -> None:
        self.settings.sync()

    def clear(self) -> None:
        self.settings.clear()

    def __getattr__(self, item: str) -> ConfigValue:
        if item == "settings":
            return ConfigValue(self.settings)
        if item in ATTRIBUTE_KEY_MAP:
            return self.get_value(ATTRIBUTE_KEY_MAP[item])
        raise AttributeError(item)


def _flatten_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten_dict(value, full_key))
        else:
            flat[full_key] = value
    return flat


def _nest_dict(flat: Dict[str, Any]) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    for key, value in flat.items():
        parts = key.split("/")
        cursor = root
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
    return root


cfg = AppConfig()


def load_config(file_path: Union[str, Path]) -> AppConfig:
    cfg.load(file_path)
    return cfg


def save_config(file_path: Union[str, Path]) -> None:
    keys = cfg.get_all_keys()
    prefixes_with_children = {key.split("/", 1)[0] for key in keys if "/" in key}

    data: Dict[str, Any] = {}
    for key in keys:
        if "/" not in key and key in prefixes_with_children:
            continue
        data[key] = cfg.get(key)

    nested = _nest_dict(data)
    serializable = _as_json_serializable(nested)
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, ensure_ascii=False)


try:
    from PyQt6.QtCore import QByteArray
except ImportError:  # pragma: no cover
    QByteArray = None  # type: ignore[assignment]


def _as_json_serializable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _as_json_serializable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_as_json_serializable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if QByteArray is not None and isinstance(value, QByteArray):
        return value.toBase64().data().decode("ascii")
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(value).decode("ascii")
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)
