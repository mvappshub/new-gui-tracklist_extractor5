import pytest

from core.domain.analysis_status import AnalysisStatus


def test_severity_ordering():
    assert AnalysisStatus.OK.severity() == 0
    assert AnalysisStatus.WARN.severity() == 1
    assert AnalysisStatus.FAIL.severity() == 2


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (AnalysisStatus.OK, "check"),
        (AnalysisStatus.WARN, "warning"),
        (AnalysisStatus.FAIL, "cross"),
    ],
)
def test_icon_lookup(status: AnalysisStatus, expected: str):
    assert status.icon_name() == expected


def test_color_key_matches_value_lowercase():
    assert AnalysisStatus.OK.color_key() == "ok"
    assert AnalysisStatus.WARN.color_key() == "warn"
    assert AnalysisStatus.FAIL.color_key() == "fail"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("ok", AnalysisStatus.OK),
        ("Warn", AnalysisStatus.WARN),
        ("FAIL", AnalysisStatus.FAIL),
        ("unexpected", AnalysisStatus.OK),
        (None, AnalysisStatus.OK),
        ("", AnalysisStatus.OK),
    ],
)
def test_from_str_parses_case_insensitively(raw, expected):
    assert AnalysisStatus.from_str(raw) is expected
