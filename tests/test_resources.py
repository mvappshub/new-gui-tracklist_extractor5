from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest
from PyQt6.QtCore import QResource

RESOURCE_MODULE = "ui._icons_rc"
RESOURCE_FILE = Path("ui") / "_icons_rc.py"
EXPECTED_ICONS = [":/icons/play.svg", ":/icons/check.svg", ":/icons/cross.svg"]


def test_icons_resources_compiled():
    """Verify that PyQt resources are compiled and accessible via the Qt resource system."""
    assert RESOURCE_FILE.exists(), "_icons_rc.py is missing; run tools/build_resources.py"

    module = import_module(RESOURCE_MODULE)
    assert getattr(module, "qt_resource_data", b""), "_icons_rc.py does not contain embedded resource data"

    module.qCleanupResources()
    module.qInitResources()

    missing = [path for path in EXPECTED_ICONS if not QResource(path).isValid()]
    if missing:
        pytest.fail(f"Missing Qt resources: {', '.join(missing)}")

    # Ensure resources remain registered for later tests.
    module.qCleanupResources()
    module.qInitResources()
