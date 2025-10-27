import pytest

from core.domain.parsing import StrictFilenameParser, TracklistParser


@pytest.fixture
def strict_parser() -> StrictFilenameParser:
    return StrictFilenameParser()


def test_strict_parser_handles_common_patterns(strict_parser: StrictFilenameParser):
    parsed = strict_parser.parse("A1_track.wav")
    assert parsed.side == "A"
    assert parsed.position == 1

    parsed = strict_parser.parse("Side_B_02.wav")
    assert parsed.side == "B"
    assert parsed.position == 2

    parsed = strict_parser.parse("03_Title.flac")
    assert parsed.side is None
    assert parsed.position is None


def test_strict_parser_handles_windows_paths(strict_parser: StrictFilenameParser):
    windows_path = r"C:\Audio\Side_C03_song.wav"
    parsed = strict_parser.parse(windows_path)
    assert parsed.side == "C"
    assert parsed.position == 3


def test_tracklist_parser_filters_and_sorts_tracks():
    raw = [
        {"title": "First", "side": "a", "position": 1, "duration_formatted": "04:30"},
        {"title": "First", "side": "A", "position": 1, "duration_formatted": "04:30"},  # duplicate
        {"title": "Long", "side": "B", "position": 1, "duration_formatted": "30:01"},
        {"title": "NoDuration", "side": "B", "position": 2, "duration_formatted": ""},
        {"title": "InvalidTime", "side": "B", "position": 3, "duration_formatted": "5m10s"},
        {"title": "BadPosition", "side": "B", "position": "x", "duration_formatted": "02:10"},
        {"title": "Second", "side": "B", "position": 3, "duration_formatted": "03:05"},
        {"title": "Third", "side": "A", "position": 5, "duration_formatted": "05:00"},
    ]

    parser = TracklistParser()
    tracks = parser.parse(raw)

    assert [(t.title, t.side, t.position, t.duration_sec) for t in tracks] == [
        ("First", "A", 1, 270),
        ("Third", "A", 5, 300),
        ("Second", "B", 3, 185),
    ]
