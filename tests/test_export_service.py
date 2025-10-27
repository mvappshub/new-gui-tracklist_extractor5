from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ExportSettings
from services.export_service import export_results_to_json


@pytest.fixture
def export_settings(tmp_path):
    return ExportSettings(auto_export=True, export_dir=tmp_path)


@pytest.fixture
def sample_results(tmp_path):
    pdf_track = TrackInfo(title="Track 1", side="A", position=1, duration_sec=120)
    wav_track = WavInfo(filename="track1.wav", duration_sec=120.0, side="A", position=1)
    result = SideResult(
        seq=1,
        pdf_path=tmp_path / "track.pdf",
        zip_path=tmp_path / "track.zip",
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=120,
        total_wav_sec=120.0,
        total_difference=0,
    )
    return [result]


def test_export_results_creates_file(tmp_path, export_settings, sample_results):
    export_path = export_results_to_json(sample_results, export_settings)
    assert export_path is not None
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["count"] == 1
    assert payload["results"][0]["pdf_path"].endswith("track.pdf")


def test_export_respects_auto_export_disabled(tmp_path, sample_results):
    settings = ExportSettings(auto_export=False, export_dir=tmp_path)
    export_path = export_results_to_json(sample_results, settings)
    assert export_path is None


def test_export_returns_none_for_empty_results(export_settings):
    export_path = export_results_to_json([], export_settings)
    assert export_path is None
