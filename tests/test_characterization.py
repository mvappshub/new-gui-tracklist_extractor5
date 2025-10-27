from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from adapters.filesystem.file_discovery import discover_and_pair_files
from core.domain.analysis_status import AnalysisStatus
from core.domain.comparison import compare_data
from core.models.analysis import TrackInfo, WavInfo
from core.models.settings import IdExtractionSettings, ToleranceSettings

FLOAT_TOLERANCE = 0.01
GOLDEN_DIR = Path(__file__).parent / "data" / "golden"


def _load_golden(name: str) -> Any:
    path = GOLDEN_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _assert_json_matches(actual: Any, expected: Any, path: str = "root") -> None:
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path} expected dict, got {type(actual).__name__}"
        assert set(actual.keys()) == set(expected.keys()), f"{path} key mismatch"
        for key in expected:
            _assert_json_matches(actual[key], expected[key], f"{path}.{key}")
        return

    if isinstance(expected, list):
        assert isinstance(actual, list), f"{path} expected list, got {type(actual).__name__}"
        assert len(actual) == len(expected), f"{path} length mismatch"
        for index, (act_item, exp_item) in enumerate(zip(actual, expected, strict=False)):
            _assert_json_matches(act_item, exp_item, f"{path}[{index}]")
        return

    if isinstance(expected, int | float) and isinstance(actual, int | float):
        if isinstance(expected, float) or isinstance(actual, float):
            delta = abs(float(actual) - float(expected))
            assert delta <= FLOAT_TOLERANCE, f"{path} float diff {delta} exceeds tolerance {FLOAT_TOLERANCE}"
        else:
            assert actual == expected, f"{path} int mismatch"
        return

    assert actual == expected, f"{path} value mismatch"


@pytest.mark.usefixtures("isolated_config")
def test_discover_and_pair_files_matches_golden(
    tmp_path,
    id_extraction_settings,
) -> None:
    pdf_dir = tmp_path / "pdf"
    wav_dir = tmp_path / "zip"
    pdf_dir.mkdir()
    wav_dir.mkdir()

    (pdf_dir / "12345_tracklist.pdf").write_text("pdf", encoding="utf-8")
    (pdf_dir / "67890_tracklist.pdf").write_text("pdf", encoding="utf-8")

    (wav_dir / "12345_masters.zip").write_text("zip", encoding="utf-8")
    (wav_dir / "67890_take1.zip").write_text("zip", encoding="utf-8")
    (wav_dir / "67890_take2.zip").write_text("zip", encoding="utf-8")

    pairs, skipped = discover_and_pair_files(pdf_dir, wav_dir, id_extraction_settings)
    actual = {
        "pairs": {
            str(pair_id): {"pdf": pair.pdf.name, "zip": pair.zip.name}
            for pair_id, pair in pairs.items()
        },
        "skipped_count": skipped,
    }

    expected = _load_golden("golden_pairs.json")
    _assert_json_matches(actual, expected)


@pytest.mark.usefixtures("isolated_config")
def test_compare_data_matches_golden(tmp_path, tolerance_settings, audio_mode_detector) -> None:
    pdf_data = {
        "A": [
            TrackInfo(title="Intro", side="A", position=1, duration_sec=120),
            TrackInfo(title="Song", side="A", position=2, duration_sec=150),
        ],
        "B": [
            TrackInfo(title="Ballad", side="B", position=1, duration_sec=210),
        ],
    }

    wav_data = [
        WavInfo(filename="Side_A_01_intro.wav", duration_sec=119.98),
        WavInfo(filename="Side_A_02_song.wav", duration_sec=150.02),
        WavInfo(filename="Side_B_01_ballad.wav", duration_sec=206.9),
    ]

    pair_info = {"pdf": tmp_path / "dummy.pdf", "zip": tmp_path / "dummy.zip"}

    results = compare_data(pdf_data, wav_data, pair_info, tolerance_settings, audio_mode_detector)
    actual_results = []

    for item in results:
        data = item.model_dump()
        data["pdf_path"] = Path(data["pdf_path"]).name
        data["zip_path"] = Path(data["zip_path"]).name
        actual_results.append(data)

    expected = _load_golden("golden_comparison.json")
    _assert_json_matches(actual_results, expected)


@pytest.mark.parametrize(
    ("warn_tolerance", "fail_tolerance", "expected_status"),
    [
        (1, 2, AnalysisStatus.FAIL),
        (2, 5, AnalysisStatus.WARN),
        (4, 6, AnalysisStatus.OK),
    ],
)
def test_compare_data_respects_injected_tolerances(
    tmp_path: Path,
    warn_tolerance: int,
    fail_tolerance: int,
    expected_status: str,
    audio_mode_detector,
) -> None:
    pdf_data = {
        "A": [
            TrackInfo(title="Intro", side="A", position=1, duration_sec=120),
            TrackInfo(title="Song", side="A", position=2, duration_sec=150),
        ],
        "B": [
            TrackInfo(title="Ballad", side="B", position=1, duration_sec=210),
        ],
    }
    wav_data = [
        WavInfo(filename="Side_A_01_intro.wav", duration_sec=119.98),
        WavInfo(filename="Side_A_02_song.wav", duration_sec=150.02),
        WavInfo(filename="Side_B_01_ballad.wav", duration_sec=206.9),
    ]
    pair_info = {"pdf": tmp_path / "dummy.pdf", "zip": tmp_path / "dummy.zip"}

    tolerance = ToleranceSettings(
        warn_tolerance=warn_tolerance,
        fail_tolerance=fail_tolerance,
    )
    results = compare_data(pdf_data, wav_data, pair_info, tolerance, audio_mode_detector)
    status_by_side = {result.side: result.status for result in results}
    assert status_by_side["B"] == expected_status


@pytest.mark.parametrize(
    ("min_digits", "max_digits", "ignore_numbers", "expected_ids"),
    [
        (1, 3, [], {1, 9}),
        (2, 3, [], {1}),
        (1, 3, ["9"], {1}),
    ],
)
def test_discover_and_pair_files_respects_id_settings(
    tmp_path: Path,
    min_digits: int,
    max_digits: int,
    ignore_numbers: list[str],
    expected_ids: set[int],
):
    pdf_dir = tmp_path / "pdf_param"
    wav_dir = tmp_path / "zip_param"
    pdf_dir.mkdir()
    wav_dir.mkdir()

    (pdf_dir / "track9.pdf").write_text("pdf", encoding="utf-8")
    (pdf_dir / "track_001.pdf").write_text("pdf", encoding="utf-8")
    (wav_dir / "track9.zip").write_text("zip", encoding="utf-8")
    (wav_dir / "track_001.zip").write_text("zip", encoding="utf-8")

    settings = IdExtractionSettings(
        min_digits=min_digits,
        max_digits=max_digits,
        ignore_numbers=ignore_numbers,
    )
    pairs, skipped = discover_and_pair_files(pdf_dir, wav_dir, settings)

    assert set(pairs.keys()) == expected_ids
    assert skipped == 0
