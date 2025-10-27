from __future__ import annotations

from enum import StrEnum


class AnalysisStatus(StrEnum):
    """Enumeration of possible analysis outcomes."""

    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"

    def severity(self) -> int:
        """Return numeric severity ordering (higher means more severe)."""

        if self is AnalysisStatus.OK:
            return 0
        if self is AnalysisStatus.WARN:
            return 1
        return 2

    def icon_name(self) -> str:
        """Return canonical icon identifier for UI rendering."""

        if self is AnalysisStatus.OK:
            return "check"
        if self is AnalysisStatus.WARN:
            return "warning"
        return "cross"

    def color_key(self) -> str:
        """Return status key suitable for theme lookups."""

        return self.value.lower()

    @classmethod
    def from_str(cls, value: str | None) -> AnalysisStatus:
        """Parse string value into an AnalysisStatus, defaulting to OK."""

        if not value:
            return cls.OK
        try:
            return cls(value.upper())
        except ValueError:
            return cls.OK
