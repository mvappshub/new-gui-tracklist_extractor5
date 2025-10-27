from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from core.models.analysis import SideResult

"""Centralized export service - single source of truth for all analysis result exports.
All export operations should use export_results_to_json() from this module."""


class ExportSettingsProtocol(Protocol):
    auto_export: bool
    export_dir: Path


ExportSettingsType = ExportSettingsProtocol


def export_results_to_json(results: list[SideResult], export_settings: ExportSettingsType) -> Path | None:
    """Export analysis results to JSON using the centralized export service.

    Usage example:
        from services.export_service import export_results_to_json
        exported_path = export_results_to_json(results, export_settings)

    This is the canonical export implementation shared by the UI layer and automated tests.
    Returns the exported file path or ``None`` when nothing is written.
    """
    if not export_settings.auto_export or not results:
        return None

    export_dir = export_settings.export_dir
    try:
        export_dir.mkdir(parents=True, exist_ok=True)
    except Exception:  # pragma: no cover
        logging.error("Failed to prepare export directory: %s", export_dir, exc_info=True)
        return None

    base = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload: dict[str, Any] = {
        "exported_at": base,
        "count": len(results),
        "results": [],
    }

    for result in results:
        item = result.model_dump(mode="json")
        item["pdf_path"] = str(result.pdf_path)
        item["zip_path"] = str(result.zip_path)
        payload["results"].append(item)

    for index in range(1000):
        suffix = f"_{index:03d}" if index else ""
        out_path = export_dir / f"analysis_{base}{suffix}.json"
        try:
            with out_path.open("x", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            logging.info("Exported analysis results to %s", out_path)
            return out_path
        except FileExistsError:
            continue
        except Exception:  # pragma: no cover
            logging.error("Failed to export analysis results to %s", out_path, exc_info=True)
            out_path.unlink(missing_ok=True)
            return None

    logging.error("Could not create unique filename for export in %s", export_dir)  # pragma: no cover
    return None
