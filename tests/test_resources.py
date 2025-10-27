from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

RESOURCE_FILE = Path("ui") / "_icons_rc.py"
EXPECTED_ICONS = ("play.svg", "check.svg", "cross.svg")


def _load_icons_module():
    spec = importlib.util.spec_from_file_location("ui._icons_rc", RESOURCE_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ui._icons_rc module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def test_icons_resources_compiled():
    """Verify that PyQt resources are compiled and accessible via the Qt resource system."""
    assert RESOURCE_FILE.exists(), "_icons_rc.py is missing; run tools/build_resources.py"

    module = _load_icons_module()
    resource_bytes = getattr(module, "qt_resource_data", b"")
    assert resource_bytes, "_icons_rc.py does not contain embedded resource data"

    svg_occurrences = resource_bytes.count(b"<svg")
    assert svg_occurrences >= len(EXPECTED_ICONS), "Embedded resources do not contain expected SVG payloads"
