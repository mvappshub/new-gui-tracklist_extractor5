from __future__ import annotations

import logging
from pathlib import Path

import pytest

from core.domain.parsing import ParsedFileInfo, StrictFilenameParser, TracklistParser
from core.domain.comparison import compare_data
from core.models.analysis import TrackInfo, WavInfo
from core.models.settings import ToleranceSettings


@pytest.fixture
def parser() -> StrictFilenameParser:
    return StrictFilenameParser()


def test_strict_filename_parser_conflicting_patterns(parser: StrictFilenameParser):
    info = parser.parse("Side_A_B1_track.wav")
    assert info.side == "A"
    assert info.position == 1

    info = parser.parse("AA01BB02.wav")
    assert info.side == "AA"
    assert info.position == 1


def test_strict_filename_parser_negative_cases(parser: StrictFilenameParser):
    assert parser.parse("song_without_markers.wav") == ParsedFileInfo(None, None)
    assert parser.parse("mixdown-final.wav") == ParsedFileInfo(None, None)


def _build_track(title: str, duration: int, side: str, position: int) -> TrackInfo:
    return TrackInfo(title=title, side=side, position=position, duration_sec=duration)


def _build_wav(filename: str, duration: float, side: str, position: int) -> WavInfo:
    return WavInfo(filename=filename, duration_sec=duration, side=side, position=position)


class DummyDetector:
    def detect(self, wavs: list[WavInfo]):
        side_map: dict[str, list[WavInfo]] = {}
        for wav in wavs:
            side = (wav.side or "A").upper()
            clone = WavInfo(filename=wav.filename, duration_sec=wav.duration_sec, side=side, position=wav.position)
            side_map.setdefault(side, []).append(clone)
        return side_map


def test_compare_data_tolerance_edge_cases():
    tolerance = ToleranceSettings(warn_tolerance=2, fail_tolerance=5)
    pdf = {"A": [_build_track("song", 120, "A", 1)]}

    wav_warn = [_build_wav("song.wav", 123, "A", 1)]
    result_warn = compare_data(pdf, wav_warn, {"pdf": Path("x.pdf"), "zip": Path("x.zip")}, tolerance, DummyDetector())
    assert result_warn[0].status.value == "WARN"

    wav_fail = [_build_wav("song.wav", 129, "A", 1)]
    result_fail = compare_data(pdf, wav_fail, {"pdf": Path("x.pdf"), "zip": Path("x.zip")}, tolerance, DummyDetector())
    assert result_fail[0].status.value == "FAIL"

    wav_ok = [_build_wav("song.wav", 121, "A", 1)]
    result_ok = compare_data(pdf, wav_ok, {"pdf": Path("x.pdf"), "zip": Path("x.zip")}, tolerance, DummyDetector())
    assert result_ok[0].status.value == "OK"


def test_compare_data_negative_difference():
    tolerance = ToleranceSettings(warn_tolerance=2, fail_tolerance=5)
    pdf = {"A": [_build_track("song", 123, "A", 1)]}
    wav = [_build_wav("song.wav", 118, "A", 1)]

    result = compare_data(pdf, wav, {"pdf": Path("x.pdf"), "zip": Path("x.zip")}, tolerance, DummyDetector())
    assert abs(result[0].total_difference) == 5
    assert result[0].status.value == "FAIL"


def test_tracklist_parser_malformed_duration(caplog):
    caplog.set_level(logging.WARNING)
    parser = TracklistParser()
    raw = [
        {"title": "Invalid Format", "side": "A", "position": 1, "duration_formatted": "invalid"},
        {"title": "Too Long", "side": "A", "position": 2, "duration_formatted": "30:10"},
        {"title": "Missing", "side": "A", "position": 3, "duration_formatted": ""},
        {"title": "Bad Position", "side": "A", "position": "x", "duration_formatted": "03:10"},
    ]

    result = parser.parse(raw)
    assert result == []
    assert any("Failed to process" in rec.message or "Ignoring track" in rec.message for rec in caplog.records)

