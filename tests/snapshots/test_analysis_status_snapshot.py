from __future__ import annotations

import json
from pathlib import Path

from core.domain.analysis_status import AnalysisStatus


SNAPSHOT_FILE = Path(__file__).with_name("analysis_status.json")


def _serialize_statuses() -> list[dict[str, object]]:
    return [
        {
            "name": status.name,
            "value": status.value,
            "severity": status.severity(),
            "icon": status.icon_name(),
            "color_key": status.color_key(),
        }
        for status in AnalysisStatus
    ]


def test_analysis_status_snapshot():
    expected = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    actual = _serialize_statuses()
    assert actual == expected, "AnalysisStatus snapshot mismatch. Run pytest --snapshot-update equivalent to refresh intentionally."
