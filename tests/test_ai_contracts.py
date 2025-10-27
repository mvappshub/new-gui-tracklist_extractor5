from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest
from PIL import Image

from adapters.ai.vlm import VlmClient
from adapters.audio import ai_helpers
from core.models.analysis import WavInfo


def _make_dummy_image() -> Image.Image:
    return Image.new("RGB", (1, 1), color="white")


def test_to_data_url_encoding():
    client = VlmClient()
    image = _make_dummy_image()

    data_url = client._to_data_url(image)

    assert data_url.startswith("data:image/png;base64,")
    b64_payload = data_url.split(",", 1)[1]
    decoded = base64.b64decode(b64_payload)
    assert decoded  # decodable payload


@dataclass
class _FakeResponse:
    content: str | None

    @property
    def choices(self):
        class _Choice:
            def __init__(self, content: str | None):
                self.message = type("Msg", (), {"content": content})()

        return [_Choice(self.content)]


class _RecordingCompletions:
    def __init__(self, content: str):
        self.content = content
        self.last_kwargs: Dict[str, Any] | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeResponse(self.content)


class _RecordingClient:
    def __init__(self, content: str):
        self.completions = _RecordingCompletions(content)


class _WrapperClient:
    def __init__(self, content: str):
        self.chat = _RecordingClient(content)


def test_get_json_response_message_format(monkeypatch):
    client = VlmClient()
    recording = _WrapperClient('{"tracks": []}')
    monkeypatch.setattr(client, "_client", recording)

    prompt = "Describe this waveform"
    images = [_make_dummy_image()]

    result = client.get_json_response(prompt, images)

    assert result == {"tracks": []}
    kwargs = recording.chat.completions.last_kwargs
    assert kwargs is not None
    assert kwargs["model"] == "google/gemini-2.5-flash"
    assert kwargs["response_format"] == {"type": "json_object"}
    assert kwargs["temperature"] == 0.0

    messages: List[Dict[str, Any]] = kwargs["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    content = messages[0]["content"]
    assert content[0]["type"] == "text"
    assert content[0]["text"] == prompt
    image_part = content[1]
    assert image_part["type"] == "image_url"
    image_url = image_part["image_url"]["url"]
    assert image_url.startswith("data:image/png;base64,")


def test_get_json_response_empty_content(monkeypatch):
    client = VlmClient()
    wrapper = _WrapperClient(None)  # type: ignore[arg-type]
    monkeypatch.setattr(client, "_client", wrapper)

    with pytest.raises(ValueError, match="AI returned an empty response."):
        client.get_json_response("prompt", [_make_dummy_image()])


def test_get_json_response_backtick_wrapped(monkeypatch):
    client = VlmClient()
    payload = "```json\n{\"tracks\": []}\n```"
    wrapper = _WrapperClient(payload)
    monkeypatch.setattr(client, "_client", wrapper)

    result = client.get_json_response("prompt", [_make_dummy_image()])

    assert result == {"tracks": []}


def test_get_json_response_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    client = VlmClient()
    assert client.get_json_response("prompt", [_make_dummy_image()]) == {}


class _RecordingAIClient:
    def __init__(self, payload: str | None = None):
        self.payload = payload or "{}"
        self.last_kwargs: Dict[str, Any] | None = None

    class _Chat:
        def __init__(self, outer: "_RecordingAIClient"):
            self._outer = outer

        class _Completions:
            def __init__(self, outer: "_RecordingAIClient"):
                self._outer = outer

            def create(self, **kwargs):
                self._outer.last_kwargs = kwargs
                return _FakeResponse(self._outer.payload)

        @property
        def completions(self):
            return _RecordingAIClient._Chat._Completions(self._outer)

    @property
    def chat(self):
        return _RecordingAIClient._Chat(self)


def test_ai_parse_batch_request_format(monkeypatch):
    client = _RecordingAIClient('{"file.wav": {"side": "A", "position": 1}}')

    def _fake_loader():
        return client, "test-model"

    monkeypatch.setattr(ai_helpers, "_load_ai_client", _fake_loader)

    result = ai_helpers.ai_parse_batch(["file.wav"])

    assert result == {"file.wav": ("A", 1)}

    kwargs = client.last_kwargs
    assert kwargs is not None
    assert kwargs["model"] == "test-model"
    assert kwargs["temperature"] == 0.0
    assert kwargs["response_format"] == {"type": "json_object"}

    messages: List[Dict[str, Any]] = kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert "STRICT JSON" in messages[0]["content"]
    user_content = messages[1]["content"]
    parsed = json.loads(user_content)
    assert parsed == {"filenames": ["file.wav"]}


def test_ai_parse_batch_valid_response(monkeypatch):
    client = _RecordingAIClient('{"file.wav": {"side": "B", "position": 3}}')
    monkeypatch.setattr(ai_helpers, "_load_ai_client", lambda: (client, "model"))

    result = ai_helpers.ai_parse_batch(["file.wav"])
    assert result == {"file.wav": ("B", 3)}


def test_ai_parse_batch_empty_response(monkeypatch):
    client = _RecordingAIClient("{}")
    monkeypatch.setattr(ai_helpers, "_load_ai_client", lambda: (client, "model"))

    assert ai_helpers.ai_parse_batch(["file.wav"]) == {"file.wav": (None, None)}


def test_ai_parse_batch_invalid_json(monkeypatch):
    client = _RecordingAIClient("not-json")
    monkeypatch.setattr(ai_helpers, "_load_ai_client", lambda: (client, "model"))

    assert ai_helpers.ai_parse_batch(["file.wav"]) == {}


def test_ai_parse_batch_empty_filenames(monkeypatch):
    client = _RecordingAIClient("{}")
    monkeypatch.setattr(ai_helpers, "_load_ai_client", lambda: (client, "model"))

    assert ai_helpers.ai_parse_batch([]) == {}


def test_merge_ai_results_side_position_update():
    wav = WavInfo(filename="file.wav", duration_sec=10.0)
    ai_map = {"file.wav": ("A", 5)}

    ai_helpers.merge_ai_results([wav], ai_map)

    assert wav.side == "A"
    assert wav.position == 5
