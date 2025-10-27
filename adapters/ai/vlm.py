from __future__ import annotations
import base64
import io
import json
import os
from typing import Any, List, Dict, cast

try:
    from openai import OpenAI
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Missing AI or Imaging libraries: {e}. Please run 'pip install openai Pillow'")

class VlmClient:
    """Adapter for communicating with a Vision Language Model (VLM) API."""

    def __init__(self, model: str = "google/gemini-2.5-flash"):
        api_key = os.getenv("OPENROUTER_API_KEY")
        # Graceful no-op mode when API key is missing
        if not api_key:
            self._client = None
        else:
            self._client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        self._model = model

    def _to_data_url(self, pil_image: Image.Image) -> str:
        """Converts a PIL image to a base64 data URL."""
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        return f"data:image/png;base64,{b64}"

    def get_json_response(self, prompt: str, images: List[Image.Image]) -> dict[str, Any]:
        """
        Calls the VLM with a prompt and images, expecting a JSON response.

        Args:
            prompt: The text prompt for the VLM.
            images: A list of PIL Image objects to send.

        Returns:
            The parsed JSON response from the VLM as a dictionary.
        """
        # If client is not configured, operate in no-op mode (return empty)
        if self._client is None:
            return {}

        image_contents: List[Dict[str, Any]] = [
            {"type": "image_url", "image_url": {"url": self._to_data_url(img)}} for img in images
        ]
        messages: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}] + image_contents,
            }
        ]

        response = self._client.chat.completions.create(  # type: ignore[call-overload]  # TODO: ai-typing-hardening
            model=self._model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("AI returned an empty response.")
            
        try:
            return cast(Dict[str, Any], json.loads(content))
        except json.JSONDecodeError:
            cleaned_content = content.strip().strip("`").strip("json\n")
            return cast(Dict[str, Any], json.loads(cleaned_content))
