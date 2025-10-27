from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("importlinter")

CONFIG_PATH = Path(__file__).resolve().parent.parent / "linter.ini"


@pytest.mark.slow
def test_import_linter_contracts():
    result = subprocess.run(
        [sys.executable, "-m", "importlinter.cli", "lint", "--config", str(CONFIG_PATH)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=CONFIG_PATH.parent,
    )
    if result.returncode != 0:
        pytest.fail(f"Import-linter contracts failed:\n{result.stdout}")
