from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pytest
from PIL import Image

import pdf_extractor
from core.models.analysis import TrackInfo


class _FakeRenderer:
    def __init__(self, images: List[Image.Image]):
        self._images = images

    def render(self, _: Path):
        return list(self._images)


class _FakeVlm:
    def __init__(self, responses: List[Dict[str, object]]):
        self._responses = responses
        self.calls: List[Dict[str, object]] = []

    def get_json_response(self, prompt: str, images: List[Image.Image]):
        self.calls.append({"prompt": prompt, "images": images})
        return self._responses.pop(0)


@pytest.fixture
def fake_image() -> Image.Image:
    return Image.new("RGB", (2, 2), color="white")


def test_extract_pdf_tracklist_valid_response(monkeypatch, tmp_path, fake_image):
    fake_renderer = _FakeRenderer([fake_image])
    fake_vlm = _FakeVlm([{"tracks": [{"title": "Track 1", "side": "A", "position": 1, "duration_formatted": "03:45"}]}])

    monkeypatch.setattr(pdf_extractor, "PdfImageRenderer", lambda: fake_renderer)
    monkeypatch.setattr(pdf_extractor, "VlmClient", lambda: fake_vlm)

    result = pdf_extractor.extract_pdf_tracklist(tmp_path / "dummy.pdf")

    assert "A" in result
    assert len(result["A"]) == 1
    track = result["A"][0]
    assert track.title == "Track 1"
    assert track.position == 1


def test_extract_pdf_tracklist_empty_response(monkeypatch, tmp_path, fake_image, caplog):
    fake_renderer = _FakeRenderer([fake_image])
    fake_vlm = _FakeVlm([{}])

    monkeypatch.setattr(pdf_extractor, "PdfImageRenderer", lambda: fake_renderer)
    monkeypatch.setattr(pdf_extractor, "VlmClient", lambda: fake_vlm)

    caplog.set_level(logging.WARNING)
    result = pdf_extractor.extract_pdf_tracklist(tmp_path / "dummy.pdf")

    assert result == {}
    assert any("returned no tracks" in message for message in caplog.messages)


def test_extract_pdf_tracklist_no_pages(monkeypatch, tmp_path, caplog):
    fake_renderer = _FakeRenderer([])
    fake_vlm = _FakeVlm([])

    monkeypatch.setattr(pdf_extractor, "PdfImageRenderer", lambda: fake_renderer)
    monkeypatch.setattr(pdf_extractor, "VlmClient", lambda: fake_vlm)

    caplog.set_level(logging.WARNING)
    result = pdf_extractor.extract_pdf_tracklist(tmp_path / "dummy.pdf")

    assert result == {}
    assert any("contains no pages" in message for message in caplog.messages)


def test_extract_pdf_tracklist_ai_exception(monkeypatch, tmp_path, fake_image, caplog):
    fake_renderer = _FakeRenderer([fake_image])

    class _FailingVlm:
        def __init__(self):
            self.calls = 0

        def get_json_response(self, *_args, **_kwargs):
            self.calls += 1
            raise RuntimeError("boom")

    fake_vlm = _FailingVlm()

    monkeypatch.setattr(pdf_extractor, "PdfImageRenderer", lambda: fake_renderer)
    monkeypatch.setattr(pdf_extractor, "VlmClient", lambda: fake_vlm)

    caplog.set_level(logging.ERROR)
    result = pdf_extractor.extract_pdf_tracklist(tmp_path / "dummy.pdf")

    assert result == {}
    assert fake_vlm.calls == 1
    assert any("AI call failed" in message for message in caplog.messages)


def test_extract_pdf_tracklist_multiple_pages(monkeypatch, tmp_path, fake_image):
    fake_renderer = _FakeRenderer([fake_image, fake_image])
    fake_vlm = _FakeVlm(
        [
            {"tracks": [{"title": "Track 1", "side": "A", "position": 1, "duration_formatted": "03:45"}]},
            {"tracks": [{"title": "Track 2", "side": "B", "position": 1, "duration_formatted": "04:10"}]},
        ]
    )

    monkeypatch.setattr(pdf_extractor, "PdfImageRenderer", lambda: fake_renderer)
    monkeypatch.setattr(pdf_extractor, "VlmClient", lambda: fake_vlm)

    result = pdf_extractor.extract_pdf_tracklist(tmp_path / "dummy.pdf")

    assert "A" in result and "B" in result
    assert {track.title for track in result["A"] + result["B"]} == {"Track 1", "Track 2"}
