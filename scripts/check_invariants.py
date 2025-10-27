#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "venv", "env", "__pycache__", "node_modules", ".mypy_cache", ".ruff_cache", ".pytest_cache"}


class InvariantViolation(Exception):
    """Raised when a forbidden pattern is discovered."""


def iter_matching_lines(path: Path, pattern: re.Pattern[str]) -> list[str]:
    matches: list[str] = []
    try:
        contents = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        contents = path.read_text(encoding="latin-1")
    for index, line in enumerate(contents.splitlines(), start=1):
        if pattern.search(line):
            rel = path.relative_to(PROJECT_ROOT)
            matches.append(f"{rel}:{index}: {line.strip()}")
    return matches


def check_forbidden_patterns() -> None:
    patterns = [
        ("QApplication(", re.compile(r"QApplication\("), ["tests"], ["**/conftest.py"]),
        ("qapp.exec(", re.compile(r"qapp\.exec\("), ["tests"], []),
        ("print() in tests", re.compile(r"\bprint\("), ["tests"], []),
        ("private import", re.compile(r"from\s+.+\s+import\s+_[A-Za-z]\w*"), [""], []),
        ("SYMBOL_ usage outside constants", re.compile(r"SYMBOL_"), ["ui"], ["**/constants.py", "**/__init__.py"]),
    ]

    violations: list[str] = []

    for description, pattern, roots, exclusions in patterns:
        matches: list[str] = []
        for root in roots:
            base = PROJECT_ROOT / root if root else PROJECT_ROOT
            if not base.exists():
                continue
            for path in base.rglob("*.py"):
                if any(path.match(excl) for excl in exclusions):
                    continue
                if any(part in SKIP_DIRS for part in path.parts):
                    continue
                matches.extend(iter_matching_lines(path, pattern))
        if matches:
            header = f"{description}:"
            violations.append("\n".join([header] + matches))

    if violations:
        joined = "\n\n".join(violations)
        raise InvariantViolation(f"Invariant violations detected:\n{joined}")


def main() -> int:
    try:
        check_forbidden_patterns()
    except InvariantViolation as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Invariant checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
