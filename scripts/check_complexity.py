#!/usr/bin/env python3
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from radon.complexity import cc_visit
from radon.complexity import cc_rank

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGETS = ["adapters", "core", "services", "ui"]
FAIL_THRESHOLD = 15
WARN_THRESHOLD = 10
BASELINE: dict[tuple[str, str], float] = {
    ("adapters/audio/ai_helpers.py", "detect_audio_mode_with_ai"): 15.0,
    ("core/domain/parsing.py", "StrictFilenameParser"): 21.0,
    ("core/domain/parsing.py", "StrictFilenameParser.parse"): 20.0,
    ("ui/models/results_table_model.py", "ResultsTableModel.data"): 38.0,
    ("ui/models/tracks_table_model.py", "TracksTableModel.data"): 36.0,
    ("ui/models/tracks_table_model.py", "TracksTableModel.get_track_row_data"): 24.0,
}


@dataclass
class ComplexityViolation:
    file: Path
    line: int
    name: str
    score: float

    @property
    def message(self) -> str:
        grade = cc_rank(self.score)
        return f"{self.file}:{self.line} - {self.name} CC={self.score:.1f} ({grade})"


def analyze_file(path: Path) -> list[ComplexityViolation]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        source = path.read_text(encoding="latin-1")

    issues: list[ComplexityViolation] = []
    for block in cc_visit(source, no_assert=True):
        score = block.complexity
        if score > WARN_THRESHOLD:
            issues.append(
                ComplexityViolation(
                    file=path.relative_to(PROJECT_ROOT),
                    line=block.lineno,
                    name=block.fullname,
                    score=score,
                )
            )
    return issues


def main() -> int:
    warnings: list[ComplexityViolation] = []
    failures: list[ComplexityViolation] = []

    for target in TARGETS:
        base = PROJECT_ROOT / target
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            issues = analyze_file(path)
            for issue in issues:
                key = (str(issue.file).replace("\\", "/"), issue.name)
                if key in BASELINE:
                    if issue.score <= BASELINE[key]:
                        continue
                    failures.append(issue)
                    continue
                if issue.score >= FAIL_THRESHOLD:
                    failures.append(issue)
                else:
                    warnings.append(issue)

    for warning in warnings:
        print(f"[WARN] {warning.message}")

    if failures:
        print("Complexity violations detected (>= 15):", file=sys.stderr)
        for failure in failures:
            print(f"[FAIL] {failure.message}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
