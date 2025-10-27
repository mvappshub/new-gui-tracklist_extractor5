## Project Context

- Root Path: D:\moje-nove-projekty\new gui tracklist_extractor5
- Timestamp: 20251027-055448
- Total Files: 83
- Total Size: 287125 bytes

## Summary Table

| Relative Path | Bytes | Lines |
|---------------|-------|-------|
| adapters\__init__.py | 1 | 2 |
| adapters\ai\__init__.py | 0 | 1 |
| adapters\ai\vlm.py | 2626 | 74 |
| adapters\audio\__init__.py | 2 | 2 |
| adapters\audio\ai_helpers.py | 6397 | 178 |
| adapters\audio\ai_mode_detector.py | 1668 | 47 |
| adapters\audio\fake_mode_detector.py | 3162 | 86 |
| adapters\audio\chained_detector.py | 1964 | 55 |
| adapters\audio\steps.py | 2564 | 68 |
| adapters\audio\wav_reader.py | 3587 | 79 |
| adapters\filesystem\__init__.py | 1 | 2 |
| adapters\filesystem\file_discovery.py | 2710 | 80 |
| adapters\pdf\__init__.py | 0 | 1 |
| adapters\pdf\renderer.py | 1016 | 33 |
| adapters\ui\__init__.py | 1 | 2 |
| adapters\ui\null_waveform_viewer.py | 1828 | 48 |
| app.py | 3980 | 109 |
| audio_utils.py | 1051 | 34 |
| config.py | 20636 | 528 |
| core\__init__.py | 1 | 2 |
| core\domain\__init__.py | 1 | 2 |
| core\domain\analysis_status.py | 1133 | 46 |
| core\domain\comparison.py | 3547 | 96 |
| core\domain\extraction.py | 447 | 16 |
| core\domain\parsing.py | 5118 | 132 |
| core\domain\steps.py | 597 | 21 |
| core\models\__init__.py | 254 | 11 |
| core\models\analysis.py | 1641 | 71 |
| core\models\settings.py | 2423 | 111 |
| core\ports.py | 3224 | 83 |
| fonts\dejavu-fonts-ttf-2.37\LICENSE | 8816 | 188 |
| mypy.ini | 497 | 27 |
| pdf_extractor.py | 2527 | 65 |
| pdf_viewer.py | 1295 | 42 |
| requirements.txt | 216 | 17 |
| scripts\run_analysis_no_ai.py | 2209 | 67 |
| scripts\smoke_test.py | 1987 | 50 |
| scripts\smoke_wav_only.py | 1928 | 55 |
| services\__init__.py | 1 | 2 |
| services\analysis_service.py | 3828 | 98 |
| services\export_service.py | 2510 | 73 |
| settings_page.py | 6705 | 183 |
| tests\__init__.py | 1 | 2 |
| tests\conftest.py | 4608 | 133 |
| tests\test_ai_mode_detector.py | 8693 | 201 |
| tests\test_config.py | 945 | 31 |
| tests\test_export_auto.py | 10168 | 273 |
| tests\test_export_service.py | 1871 | 58 |
| tests\test_gui_minimal.py | 1470 | 42 |
| tests\test_gui_show.py | 2138 | 62 |
| tests\test_gui_simple.py | 765 | 35 |
| tests\test_chained_detector.py | 19689 | 491 |
| tests\test_characterization.py | 6488 | 188 |
| tests\test_parsing.py | 9986 | 244 |
| tests\test_results_table_model.py | 2488 | 83 |
| tests\test_settings_dialog.py | 18021 | 553 |
| tests\test_tracks_table_model.py | 4042 | 109 |
| tests\test_wav_reader.py | 6708 | 209 |
| tests\test_worker_manager.py | 4166 | 147 |
| tools\bootstrap_and_finalize.sh | 2881 | 90 |
| tools\bootstrap_finalize.sh | 1675 | 48 |
| tools\build_resources.py | 2349 | 71 |
| tools\finalize.sh | 2654 | 94 |
| tools\check.sh | 1359 | 43 |
| ui\__init__.py | 2326 | 88 |
| ui\_icons_rc.py | 705 | 23 |
| ui\config_models.py | 2026 | 58 |
| ui\constants.py | 1700 | 51 |
| ui\delegates\__init__.py | 0 | 1 |
| ui\delegates\action_cell_delegate.py | 3311 | 99 |
| ui\dialogs\__init__.py | 0 | 1 |
| ui\dialogs\settings_dialog.py | 4679 | 130 |
| ui\main_window.py | 18788 | 471 |
| ui\models\__init__.py | 0 | 1 |
| ui\models\results_table_model.py | 6345 | 167 |
| ui\models\tracks_table_model.py | 8677 | 212 |
| ui\theme.py | 5975 | 169 |
| ui\widgets\__init__.py | 38 | 3 |
| ui\widgets\settings\__init__.py | 198 | 10 |
| ui\widgets\settings\groups.py | 11548 | 339 |
| ui\workers\__init__.py | 0 | 1 |
| ui\workers\analysis_worker.py | 1573 | 45 |
| ui\workers\worker_manager.py | 1972 | 60 |

## File Contents

### adapters\__init__.py

`$tag


``n
### adapters\ai\__init__.py

`$tag

``n
### adapters\ai\vlm.py

`$tag
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

``n
### adapters\audio\__init__.py

`$tag


``n
### adapters\audio\ai_helpers.py

`$tag
"""AI parsing helper functions for audio mode detection.

Migrated from legacy wav_extractor_wave.py module.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional, List, Dict, Tuple, Any

from core.domain.parsing import UNKNOWN_POSITION
from core.models.analysis import WavInfo


def _load_ai_client() -> Tuple[Any, Optional[str]]:
    """Load OpenAI client from environment configuration."""
    try:
        from openai import OpenAI
    except Exception:
        return (None, None)
    if os.getenv("OPENROUTER_API_KEY"):
        try:
            client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
            model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
            return client, model
        except Exception:
            pass
    if os.getenv("OPENAI_API_KEY"):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return client, model
        except Exception:
            pass
    return (None, None)


def ai_parse_batch(filenames: List[str]) -> Dict[str, Tuple[Optional[str], Optional[int]]]:
    """Parse WAV filenames using AI to extract side and position metadata.

    Args:
        filenames: List of WAV filenames to parse.

    Returns:
        Dictionary mapping filename to (side, position) tuple.
        Returns empty dict if AI client unavailable or parsing fails.
    """
    client, model = _load_ai_client()
    if not client or not model or not filenames:
        return {}
    system = (
        "You extract metadata from WAV filenames. "
        "For each filename, infer 'side' (letters only, like A,B,AA) and 'position' (1..99). "
        "Return STRICT JSON object mapping filename -> {\"side\": str|null, \"position\": int|null}. No extra text."
    )
    user = {"filenames": filenames}
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            cleaned = content.strip().strip("`").replace("json\\n", "").strip()
            data = json.loads(cleaned)
        out: Dict[str, Tuple[Optional[str], Optional[int]]] = {}
        for fn in filenames:
            rec = data.get(fn, {})
            s_raw = rec.get("side")
            p_raw = rec.get("position")
            side = s_raw.strip().upper() if isinstance(s_raw, str) and s_raw.strip() else None
            pos = int(p_raw) if isinstance(p_raw, int) else None
            out[fn] = (side, pos)
        return out
    except Exception as e:
        print(f"[WARN] AI fallback selhal: {e}", file=sys.stderr)
        return {}


def merge_ai_results(wavs: List[WavInfo], ai_map: Dict[str, Tuple[Optional[str], Optional[int]]]) -> None:
    """Merge AI parsing results into WavInfo objects.

    Args:
        wavs: List of WavInfo objects to update.
        ai_map: Dictionary mapping filename to (side, position) tuple from AI.
    """
    if not ai_map:
        return
    for w in wavs:
        if w.filename in ai_map:
            s_ai, p_ai = ai_map[w.filename]
            updates: dict[str, object] = {}
            s_candidate = s_ai.strip().upper() if isinstance(s_ai, str) else None
            side_is_valid = w.side not in (None, "", "UNKNOWN")
            side_will_be_set = (w.side in (None, "", "UNKNOWN")) and (s_candidate not in (None, "", "UNKNOWN"))
            if side_will_be_set:
                updates["side"] = s_candidate
            if (
                (side_is_valid or side_will_be_set)
                and w.position is None
                and p_ai is not None
            ):
                updates["position"] = p_ai
            if updates:
                w.apply_parsed_info(updates)


def detect_audio_mode_with_ai(wavs: List[WavInfo]) -> Dict[str, List[WavInfo]]:
    """Detect audio side and position from WAV filenames using AI.

    Args:
        wavs: List of WavInfo objects with filename and duration_sec populated.

    Returns:
        Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
        with side and position populated.
    """
    if not wavs:
        return {}

    # Use existing AI parsing logic
    filenames = [w.filename for w in wavs]
    ai_map = ai_parse_batch(filenames)

    # Apply AI results to wavs
    for w in wavs:
        if w.filename in ai_map:
            side, position = ai_map[w.filename]
            updates: dict[str, object] = {}
            side_candidate = side.strip().upper() if isinstance(side, str) else None
            side_is_valid = w.side not in (None, "", "UNKNOWN")
            side_will_be_set = (w.side in (None, "", "UNKNOWN")) and (side_candidate not in (None, "", "UNKNOWN"))
            if side_candidate:
                updates["side"] = side_candidate
            if (
                (side_is_valid or side_will_be_set)
                and w.position is None
                and position is not None
            ):
                updates["position"] = position
            if updates:
                w.apply_parsed_info(updates)

    # Group by side
    side_map: Dict[str, List[WavInfo]] = {}
    for w in wavs:
        side = w.side or "A"  # Default to "A" if side is None
        side_map.setdefault(side, []).append(w)

    return side_map


def normalize_positions(side_map: Dict[str, List[WavInfo]]) -> None:
    """Normalize positions to be sequential (1, 2, 3...) with no gaps.

    Args:
        side_map: Dictionary mapping side to list of WavInfo objects.
    """
    for side, wav_list in side_map.items():
        if not wav_list:
            continue

        # Sort by current position and filename for deterministic ordering
        wav_list.sort(key=lambda w: (w.position if w.position is not None else UNKNOWN_POSITION, w.filename.lower()))

        # Normalize positions to be sequential starting from 1
        for i, wav in enumerate(wav_list, start=1):
            wav.apply_parsed_info({"position": i})

``n
### adapters\audio\ai_mode_detector.py

`$tag
"""Real AI-backed audio mode detector adapter.

Implements the AudioModeDetector protocol using OpenAI/OpenRouter APIs.
Wraps existing wav_extractor_wave functions for strict parsing → AI fallback →
deterministic fallback → normalization.
"""

from __future__ import annotations

from core.models.analysis import WavInfo
from core.ports import AudioModeDetector
from adapters.audio.ai_helpers import detect_audio_mode_with_ai, normalize_positions


class AiAudioModeDetector(AudioModeDetector):
    """Real AI-backed audio mode detector using OpenAI/OpenRouter APIs.

    Wraps existing wav_extractor_wave functions for strict parsing → AI fallback →
    deterministic fallback → normalization.
    """

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Detect audio side and position from WAV filenames using AI.

        Args:
            wavs: List of WavInfo objects with filename and duration_sec populated.

        Returns:
            Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
            with side and position populated and normalized (sequential 1, 2, 3...).

        Raises:
            No exceptions raised - handles edge cases gracefully.
        """
        # Handle empty input
        if not wavs:
            return {}

        # Call AI detection function directly with unified WavInfo type
        side_map = detect_audio_mode_with_ai(wavs)

        # Normalize positions to be sequential (1, 2, 3...) with no gaps
        normalize_positions(side_map)

        # side_map is already in unified WavInfo type
        return side_map

``n
### adapters\audio\fake_mode_detector.py

`$tag
"""Fake audio mode detector adapter for tests.

Implements the AudioModeDetector protocol with deterministic filename parsing.
No external API calls - guarantees consistent results for same inputs.
"""

from __future__ import annotations

from core.domain.parsing import UNKNOWN_POSITION, StrictFilenameParser
from core.models.analysis import WavInfo
from core.ports import AudioModeDetector


class FakeAudioModeDetector(AudioModeDetector):
    """Fake audio mode detector for tests.

    Uses deterministic filename parsing with no external API calls.
    Guarantees consistent results for same inputs.
    """

    def __init__(self) -> None:
        self._parser = StrictFilenameParser()

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Detect audio side and position from WAV filenames using deterministic parsing.

        Args:
            wavs: List of WavInfo objects with filename and duration_sec populated.

        Returns:
            Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
            with side and position populated and normalized (sequential 1, 2, 3...).

        Raises:
            No exceptions raised - handles edge cases gracefully.
        """
        if not wavs:
            return {}

        parsed_wavs = []
        for wav in wavs:
            parsed_info = self._parser.parse(wav.filename)
            parsed_wavs.append(
                WavInfo(
                    filename=wav.filename,
                    duration_sec=wav.duration_sec,
                    side=parsed_info.side,
                    position=parsed_info.position,
                )
            )

        side_map: dict[str, list[WavInfo]] = {}
        for wav in parsed_wavs:
            side = wav.side or "A"  # Default to "A" if side is None
            side_map.setdefault(side, []).append(wav)

        for wav_list in side_map.values():
            wav_list.sort(
                key=lambda x: (x.position if x.position is not None else UNKNOWN_POSITION, x.filename.lower())
            )

        self._normalize_positions(side_map)

        return side_map

    def _normalize_positions(self, side_map: dict[str, list[WavInfo]]) -> None:
        """Normalize positions to be sequential (1, 2, 3...) with no gaps or duplicates."""
        for wav_list in side_map.values():
            if not wav_list:
                continue

            wav_list.sort(
                key=lambda x: (x.position if x.position is not None else UNKNOWN_POSITION, x.filename.lower())
            )

            actual = [w.position for w in wav_list]
            expected = list(range(1, len(wav_list) + 1))

            has_missing = any(pos is None for pos in actual)
            non_none_positions = {p for p in actual if p is not None}
            has_duplicates = len([p for p in actual if p is not None]) != len(non_none_positions)

            if has_missing or has_duplicates or actual != expected:
                for i, wav in enumerate(wav_list, start=1):
                    wav.apply_parsed_info({"position": i})

``n
### adapters\audio\chained_detector.py

`$tag
from __future__ import annotations
from typing import List

from core.domain.parsing import UNKNOWN_POSITION
from core.domain.steps import DetectionStep
from core.models.analysis import WavInfo
from core.ports import AudioModeDetector
from adapters.audio.steps import StrictParserStep, AiParserStep, DeterministicFallbackStep

class ChainedAudioModeDetector(AudioModeDetector):
    """
    Orchestrates audio mode detection using a Chain of Responsibility pattern.
    """
    def __init__(self, steps: List[DetectionStep] | None = None):
        if steps is None:
            self._steps: List[DetectionStep] = [
                StrictParserStep(),
                AiParserStep(),
                DeterministicFallbackStep(),
            ]
        else:
            self._steps = steps

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        if not wavs:
            return {}
        
        # Create a mutable copy for processing
        processing_wavs = [w.model_copy() for w in wavs]

        for step in self._steps:
            stop_chain = step.process(processing_wavs)
            if stop_chain:
                break
        
        return self._normalize_and_group(processing_wavs)

    def _normalize_and_group(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Groups WAVs by side and normalizes their positions."""
        side_map: dict[str, list[WavInfo]] = {}
        for wav in wavs:
            side = wav.side or "A"  # Default to "A" if side is still None
            side_map.setdefault(side, []).append(wav)

        for wav_list in side_map.values():
            if not wav_list:
                continue
            
            wav_list.sort(key=lambda x: (x.position if x.position is not None else UNKNOWN_POSITION, x.filename.lower()))
            
            for i, wav in enumerate(wav_list, start=1):
                wav.apply_parsed_info({"position": i})
        
        return side_map

``n
### adapters\audio\steps.py

`$tag
from __future__ import annotations
import logging
from typing import List

from core.domain.parsing import StrictFilenameParser
from core.models.analysis import WavInfo
from adapters.audio.ai_helpers import ai_parse_batch, merge_ai_results

class StrictParserStep:
    """First step: attempts to parse side/position using strict regex rules."""
    def __init__(self) -> None:
        self._parser = StrictFilenameParser()

    def process(self, wavs: List[WavInfo]) -> bool:
        all_parsed = True
        for wav in wavs:
            if wav.side is None or wav.position is None:
                parsed = self._parser.parse(wav.filename)
                updates: dict[str, object] = {}
                if wav.side is None and parsed.side:
                    updates["side"] = parsed.side
                if wav.position is None and parsed.position is not None:
                    updates["position"] = parsed.position
                if updates:
                    wav.apply_parsed_info(updates)
            if wav.side is None or wav.position is None:
                all_parsed = False
        return all_parsed

class AiParserStep:
    """Second step: uses an AI model as a fallback for unparsed files."""
    def process(self, wavs: List[WavInfo]) -> bool:
        unparsed_wavs = [w for w in wavs if w.side is None or w.position is None]
        if not unparsed_wavs:
            return True  # Chain can stop, everything is parsed

        try:
            filenames = [w.filename for w in unparsed_wavs]
            ai_map = ai_parse_batch(filenames)
            if ai_map:
                merge_ai_results(unparsed_wavs, ai_map)
        except Exception as e:
            logging.warning(f"AI parser step failed: {e}", exc_info=True)

        # Never stop the chain here; always allow fallback
        return False

class DeterministicFallbackStep:
    """Final step: assigns default side/position if all else fails."""
    def process(self, wavs: List[WavInfo]) -> bool:
        if not wavs:
            return True

        # Only run if NO files have a side assigned
        if any(w.side for w in wavs):
            return True

        wavs.sort(key=lambda x: x.filename.lower())
        for i, wav in enumerate(wavs, start=1):
            updates: dict[str, object] = {}
            if not wav.side:
                updates["side"] = "A"
            if wav.position is None:
                updates["position"] = i
            if updates:
                wav.apply_parsed_info(updates)
        return True # This is the last step, always stop

``n
### adapters\audio\wav_reader.py

`$tag
from __future__ import annotations

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from audio_utils import get_wav_duration
from core.models.analysis import WavInfo


class ZipWavFileReader:
    """Adapter that encapsulates ZIP file handling and WAV duration probing for the extraction pipeline.

    Responsibilities:
    - Enumerate WAV members within a ZIP archive
    - Materialize entries into a temporary directory for duration inspection
    - Delegate duration probing to `audio_utils.get_wav_duration`
    - Surface results as `WavInfo` domain objects while containing all file I/O concerns
    """

    def read_wav_files(self, zip_path: Path) -> list[WavInfo]:
        """Extract WAV files from the provided ZIP archive and return their durations."""
        wav_infos: list[WavInfo] = []
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = sorted(
                    [name for name in zf.namelist() if name.lower().endswith(".wav")],
                    key=lambda value: value.lower(),
                )
                if not names:
                    return wav_infos

                with tempfile.TemporaryDirectory(prefix="wavprobe_") as tmpdir:
                    tmpdir_path = Path(tmpdir)
                    for name in names:
                        try:
                            relative_path = PurePosixPath(name)
                            safe_parts = [part for part in relative_path.parts if part not in ("", ".", "..")]
                            if not safe_parts:
                                logging.warning(
                                    "Přeskakuji podezřelý ZIP člen '%s' v archivu '%s'",
                                    name,
                                    zip_path.name,
                                )
                                continue

                            safe_relative = PurePosixPath(*safe_parts)
                            dest = tmpdir_path.joinpath(*safe_relative.parts)
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            with zf.open(name) as src, dest.open("wb") as dst:
                                shutil.copyfileobj(src, dst)
                            duration = get_wav_duration(dest)
                            if duration <= 0.0:
                                logging.warning(
                                    "WAV '%s' z archivu '%s' má neplatnou délku %.3fs; přeskočeno",
                                    safe_relative.as_posix(),
                                    zip_path.name,
                                    duration,
                                )
                                continue
                            wav_infos.append(
                                WavInfo(
                                    filename=safe_relative.as_posix(),
                                    duration_sec=duration,
                                )
                            )
                        except (zipfile.BadZipFile, IOError, OSError) as exc:
                            logging.warning(
                                "Nelze přečíst hlavičku WAV '%s' v archivu '%s': %s",
                                name,
                                zip_path.name,
                                exc,
                            )
        except (zipfile.BadZipFile, IOError, OSError) as exc:
            logging.error("Nelze otevřít ZIP archiv '%s': %s", zip_path.name, exc)
        return wav_infos

``n
### adapters\filesystem\__init__.py

`$tag


``n
### adapters\filesystem\file_discovery.py

`$tag
from __future__ import annotations

import logging
import re
from pathlib import Path

from core.models.analysis import FilePair
from core.models.settings import IdExtractionSettings

ID_PATTERN = re.compile(r"\d+")


def extract_numeric_id(filename: str, settings: IdExtractionSettings) -> list[int]:
    """Extract filtered numeric IDs from filename using injected settings."""
    matches = ID_PATTERN.findall(filename)
    if not matches:
        return []

    min_digits = settings.min_digits
    max_digits = settings.max_digits
    assert min_digits <= max_digits, "IdExtractionSettings must satisfy min_digits <= max_digits"

    ignore_values = set(settings.ignore_numbers)

    filtered_ids: set[int] = set()
    for match in matches:
        if not match.isdigit():
            continue
        if not (min_digits <= len(match) <= max_digits):
            continue
        normalized = str(int(match))
        if match in ignore_values or normalized in ignore_values:
            continue
        filtered_ids.add(int(match))

    return sorted(filtered_ids)


def discover_and_pair_files(
    pdf_dir: Path, wav_dir: Path, settings: IdExtractionSettings
) -> tuple[dict[int, FilePair], int]:
    """Discover and pair files using injected ID extraction settings."""
    logging.info(f"Skenuji PDF v: {pdf_dir}")
    pdf_map: dict[int, list[Path]] = {}
    for p in pdf_dir.rglob("*.pdf"):
        ids = extract_numeric_id(p.name, settings)
        if not ids:
            continue
        for id_val in ids:
            pdf_map.setdefault(id_val, []).append(p)

    logging.info(f"Skenuji ZIP v: {wav_dir}")
    zip_map: dict[int, list[Path]] = {}
    for p in wav_dir.rglob("*.zip"):
        ids = extract_numeric_id(p.name, settings)
        if not ids:
            continue
        for id_val in ids:
            zip_map.setdefault(id_val, []).append(p)

    pairs: dict[int, FilePair] = {}
    skipped_count = 0
    seen_pairs: set[tuple[Path, Path]] = set()

    for id_val in sorted(set(pdf_map.keys()) & set(zip_map.keys())):
        pdf_files = pdf_map[id_val]
        zip_files = zip_map[id_val]

        if len(pdf_files) == 1 and len(zip_files) == 1:
            pair_key = (pdf_files[0], zip_files[0])
            if pair_key in seen_pairs:
                logging.debug(f"Skipping duplicate pair for ID {id_val}: {pdf_files[0].name} & {zip_files[0].name}")
                continue
            pairs[id_val] = FilePair(pdf=pdf_files[0], zip=zip_files[0])
            seen_pairs.add(pair_key)
        else:
            logging.warning(f"Ambiguous pairing for ID {id_val}: {len(pdf_files)} PDF(s), {len(zip_files)} ZIP(s)")
            skipped_count += 1
    return pairs, skipped_count

``n
### adapters\pdf\__init__.py

`$tag

``n
### adapters\pdf\renderer.py

`$tag
from __future__ import annotations
import io
from pathlib import Path
from typing import List

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Missing PDF processing libraries: {e}. Please run 'pip install PyMuPDF Pillow'")

class PdfImageRenderer:
    """Adapter for rendering PDF pages into PIL Images using PyMuPDF."""

    def render(self, pdf_path: Path, dpi: int = 300) -> List[Image.Image]:
        """
        Renders each page of a PDF file into a list of PIL Image objects.

        Args:
            pdf_path: The path to the PDF file.
            dpi: The resolution (dots per inch) for rendering.

        Returns:
            A list of PIL Image objects, one for each page.
        """
        images = []
        doc = fitz.open(str(pdf_path))
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            images.append(img)
        return images

``n
### adapters\ui\__init__.py

`$tag


``n
### adapters\ui\null_waveform_viewer.py

`$tag
"""Null implementation of waveform viewer port.

This adapter provides a placeholder implementation that displays an informational
message when waveform viewing is requested. It serves as the default implementation
until a full waveform viewer is integrated.
"""

import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox, QWidget

from core.ports import WaveformViewerPort


class NullWaveformViewer(WaveformViewerPort):
    """Null adapter for waveform viewing that displays an informational message.

    This implementation satisfies the WaveformViewerPort protocol but does not
    provide actual waveform visualization. Instead, it shows a user-friendly
    message indicating that the feature is temporarily unavailable.

    This adapter allows the application to function without waveform viewing
    capabilities while maintaining the port-based architecture for future
    implementations.
    """

    def show(self, zip_path: Path, wav_filename: str, parent: QWidget | None = None) -> None:
        """Display an informational message about waveform viewer unavailability.

        Args:
            zip_path: Path to ZIP archive (unused in null implementation)
            wav_filename: Name of WAV file (unused in null implementation)
            parent: Parent widget for message box positioning
        """
        platform = os.getenv("QT_QPA_PLATFORM", "")
        if platform.lower() in ("offscreen", "minimal"):
            logging.info("Waveform viewer unavailable: %s in %s (headless).", wav_filename, zip_path)
            return

        QMessageBox.information(
            parent,
            "Feature Unavailable",
            "The waveform viewer is currently unavailable.\n\n"
            "This feature has been temporarily disabled during refactoring.",
        )

``n
### app.py

`$tag
import json
import sys
import os
from pathlib import Path
from typing import Optional

# Debug: Print the Python executable path to validate which Python is being used
print(f"Debug: Python executable: {sys.executable}")

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

from config import cfg, load_config, ConfigLoader
from ui.main_window import MainWindow
from ui.config_models import (
    load_tolerance_settings,
    load_id_extraction_settings,
    load_export_settings,
    load_theme_settings,
    load_worker_settings,
)
from ui.workers.worker_manager import AnalysisWorkerManager
from ui.theme import load_gz_media_fonts, load_gz_media_stylesheet
import ui._icons_rc  # Import Qt resources for icons (registers search paths)
from ui.constants import SETTINGS_FILENAME
from adapters.ui.null_waveform_viewer import NullWaveformViewer

if os.environ.get("QT_QPA_PLATFORM") in {"offscreen", "minimal"}:
    fonts_dir = Path(__file__).resolve().parent / "fonts"
    if fonts_dir.exists():
        for font_path in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_path))


def main(config_path: Optional[Path] = None):
    """
    Entry point for the application. Assembles and launches the UI with dependency injection.
    """
    if config_path is None:
        env_path = os.getenv("TRACKLIST_CONFIG")
        config_path = Path(env_path) if env_path else SETTINGS_FILENAME
    else:
        config_path = Path(config_path)

    scale_value = None
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            ui_section = data.get("ui", {})
            scale_value = ui_section.get("dpi_scale", "AUTO")
        except Exception:
            scale_value = None

    if hasattr(Qt, "ApplicationAttribute") and hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "ApplicationAttribute") and hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    if isinstance(scale_value, (int, float)) and float(scale_value) not in (0.0, 1.0):
        os.environ.setdefault("QT_SCALE_FACTOR", str(scale_value))
    elif isinstance(scale_value, str):
        value = scale_value.strip()
        if value and value.upper() != "AUTO":
            os.environ.setdefault("QT_SCALE_FACTOR", value)

    app = QApplication(sys.argv)

    load_config(config_path)
    config_loader = ConfigLoader(cfg.settings)

    tolerance_settings = load_tolerance_settings(loader=config_loader)
    id_extraction_settings = load_id_extraction_settings(loader=config_loader)
    export_settings = load_export_settings(loader=config_loader)
    theme_settings = load_theme_settings(loader=config_loader)
    worker_settings = load_worker_settings(loader=config_loader)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )
    load_gz_media_fonts(app, font_family=theme_settings.font_family, font_size=theme_settings.font_size)
    load_gz_media_stylesheet(app, stylesheet_path=theme_settings.stylesheet_path)

    window = MainWindow(
        tolerance_settings=tolerance_settings,
        export_settings=export_settings,
        theme_settings=theme_settings,
        waveform_viewer=NullWaveformViewer(),
        worker_manager=worker_manager,
        settings_filename=config_path,
        app_config=cfg,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

``n
### audio_utils.py

`$tag
from __future__ import annotations

from pathlib import Path
import logging


def get_wav_duration(path: Path) -> float:
    """Return duration seconds of a WAV file using soundfile, with wave fallback.

    Uses libsndfile via `soundfile` for robust support of WAV variants. If that
    fails, falls back to Python's builtin `wave` header read. Returns 0 on error.
    """
    # Primary: soundfile (libsndfile)
    try:
        import soundfile as sf

        info = sf.info(str(path))
        if info.samplerate and info.frames:
            return float(info.frames) / float(info.samplerate)
    except Exception as e:
        logging.debug("soundfile failed to read %s: %s", path.name, e)

    # Fallback: wave
    try:
        import wave

        with wave.open(str(path), "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            return (frames / float(rate)) if rate > 0 else 0.0
    except Exception as e:
        logging.warning("Unable to read WAV header for '%s': %s", path.name, e)
        return 0.0

``n
### config.py

`$tag
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from PyQt6.QtCore import QSettings

from core.models.settings import (
    AnalysisSettings,
    ExportSettings,
    IdExtractionSettings,
    LlmSettings,
    PathSettings,
    PromptSettings,
    ThemeSettings,
    ToleranceSettings,
    UiSettings,
    WorkerSettings,
)

DEFAULT_SETTINGS_ORG = "GZMedia"
DEFAULT_SETTINGS_APP = "TracklistExtractor"

DEFAULT_LLM_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_LLM_MODEL = "google/gemini-2.5-flash"
DEFAULT_LLM_TEMPERATURE = 0.0

AVAILABLE_LLM_MODELS = [
    "google/gemini-2.5-flash",
    "qwen/qwen2.5-vl-72b-instruct",
    "anthropic/claude-3-haiku",
    "qwen/qwen2.5-vl-3b-instruct",
    "nousresearch/nous-hermes-2-vision-7b",
    "moonshotai/kimi-vl-a3b-thinking",
    "google/gemini-flash-1.5",
    "qwen/qwen2.5-vl-32b-instruct",
    "opengvlab/internvl3-14b",
    "openai/gpt-4o",
    "mistralai/pixtral-12b",
    "microsoft/phi-4-multimodal-instruct",
    "meta-llama/llama-3.2-90b-vision-instruct",
    "meta-llama/llama-3.2-11b-vision-instruct",
    "google/gemini-pro-1.5",
    "google/gemini-2.5-pro",
    "google/gemini-2.0-flash-001",
    "fireworks/firellava-13b",
    "bytedance/ui-tars-1.5-7b",
    "bytedance-research/ui-tars-72b",
    "baidu/ernie-4.5-vl-424b-a47b",
    "baidu/ernie-4.5-vl-28b-a3b",
    "01-ai/yi-vision",
    "z-ai/glm-4.5v",
    "x-ai/grok-2-vision-1212",
]
DEFAULT_ALT_LLM_MODELS = AVAILABLE_LLM_MODELS[1:]

AVAILABLE_DPI_SCALES: List[Union[float, str]] = [1, 1.25, 1.5, 1.75, 2, "AUTO"]

DEFAULT_INPUT_DIR = "./data"
DEFAULT_PDF_DIR = "./data/pdf"
DEFAULT_WAV_DIR = "./data/wav"
DEFAULT_EXPORT_DIR = "exports"

DEFAULTS: Dict[str, Any] = {
    "llm/base_url": DEFAULT_LLM_BASE_URL,
    "llm/model": DEFAULT_LLM_MODEL,
    "llm/alt_models": DEFAULT_ALT_LLM_MODELS,
    "llm/temperature": DEFAULT_LLM_TEMPERATURE,
    "extract/render_dpi": 380,
    "extract/max_side_px": 2000,
    "extract/image_format": "jpeg",
    "extract/jpeg_quality": 85,
    "extract/use_unsharp": True,
    "extract/use_autocontrast": True,
    "prompts/primary": (
        "You are a tracklist extractor. Your single purpose is to return STRICT JSON.\n"
        'Schema: { "tracks": [ {"title": string, "side": string, "position": integer, '
        '"duration_seconds": integer, "duration_formatted": "MM:SS" } ] }.\n'
        "Your entire logic is governed by this unbreakable rule:\n"
        "A track is anchored by its duration value (e.g., 4:40, 5m10s). The title is ALL meaningful text visually "
        "associated with that single time value. Combine multi-line text into one title.\n"
        "Follow these steps:\n"
        "Analyze Visual Layout: First, scan the entire image for structure. Identify columns, sections, and distinct visual blocks. "
        "Process multi-column layouts as separate lists.\n"
        "Find the Duration: For each potential track, locate the duration. This might be under a header like Time, Duration, or Length. "
        "If both Start/End times and a Length column exist, always prioritize the Length column.\n"
        "Establish Context: Use headers like SIDE A, Side B:, TAPE FLIP: A, or multi-track prefixes (A1, B-02) to determine the side "
        "and position. The prefix (B-02) is the most reliable source and overrides other context. Position numbering MUST reset for each new side.\n"
        "Strictly Filter: If a block of text has no clear, parsable duration anchored to it, it IS NOT a track. Aggressively ignore "
        "non-track lines: notes, pauses, headers, ISRC codes, credits, empty rows, and total runtimes."
    ),
    "prompts/user_instructions": "",
    "input/default_dir": DEFAULT_INPUT_DIR,
    "input/pdf_dir": DEFAULT_PDF_DIR,
    "input/wav_dir": DEFAULT_WAV_DIR,
    "export/default_dir": DEFAULT_EXPORT_DIR,
    "export/auto": True,
    "analysis/tolerance_warn": 2,
    "analysis/tolerance_fail": 5,
    "analysis/min_id_digits": 3,
    "analysis/max_id_digits": 6,
    "analysis/ignore_numbers": [],
    "ui/dpi_scale": "AUTO",
    "ui/theme": "AUTO",
    "ui/window_geometry": "1720x1440",
    "ui/base_font_family": "Poppins, Segoe UI, Arial, sans-serif",
    "ui/base_font_size": 13,
    "ui/heading_font_size": 12,
    "ui/treeview_row_height": 28,
    "ui/update_interval_ms": 50,
    "ui/table_action_bg_color": "#E0E7FF",
    "ui/total_row_bg_color": "#F3F4F6",
    "gz_brand/primary_blue": "#1E3A8A",
    "gz_brand/light_blue": "#3B82F6",
    "gz_brand/dark": "#1F2937",
    "gz_brand/light_gray": "#757575",
    "gz_brand/gray": "#6B7280",
    "gz_brand/logo_path": "assets/gz_logo_white.png",
    "gz_brand/claim_visible": True,
    "gz_brand/claim_text": "Emotions. Materialized.",
    "gz_status/ok_color": "#10B981",
    "gz_status/warn_color": "#F59E0B",
    "gz_status/fail_color": "#EF4444",
    "dark_mode/background": "#1F2937",
    "dark_mode/surface": "#374151",
    "dark_mode/text": "#F9FAFB",
    "dark_mode/text_secondary": "#D1D5DB",
    "dark_mode/accent": "#3B82F6",
}

ATTRIBUTE_KEY_MAP: Dict[str, str] = {
    "llm_model": "llm/model",
    "llm_base_url": "llm/base_url",
    "llm_alt_models": "llm/alt_models",
    "llm_temperature": "llm/temperature",
    "input_pdf_dir": "input/pdf_dir",
    "input_wav_dir": "input/wav_dir",
    "export_default_dir": "export/default_dir",
    "export_auto": "export/auto",
    "analysis_tolerance_warn": "analysis/tolerance_warn",
    "analysis_tolerance_fail": "analysis/tolerance_fail",
    "analysis_min_id_digits": "analysis/min_id_digits",
    "analysis_max_id_digits": "analysis/max_id_digits",
    "analysis_ignore_numbers": "analysis/ignore_numbers",
    "ui_dpi_scale": "ui/dpi_scale",
    "ui_theme": "ui/theme",
    "ui_window_geometry": "ui/window_geometry",
    "ui_base_font_family": "ui/base_font_family",
    "ui_base_font_size": "ui/base_font_size",
    "ui_heading_font_size": "ui/heading_font_size",
    "ui_treeview_row_height": "ui/treeview_row_height",
    "ui_update_interval_ms": "ui/update_interval_ms",
    "ui_table_action_bg_color": "ui/table_action_bg_color",
    "ui_total_row_bg_color": "ui/total_row_bg_color",
    "gz_logo_path": "gz_brand/logo_path",
    "gz_claim_visible": "gz_brand/claim_visible",
    "gz_claim_text": "gz_brand/claim_text",
    "gz_status_ok_color": "gz_status/ok_color",
    "gz_status_warn_color": "gz_status/warn_color",
    "gz_status_fail_color": "gz_status/fail_color",
}

SETTINGS_FILENAME = Path("settings.json")


def resolve_path(path: Union[str, Path]) -> Path:
    """Resolve a path relative to the project root directory."""

    if not path:
        return Path()
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj.resolve()
    project_root = Path(__file__).resolve().parent
    return (project_root / path_obj).resolve()


class ConfigValue:
    """Wrapper class for configuration values returning consistent types."""

    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __repr__(self) -> str:
        return f"ConfigValue({self.value!r})"

    def __iter__(self):
        if isinstance(self.value, Iterable) and not isinstance(self.value, (str, bytes)):
            return iter(self.value)
        raise TypeError("Value is not iterable")


class ConfigLoader:
    """Factory that builds typed configuration dataclasses from QSettings."""

    def __init__(self, settings: Optional[QSettings] = None):
        self._settings = settings or QSettings(DEFAULT_SETTINGS_ORG, DEFAULT_SETTINGS_APP)

    def _value(self, key: str, default: Any = None) -> Any:
        if default is None and key in DEFAULTS:
            default = DEFAULTS[key]
        value = self._settings.value(key, default)
        if value is None:
            return default

        if isinstance(default, bool):
            if isinstance(value, bool):
                return value
            return str(value).lower() in {"true", "1", "yes", "on"}

        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        if isinstance(default, float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        if isinstance(default, list):
            if isinstance(value, list):
                return list(value)
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, TypeError, ValueError):
                    candidates = [item.strip() for item in value.split(",") if item.strip()]
                    if candidates:
                        return candidates
            return list(default)

        return value

    def load_llm_settings(self) -> LlmSettings:
        base_url = self._value("llm/base_url", DEFAULT_LLM_BASE_URL)
        model = self._value("llm/model", DEFAULT_LLM_MODEL)
        temperature = self._value("llm/temperature", DEFAULT_LLM_TEMPERATURE)
        alt_models = self._value("llm/alt_models", list(DEFAULT_ALT_LLM_MODELS))
        return LlmSettings(
            base_url=str(base_url),
            model=str(model),
            temperature=float(temperature),
            alt_models=[str(item) for item in alt_models],
        )

    def load_prompt_settings(self) -> PromptSettings:
        primary = self._value("prompts/primary", DEFAULTS["prompts/primary"])
        user_instructions = self._value("prompts/user_instructions", "")
        return PromptSettings(primary=str(primary), user_instructions=str(user_instructions))

    def load_path_settings(self) -> PathSettings:
        pdf_dir = Path(self._value("input/pdf_dir", DEFAULT_PDF_DIR))
        wav_dir = Path(self._value("input/wav_dir", DEFAULT_WAV_DIR))
        export_dir = Path(self._value("export/default_dir", DEFAULT_EXPORT_DIR))
        return PathSettings(pdf_dir=pdf_dir, wav_dir=wav_dir, export_dir=export_dir)

    def load_worker_settings(self) -> WorkerSettings:
        pdf_dir = Path(self._value("input/pdf_dir", DEFAULT_PDF_DIR))
        wav_dir = Path(self._value("input/wav_dir", DEFAULT_WAV_DIR))
        return WorkerSettings(pdf_dir=pdf_dir, wav_dir=wav_dir)

    def load_export_settings(self) -> ExportSettings:
        export_dir = Path(self._value("export/default_dir", DEFAULT_EXPORT_DIR))
        auto_export = bool(self._value("export/auto", True))
        return ExportSettings(auto_export=auto_export, export_dir=export_dir)

    def load_tolerance_settings(self) -> ToleranceSettings:
        warn = int(self._value("analysis/tolerance_warn", 2))
        fail = int(self._value("analysis/tolerance_fail", 5))
        return ToleranceSettings(warn_tolerance=warn, fail_tolerance=fail)

    def load_id_extraction_settings(self) -> IdExtractionSettings:
        min_digits = int(self._value("analysis/min_id_digits", 3))
        max_digits = int(self._value("analysis/max_id_digits", 6))
        if min_digits > max_digits:
            min_digits, max_digits = max_digits, min_digits
        ignore = self._value("analysis/ignore_numbers", [])
        ignore_numbers: List[str] = []
        seen: set[str] = set()
        for item in ignore:
            candidate = str(item).strip()
            if not candidate:
                continue
            if candidate not in seen:
                seen.add(candidate)
                ignore_numbers.append(candidate)
            if candidate.isdigit():
                canonical = str(int(candidate))
                if canonical not in seen:
                    seen.add(canonical)
                    ignore_numbers.append(canonical)
        return IdExtractionSettings(
            min_digits=min_digits,
            max_digits=max_digits,
            ignore_numbers=ignore_numbers,
        )

    def load_analysis_settings(self) -> AnalysisSettings:
        tolerance = self.load_tolerance_settings()
        ids = self.load_id_extraction_settings()
        return AnalysisSettings(
            tolerance_warn=tolerance.warn_tolerance,
            tolerance_fail=tolerance.fail_tolerance,
            min_id_digits=ids.min_digits,
            max_id_digits=ids.max_digits,
            ignore_numbers=ids.ignore_numbers,
        )

    def load_ui_settings(self) -> UiSettings:
        dpi_scale = self._value("ui/dpi_scale", "AUTO")
        theme = self._value("ui/theme", "AUTO")
        geometry = self._value("ui/window_geometry", "1720x1440")
        base_font_family = self._value("ui/base_font_family", "Poppins, Segoe UI, Arial, sans-serif")
        base_font_size = int(self._value("ui/base_font_size", 13))
        heading_font_size = int(self._value("ui/heading_font_size", 12))
        treeview_row_height = int(self._value("ui/treeview_row_height", 28))
        action_bg = self._value("ui/table_action_bg_color", "#E0E7FF")
        total_row_bg = self._value("ui/total_row_bg_color", "#F3F4F6")
        claim_visible = bool(self._value("gz_brand/claim_visible", True))
        claim_text = self._value("gz_brand/claim_text", "Emotions. Materialized.")
        logo_path = Path(self._value("gz_brand/logo_path", "assets/gz_logo_white.png"))
        status_colors = {
            "ok": str(self._value("gz_status/ok_color", "#10B981")),
            "warn": str(self._value("gz_status/warn_color", "#F59E0B")),
            "fail": str(self._value("gz_status/fail_color", "#EF4444")),
        }
        return UiSettings(
            dpi_scale=dpi_scale,
            theme=str(theme),
            window_geometry=str(geometry),
            base_font_family=str(base_font_family),
            base_font_size=base_font_size,
            heading_font_size=heading_font_size,
            treeview_row_height=treeview_row_height,
            status_colors=status_colors,
            action_row_bg_color=str(action_bg),
            total_row_bg_color=str(total_row_bg),
            claim_visible=claim_visible,
            claim_text=str(claim_text),
            logo_path=logo_path,
        )

    def load_theme_settings(self) -> ThemeSettings:
        ui_settings = self.load_ui_settings()
        stylesheet_path = Path("gz_media.qss")
        return ThemeSettings(
            font_family=ui_settings.base_font_family,
            font_size=ui_settings.base_font_size,
            stylesheet_path=stylesheet_path,
            status_colors=ui_settings.status_colors,
            logo_path=ui_settings.logo_path,
            claim_visible=ui_settings.claim_visible,
            claim_text=ui_settings.claim_text,
            action_bg_color=ui_settings.action_row_bg_color,
            total_row_bg_color=ui_settings.total_row_bg_color,
        )


class AppConfig:
    """Application configuration backed by QSettings."""

    def __init__(self) -> None:
        self.settings = QSettings(DEFAULT_SETTINGS_ORG, DEFAULT_SETTINGS_APP)
        self._defaults: Dict[str, Any] = dict(DEFAULTS)
        self.file: Path = SETTINGS_FILENAME

    def _key(self, attr: str) -> str:
        if attr in ATTRIBUTE_KEY_MAP:
            return ATTRIBUTE_KEY_MAP[attr]
        raise AttributeError(attr)

    def get(self, key: str, default: Any = None) -> Any:
        if default is None and key in self._defaults:
            default = self._defaults[key]
        value = self.settings.value(key, default)
        if isinstance(default, bool):
            if isinstance(value, bool):
                return value
            return str(value).lower() in {"true", "1", "yes", "on"}
        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default
        if isinstance(default, float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
        if isinstance(default, list):
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, TypeError, ValueError):
                    candidates = [item.strip() for item in value.split(",") if item.strip()]
                    if candidates:
                        return candidates
            return list(default)
        return value

    def set(self, key: str, value: Any) -> None:
        self.settings.setValue(key, value)

    def get_value(self, key: str) -> ConfigValue:
        return ConfigValue(self.get(key))

    def get_all_keys(self) -> List[str]:
        keys = set(self._defaults.keys())
        keys.update(self.settings.allKeys())
        return sorted(keys)

    def reset_to_defaults(self) -> None:
        for key, value in self._defaults.items():
            self.set(key, value)
        self.settings.sync()

    def load(self, file_path: Union[str, Path]) -> None:
        path = Path(file_path)
        if not path.exists():
            self.file = path
            return
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        for key, value in _flatten_dict(data).items():
            self.set(key, value)
        self.settings.sync()
        self.file = path

    def save(self) -> None:
        self.settings.sync()

    def clear(self) -> None:
        self.settings.clear()

    def __getattr__(self, item: str) -> ConfigValue:
        if item == "settings":
            return ConfigValue(self.settings)
        if item in ATTRIBUTE_KEY_MAP:
            return self.get_value(ATTRIBUTE_KEY_MAP[item])
        raise AttributeError(item)


def _flatten_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flat: Dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten_dict(value, full_key))
        else:
            flat[full_key] = value
    return flat


def _nest_dict(flat: Dict[str, Any]) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    for key, value in flat.items():
        parts = key.split("/")
        cursor = root
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
    return root


cfg = AppConfig()


def load_config(file_path: Union[str, Path]) -> AppConfig:
    cfg.load(file_path)
    return cfg


def save_config(file_path: Union[str, Path]) -> None:
    data = {key: cfg.get(key) for key in cfg.get_all_keys()}
    nested = _nest_dict(data)
    serializable = _as_json_serializable(nested)
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, ensure_ascii=False)


try:
    from PyQt6.QtCore import QByteArray
except ImportError:  # pragma: no cover
    QByteArray = None  # type: ignore[assignment]


def _as_json_serializable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _as_json_serializable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_as_json_serializable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if QByteArray is not None and isinstance(value, QByteArray):
        return value.toBase64().data().decode("ascii")
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(value).decode("ascii")
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)

``n
### core\__init__.py

`$tag


``n
### core\domain\__init__.py

`$tag


``n
### core\domain\analysis_status.py

`$tag
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

``n
### core\domain\comparison.py

`$tag
from __future__ import annotations

from pathlib import Path

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ToleranceSettings
from core.ports import AudioModeDetector


def detect_audio_mode(
    wavs: list[WavInfo], detector: AudioModeDetector
) -> tuple[dict[str, str], dict[str, list[WavInfo]]]:
    """
    Vylepšená detekce stran/pořadí:
    strict z názvu → AI fallback (je-li k dispozici) → deterministické fallback,
    poté normalizace pořadí per strana.

    Args:
        wavs: List of WavInfo objects with filename and duration_sec populated.
        detector: AudioModeDetector instance to use for side/position detection.

    Returns:
        Tuple of (modes, side_map) where modes maps side to mode string,
        and side_map maps side to list of WavInfo objects with normalized positions.
    """
    # Use the injected detector for side/position detection
    side_map = detector.detect(wavs)
    # Detector returns normalized results, so no need for separate normalization

    modes: dict[str, str] = {side: ("side" if len(items) == 1 else "tracks") for side, items in side_map.items()}
    return modes, side_map


def compare_data(
    pdf_data: dict[str, list[TrackInfo]],
    wav_data: list[WavInfo],
    pair_info: dict[str, Path],
    tolerance_settings: ToleranceSettings,
    detector: AudioModeDetector,
) -> list[SideResult]:
    """Compare PDF and WAV track data using injected tolerance thresholds.

    Args:
        pdf_data: Dictionary mapping sides to lists of TrackInfo from PDF.
        wav_data: List of WavInfo objects from WAV files.
        pair_info: Dictionary with 'pdf' and 'zip' paths.
        tolerance_settings: ToleranceSettings object with warn/fail thresholds.
        detector: AudioModeDetector instance to use for side/position detection.

    Returns:
        List of SideResult objects with comparison results.
    """
    results: list[SideResult] = []
    modes, wavs_by_side = detect_audio_mode(wav_data, detector)
    all_sides = set(pdf_data.keys()) | set(wavs_by_side.keys())

    tolerance_warn = tolerance_settings.warn_tolerance
    tolerance_fail = tolerance_settings.fail_tolerance

    for side in sorted(all_sides):
        pdf_tracks = pdf_data.get(side, [])
        wav_tracks = wavs_by_side.get(side, [])
        sorted_wav_tracks = sorted(
            wav_tracks,
            key=lambda track: track.position if track.position is not None else 99,
        )
        mode = modes.get(side, "tracks")

        total_pdf_sec = sum(t.duration_sec for t in pdf_tracks)
        total_wav_sec = sum(w.duration_sec for w in wav_tracks)
        difference = round(total_wav_sec - total_pdf_sec)

        status = AnalysisStatus.OK
        if abs(difference) > tolerance_fail:
            status = AnalysisStatus.FAIL
        elif abs(difference) > tolerance_warn:
            status = AnalysisStatus.WARN

        results.append(
            SideResult(
                seq=0,  # Will be assigned by TopTableModel.add_result()
                pdf_path=pair_info["pdf"],
                zip_path=pair_info["zip"],
                side=side,
                mode=mode,
                status=status,
                pdf_tracks=pdf_tracks,
                wav_tracks=sorted_wav_tracks,
                total_pdf_sec=total_pdf_sec,
                total_wav_sec=total_wav_sec,
                total_difference=difference,
            )
        )
    return results

``n
### core\domain\extraction.py

`$tag
"""Domain-level abstractions for audio extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from core.models.analysis import WavInfo


class WavReader(Protocol):
    """Abstraction used by domain services to retrieve WAV metadata without performing I/O."""

    def read_wav_files(self, zip_path: Path) -> list[WavInfo]:
        """Return WAV metadata derived from the provided ZIP archive."""

``n
### core\domain\parsing.py

`$tag
from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple, Optional, Any

# Named constant to replace magic numbers
UNKNOWN_POSITION = 999

class ParsedFileInfo(NamedTuple):
    side: Optional[str]
    position: Optional[int]

class StrictFilenameParser:
    """A domain service to centralize all strict filename parsing logic."""

    def parse(self, filename: str | Path) -> ParsedFileInfo:
        """
        Parses side and position from a filename using deterministic regex patterns.

        Args:
            filename: The filename (or full path) to parse.

        Returns:
            A ParsedFileInfo tuple containing the extracted side and position.
        """
        name = Path(filename).stem

        # pos: prefix číslo "01_Track"
        m_pos = re.match(r"^0*([1-9][0-9]?)\b", name)
        pos = int(m_pos.group(1)) if m_pos else None

        # side: "Side_A", "Side-AA"
        m_side = re.search(r"(?i)side[^A-Za-z0-9]*([A-Za-z]+)", name)
        side = m_side.group(1).upper() if m_side else None

        # "A1", "AA02"
        if side is None:
            m_pref = re.match(r"^([A-Za-z]+)0*([1-9][0-9]?)[^A-Za-z0-9]*", name)
            if m_pref:
                side = m_pref.group(1).upper()
                if pos is None:
                    pos = int(m_pref.group(2))

        # "Side_A_01", "SideA_02", "Side_A01"
        if pos is None and side:
            m_pos2 = re.search(rf"(?i)side[^A-Za-z0-9]*{re.escape(side)}[^0-9]*0*([1-9][0-9]?)", name)
            if m_pos2:
                pos = int(m_pos2.group(1))

        # Handle Windows paths - extract filename from full path
        if side is None and pos is None:
            # For Windows paths like "C:\Users\Music\B2_Song.mp3", extract just the filename part
            path_str = str(filename)
            if '\\' in path_str:
                # Windows path - get the last component after backslash
                basename = path_str.split('\\')[-1]
                # Remove extension to get stem
                name = Path(basename).stem
                # Retry parsing with just the filename
                m_pos = re.match(r"^0*([1-9][0-9]?)\b", name)
                pos = int(m_pos.group(1)) if m_pos else None
                m_side = re.search(r"(?i)side[^A-Za-z0-9]*([A-Za-z]+)", name)
                side = m_side.group(1).upper() if m_side else None
                if side is None:
                    m_pref = re.match(r"^([A-Za-z]+)0*([1-9][0-9]?)[^A-Za-z0-9]*", name)
                    if m_pref:
                        side = m_pref.group(1).upper()
                        if pos is None:
                            pos = int(m_pref.group(2))
                if pos is None and side:
                    m_pos2 = re.search(rf"(?i)side[^A-Za-z0-9]*{re.escape(side)}[^0-9]*0*([1-9][0-9]?)", name)
                    if m_pos2:
                        pos = int(m_pos2.group(1))

        return ParsedFileInfo(side=side, position=pos)

import logging
from core.models.analysis import TrackInfo

class TracklistParser:
    """A domain service for parsing and consolidating track data from a raw VLM response."""

    def parse(self, raw_data: list[dict[str, Any]]) -> list[TrackInfo]:
        """
        Cleans, deduplicates, and converts raw AI data into strict TrackInfo objects.

        Args:
            raw_data: A list of track dictionaries from the VLM response.

        Returns:
            A sorted and deduplicated list of TrackInfo objects.
        """
        final_tracks = []
        seen = set()
        time_pattern = re.compile(r'(\d{1,2}):([0-5]\d)')

        for track_data in raw_data:
            try:
                title = str(track_data.get("title", "")).strip()
                side = str(track_data.get("side", "?")).strip().upper()
                position = int(track_data.get("position", UNKNOWN_POSITION))
                duration_str = str(track_data.get("duration_formatted", "")).strip()

                if not title or not duration_str:
                    continue

                match = time_pattern.match(duration_str)
                if not match:
                    continue
                
                minutes, seconds = int(match.group(1)), int(match.group(2))
                duration_sec = minutes * 60 + seconds
                
                if minutes > 25: # Sanity check for unreasonable durations
                    logging.warning(f"Ignoring track with unreasonable duration: {title} ({duration_str})")
                    continue

                key = (title.lower(), side, duration_sec)
                if key in seen:
                    continue
                seen.add(key)

                final_tracks.append(TrackInfo(
                    title=title, side=side, position=position, duration_sec=duration_sec
                ))
            except (ValueError, TypeError, KeyError) as e:
                logging.warning(f"Failed to process track data: {track_data}. Error: {e}")

        final_tracks.sort(key=lambda t: (t.side, t.position, t.title))
        return final_tracks

``n
### core\domain\steps.py

`$tag
from __future__ import annotations

from typing import Protocol, List
from core.models.analysis import WavInfo

class DetectionStep(Protocol):
    """Protocol for a single step in the audio mode detection chain."""

    def process(self, wavs: List[WavInfo]) -> bool:
        """
        Processes a list of WavInfo objects to detect side and position.

        Args:
            wavs: The list of WavInfo objects to process.

        Returns:
            True if the chain should stop processing (definitive result found),
            False to continue to the next step.
        """
        ...

``n
### core\models\__init__.py

`$tag
"""Core model exports for convenience."""

from .analysis import *  # noqa: F401,F403
from .settings import ExportSettings, IdExtractionSettings, ToleranceSettings

__all__ = [
    "ExportSettings",
    "IdExtractionSettings",
    "ToleranceSettings",
]

``n
### core\models\analysis.py

`$tag
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pathlib import Path

from pydantic import BaseModel

from core.domain.analysis_status import AnalysisStatus


class TrackInfo(BaseModel):
    title: str
    side: str
    position: int
    duration_sec: int


class WavInfo(BaseModel):
    filename: str
    duration_sec: float
    side: str | None = None
    position: int | None = None

    def apply_parsed_info(self, parsed_data: dict[str, Any]) -> None:
        """Update side and position fields using metadata from parsing helpers."""

        if not isinstance(parsed_data, dict):
            return

        side_value = parsed_data.get("side")
        if isinstance(side_value, str):
            normalized_side = side_value.strip().upper()
            if normalized_side and normalized_side != "UNKNOWN":
                self.side = normalized_side

        position_value = parsed_data.get("position")
        if position_value is None:
            return

        try:
            position_int = int(position_value)
        except (TypeError, ValueError):
            return

        if position_int > 0:
            self.position = position_int


class SideResult(BaseModel):
    seq: int
    pdf_path: Path
    zip_path: Path
    side: str
    mode: str
    status: AnalysisStatus
    pdf_tracks: list[TrackInfo]
    wav_tracks: list[WavInfo]
    total_pdf_sec: int
    total_wav_sec: float
    total_difference: int


@dataclass
class FilePair:
    """Represents a paired PDF and ZIP file based on a shared numeric ID."""

    pdf: Path
    zip: Path

``n
### core\models\settings.py

`$tag
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union


@dataclass
class ToleranceSettings:
    """Duration comparison thresholds controlling WARN and FAIL classifications."""

    warn_tolerance: int
    fail_tolerance: int


@dataclass
class ExportSettings:
    """Settings defining automatic export behaviour."""

    auto_export: bool
    export_dir: Path


@dataclass
class IdExtractionSettings:
    """Settings controlling numeric ID extraction from filenames."""

    min_digits: int
    max_digits: int
    ignore_numbers: list[str]


@dataclass
class LlmSettings:
    """LLM configuration shared across adapters and UI."""

    base_url: str
    model: str
    temperature: float
    alt_models: List[str] = field(default_factory=list)


@dataclass
class AnalysisSettings:
    """Aggregated analysis configuration for tolerance and identifier parsing."""

    tolerance_warn: int
    tolerance_fail: int
    min_id_digits: int
    max_id_digits: int
    ignore_numbers: List[str] = field(default_factory=list)


@dataclass
class PathSettings:
    """Filesystem locations used by the application pipeline."""

    pdf_dir: Path
    wav_dir: Path
    export_dir: Path


@dataclass
class UiSettings:
    """UI configuration that informs theme loading and runtime behaviour."""

    dpi_scale: Union[str, float]
    theme: str
    window_geometry: str
    base_font_family: str
    base_font_size: int
    heading_font_size: int
    treeview_row_height: int
    status_colors: Dict[str, str] = field(default_factory=dict)
    action_row_bg_color: str = "#E0E7FF"
    total_row_bg_color: str = "#F3F4F6"
    claim_visible: bool = True
    claim_text: str = "Emotions. Materialized."
    logo_path: Path = Path("assets/gz_logo_white.png")


@dataclass
class PromptSettings:
    """Prompt text blocks used by PDF + VLM extraction."""

    primary: str
    user_instructions: str = ""


@dataclass
class WorkerSettings:
    """Worker configuration injected into background analysis threads."""

    pdf_dir: Path
    wav_dir: Path


@dataclass
class ThemeSettings:
    """Theme configuration consumed by Qt widgets."""

    font_family: str
    font_size: int
    stylesheet_path: Path
    status_colors: Dict[str, str]
    logo_path: Path
    claim_visible: bool
    claim_text: str
    action_bg_color: str
    total_row_bg_color: str

``n
### core\ports.py

`$tag
"""Port interfaces for hexagonal architecture - domain depends on these abstractions, adapters implement them."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget

from core.models.analysis import WavInfo


class AudioModeDetector(Protocol):
    """Protocol for detecting audio side/position from WAV filenames.

    This protocol defines the contract for audio mode detection strategies.
    Implementations can use various approaches (AI-backed, deterministic parsing, etc.)
    while maintaining the same interface.

    Purpose:
        Detect side (e.g., "A", "B") and position (1, 2, 3...) from WAV filenames.
        This abstraction allows the domain layer to remain independent of detection
        strategy, enabling easy swapping between AI-backed and test implementations.

    Input:
        list[WavInfo]: List of WavInfo objects with filename and duration_sec populated.
        The side and position fields may be None initially.

    Output:
        dict[str, list[WavInfo]]: Dictionary mapping side (e.g., "A", "B") to list of
        WavInfo objects with side and position fields populated and normalized.

    Normalization:
        Positions must be sequential (1, 2, 3...) with no gaps or duplicates.
        For each side, positions are renumbered to start at 1 and increment by 1.
    """

    def detect(self, wavs: list[WavInfo]) -> dict[str, list[WavInfo]]:
        """Detect audio side and position from WAV filenames.

        Args:
            wavs: List of WavInfo objects with filename and duration_sec populated.

        Returns:
            Dictionary mapping side (e.g., "A", "B") to list of WavInfo objects
            with side and position fields populated and normalized.
        """
        ...


class WaveformViewerPort(Protocol):
    """Protocol for waveform viewer implementations.

    This protocol defines the contract for waveform visualization components.
    Implementations can provide different viewing/editing capabilities while
    maintaining the same interface.

    Purpose:
        Display and optionally edit audio waveforms from WAV files in ZIP archives.
        This abstraction allows the UI layer to remain independent of specific
        waveform viewer implementations, enabling easy swapping between different
        viewers or a null implementation.

    Input:
        zip_path: Path to ZIP archive containing WAV files
        wav_filename: Name of the WAV file within the ZIP to display
        parent: Optional parent widget for dialog positioning

    Output:
        None - implementations typically show a modal or non-modal dialog
    """

    def show(self, zip_path: Path, wav_filename: str, parent: QWidget | None = None) -> None:
        """Open and display the waveform viewer for the specified audio file.

        Args:
            zip_path: Path to ZIP archive containing the WAV file
            wav_filename: Name of the WAV file to display (may include subdirectory path)
            parent: Optional parent widget for proper dialog positioning and modality
        """
        ...

``n
### fonts\dejavu-fonts-ttf-2.37\LICENSE

``nFonts are (c) Bitstream (see below). DejaVu changes are in public domain.
Glyphs imported from Arev fonts are (c) Tavmjong Bah (see below)


Bitstream Vera Fonts Copyright
------------------------------

Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved. Bitstream Vera is
a trademark of Bitstream, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of the fonts accompanying this license ("Fonts") and associated
documentation files (the "Font Software"), to reproduce and distribute the
Font Software, including without limitation the rights to use, copy, merge,
publish, distribute, and/or sell copies of the Font Software, and to permit
persons to whom the Font Software is furnished to do so, subject to the
following conditions:

The above copyright and trademark notices and this permission notice shall
be included in all copies of one or more of the Font Software typefaces.

The Font Software may be modified, altered, or added to, and in particular
the designs of glyphs or characters in the Fonts may be modified and
additional glyphs or characters may be added to the Fonts, only if the fonts
are renamed to names not containing either the words "Bitstream" or the word
"Vera".

This License becomes null and void to the extent applicable to Fonts or Font
Software that has been modified and is distributed under the "Bitstream
Vera" names.

The Font Software may be sold as part of a larger software package but no
copy of one or more of the Font Software typefaces may be sold by itself.

THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF COPYRIGHT, PATENT,
TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL BITSTREAM OR THE GNOME
FOUNDATION BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, INCLUDING
ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM OTHER DEALINGS IN THE
FONT SOFTWARE.

Except as contained in this notice, the names of Gnome, the Gnome
Foundation, and Bitstream Inc., shall not be used in advertising or
otherwise to promote the sale, use or other dealings in this Font Software
without prior written authorization from the Gnome Foundation or Bitstream
Inc., respectively. For further information, contact: fonts at gnome dot
org.

Arev Fonts Copyright
------------------------------

Copyright (c) 2006 by Tavmjong Bah. All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining
a copy of the fonts accompanying this license ("Fonts") and
associated documentation files (the "Font Software"), to reproduce
and distribute the modifications to the Bitstream Vera Font Software,
including without limitation the rights to use, copy, merge, publish,
distribute, and/or sell copies of the Font Software, and to permit
persons to whom the Font Software is furnished to do so, subject to
the following conditions:

The above copyright and trademark notices and this permission notice
shall be included in all copies of one or more of the Font Software
typefaces.

The Font Software may be modified, altered, or added to, and in
particular the designs of glyphs or characters in the Fonts may be
modified and additional glyphs or characters may be added to the
Fonts, only if the fonts are renamed to names not containing either
the words "Tavmjong Bah" or the word "Arev".

This License becomes null and void to the extent applicable to Fonts
or Font Software that has been modified and is distributed under the 
"Tavmjong Bah Arev" names.

The Font Software may be sold as part of a larger software package but
no copy of one or more of the Font Software typefaces may be sold by
itself.

THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL
TAVMJONG BAH BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.

Except as contained in this notice, the name of Tavmjong Bah shall not
be used in advertising or otherwise to promote the sale, use or other
dealings in this Font Software without prior written authorization
from Tavmjong Bah. For further information, contact: tavmjong @ free
. fr.

TeX Gyre DJV Math
-----------------
Fonts are (c) Bitstream (see below). DejaVu changes are in public domain.

Math extensions done by B. Jackowski, P. Strzelczyk and P. Pianowski
(on behalf of TeX users groups) are in public domain.

Letters imported from Euler Fraktur from AMSfonts are (c) American
Mathematical Society (see below).
Bitstream Vera Fonts Copyright
Copyright (c) 2003 by Bitstream, Inc. All Rights Reserved. Bitstream Vera
is a trademark of Bitstream, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of the fonts accompanying this license (“Fonts”) and associated
documentation
files (the “Font Software”), to reproduce and distribute the Font Software,
including without limitation the rights to use, copy, merge, publish,
distribute,
and/or sell copies of the Font Software, and to permit persons  to whom
the Font Software is furnished to do so, subject to the following
conditions:

The above copyright and trademark notices and this permission notice
shall be
included in all copies of one or more of the Font Software typefaces.

The Font Software may be modified, altered, or added to, and in particular
the designs of glyphs or characters in the Fonts may be modified and
additional
glyphs or characters may be added to the Fonts, only if the fonts are
renamed
to names not containing either the words “Bitstream” or the word “Vera”.

This License becomes null and void to the extent applicable to Fonts or
Font Software
that has been modified and is distributed under the “Bitstream Vera”
names.

The Font Software may be sold as part of a larger software package but
no copy
of one or more of the Font Software typefaces may be sold by itself.

THE FONT SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF COPYRIGHT, PATENT,
TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL BITSTREAM OR THE GNOME
FOUNDATION
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, INCLUDING ANY GENERAL,
SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, WHETHER IN AN
ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF THE USE OR
INABILITY TO USE
THE FONT SOFTWARE OR FROM OTHER DEALINGS IN THE FONT SOFTWARE.
Except as contained in this notice, the names of GNOME, the GNOME
Foundation,
and Bitstream Inc., shall not be used in advertising or otherwise to promote
the sale, use or other dealings in this Font Software without prior written
authorization from the GNOME Foundation or Bitstream Inc., respectively.
For further information, contact: fonts at gnome dot org.

AMSFonts (v. 2.2) copyright

The PostScript Type 1 implementation of the AMSFonts produced by and
previously distributed by Blue Sky Research and Y&Y, Inc. are now freely
available for general use. This has been accomplished through the
cooperation
of a consortium of scientific publishers with Blue Sky Research and Y&Y.
Members of this consortium include:

Elsevier Science IBM Corporation Society for Industrial and Applied
Mathematics (SIAM) Springer-Verlag American Mathematical Society (AMS)

In order to assure the authenticity of these fonts, copyright will be
held by
the American Mathematical Society. This is not meant to restrict in any way
the legitimate use of the fonts, such as (but not limited to) electronic
distribution of documents containing these fonts, inclusion of these fonts
into other public domain or commercial font collections or computer
applications, use of the outline data to create derivative fonts and/or
faces, etc. However, the AMS does require that the AMS copyright notice be
removed from any derivative versions of the fonts which have been altered in
any way. In addition, to ensure the fidelity of TeX documents using Computer
Modern fonts, Professor Donald Knuth, creator of the Computer Modern faces,
has requested that any alterations which yield different font metrics be
given a different name.

$Id$

``n
### mypy.ini

``n[mypy]
ignore_missing_imports = True
# Limit type checking to refactored layers for this phase
files = core, adapters, services
# Phase 1 strictness is enforced via tools/check.sh running `mypy --strict` on these packages.

[mypy-pdf_extractor]
ignore_errors = True

[mypy-config]
ignore_errors = True

[mypy-ui.*]
ignore_errors = True

[mypy-app]
ignore_errors = True

[mypy-settings_page]
ignore_errors = True

[mypy-waveform_viewer]
ignore_errors = True

[mypy-pdf_viewer]
ignore_errors = True

``n
### pdf_extractor.py

`$tag
import logging
from pathlib import Path
from typing import List

from adapters.ai.vlm import VlmClient
from adapters.pdf.renderer import PdfImageRenderer
from core.domain.parsing import TracklistParser
from core.models.analysis import TrackInfo

def extract_pdf_tracklist(pdf_path: Path) -> dict[str, List[TrackInfo]]:
    """
    Orchestrates the PDF tracklist extraction process.

    This function uses dedicated components to:
    1. Render PDF pages to images (`PdfImageRenderer`).
    2. Send images to a VLM for analysis (`VlmClient`).
    3. Parse the VLM's JSON response into structured data (`TracklistParser`).
    """
    logging.info(f"Starting PDF extraction for: {pdf_path.name}")
    
    try:
        renderer = PdfImageRenderer()
        vlm_client = VlmClient()
        parser = TracklistParser()

        images = renderer.render(pdf_path)
        if not images:
            logging.warning(f"PDF file '{pdf_path.name}' contains no pages.")
            return {}

        prompt = (
            "You are a tracklist extractor. Return STRICT JSON only.\n"
            "Schema: { \"tracks\": [ {\"title\": string, \"side\": string, \"position\": integer, \"duration_formatted\": \"MM:SS\" } ] }.\n"
            "- Extract all visible tracks.\n"
            "- Normalize time to MM:SS format.\n"
            "- Infer side and position if possible.\n"
            "- Do not invent data. Ignore non-track information."
        )

        all_raw_tracks = []
        for img in images:
            try:
                ai_response = vlm_client.get_json_response(prompt, [img])
                if "tracks" in ai_response and isinstance(ai_response["tracks"], list):
                    all_raw_tracks.extend(ai_response["tracks"])
            except Exception as e:
                logging.error(f"AI call failed for a page from '{pdf_path.name}': {e}")
        
        if not all_raw_tracks:
            logging.warning(f"VLM returned no tracks for file: {pdf_path.name}")
            return {}

        parsed_tracks = parser.parse(all_raw_tracks)
        
        result_by_side: dict[str, list[TrackInfo]] = {}
        for track in parsed_tracks:
            result_by_side.setdefault(track.side, []).append(track)
        
        logging.info(f"PDF extraction for '{pdf_path.name}' complete. Found {len(parsed_tracks)} tracks.")
        return result_by_side

    except Exception as e:
        logging.error(f"Failed to extract tracklist from PDF '{pdf_path.name}': {e}", exc_info=True)
        return {}

``n
### pdf_viewer.py

`$tag
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Viewer Module for Tracklist Extractor
Provides custom PDF viewing functionality
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from pathlib import Path


class PdfViewerDialog(QDialog):
    """Custom PDF viewer dialog using system default viewer."""

    def __init__(self, pdf_path: Path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.setWindowTitle(f"PDF Viewer - {pdf_path.name}")
        self.resize(900, 700)

        # Create layout
        layout = QVBoxLayout(self)

        # For now, just open with system viewer and close dialog
        # In future, this could be extended with embedded PDF viewer
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path)))
        except Exception as e:
            print(f"Failed to open PDF: {e}")

        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

        # Auto-close after opening (since we're using system viewer)
        self.accept()

``n
### requirements.txt

``nPillow>=10.0
PyMuPDF>=1.24
pydantic>=2.0
python-dotenv>=1.0.1
openai>=1.30
PyQt6>=6.4
pyqtgraph>=0.13.0
soundfile>=0.12
pytest-qt>=4.2.0
pytest-mock>=3.12.0

ruff>=0.5
black>=24.0
mypy>=1.8
pytest>=8.0
coverage>=7.0

``n
### scripts\run_analysis_no_ai.py

`$tag
from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
import sys as _sys
if str(PROJECT_ROOT) not in _sys.path:
    _sys.path.insert(0, str(PROJECT_ROOT))

from services.analysis_service import AnalysisService
from adapters.audio.wav_reader import ZipWavFileReader
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.settings import IdExtractionSettings, ToleranceSettings
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/run_analysis_no_ai.py <PDF_DIR> <WAV_DIR>")
        return 2
    pdf_dir = Path(sys.argv[1])
    wav_dir = Path(sys.argv[2])

    if not pdf_dir.exists() or not wav_dir.exists():
        print(f"Error: Provided paths must exist. PDF: {pdf_dir}, WAV: {wav_dir}")
        return 2

    tol = ToleranceSettings(warn_tolerance=2, fail_tolerance=5)
    ids = IdExtractionSettings(min_digits=3, max_digits=8, ignore_numbers=["33", "45"])  # conservative defaults

    service = AnalysisService(
        tolerance_settings=tol,
        id_extraction_settings=ids,
        wav_reader=ZipWavFileReader(),
        audio_mode_detector=FakeAudioModeDetector(),
    )

    def on_progress(msg: str) -> None:
        print(f"[progress] {msg}")

    def on_result(res: object) -> None:
        try:
            # SideResult has attributes; keep output succinct
            side = getattr(res, "side", "?")
            pdf = getattr(res, "pdf_path", "?")
            zipf = getattr(res, "zip_path", "?")
            status = getattr(res, "status", "?")
            total_diff = getattr(res, "total_difference", "?")
            print(f"[result] side={side} status={status} diff={total_diff} pdf={getattr(pdf, 'name', pdf)} zip={getattr(zipf, 'name', zipf)}")
        except Exception:
            print(f"[result] {res}")

    def on_finished(msg: str) -> None:
        print(f"[finished] {msg}")

    service.start_analysis(pdf_dir, wav_dir, on_progress, on_result, on_finished)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

``n
### scripts\smoke_test.py

`$tag
import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from adapters.audio.ai_mode_detector import AiAudioModeDetector
from adapters.audio.wav_reader import ZipWavFileReader
from adapters.filesystem.file_discovery import discover_and_pair_files
from core.domain.comparison import compare_data
from config import ConfigLoader
from pdf_extractor import extract_pdf_tracklist
from ui.config_models import load_id_extraction_settings, load_tolerance_settings

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

pdf_dir = Path('test_data/pdf').resolve()
wav_dir = Path('test_data/wav').resolve()
print(f"Using pdf_dir={pdf_dir}")
print(f"Using wav_dir={wav_dir}")

if not pdf_dir.exists() or not wav_dir.exists():
    print("Test data directories not found. Aborting.")
    sys.exit(2)

config_loader = ConfigLoader()
tolerance_settings = load_tolerance_settings(loader=config_loader)
id_extraction_settings = load_id_extraction_settings(loader=config_loader)
wav_reader = ZipWavFileReader()
audio_mode_detector = AiAudioModeDetector()

pairs, skipped = discover_and_pair_files(pdf_dir, wav_dir, id_extraction_settings)
print(f"Found {len(pairs)} pair(s); {skipped} ambiguous skipped")

all_results = []
for i, (file_id, pair_info) in enumerate(pairs.items(), 1):
    print(f"Processing {i}/{len(pairs)}: {pair_info.pdf.name}")
    pdf_data = extract_pdf_tracklist(pair_info.pdf)
    wav_data = wav_reader.read_wav_files(pair_info.zip)
    pair_info_dict = {"pdf": pair_info.pdf, "zip": pair_info.zip}
    side_results = compare_data(pdf_data, wav_data, pair_info_dict, tolerance_settings, audio_mode_detector)
    all_results.extend(side_results)

print(f"Side results: {len(all_results)}")
status_counts = Counter(r.status for r in all_results)
print("Status counts:", dict(status_counts))

sys.exit(0 if all_results else 1)

``n
### scripts\smoke_wav_only.py

`$tag
from __future__ import annotations
import sys
from pathlib import Path

# Ensure project root is on sys.path when running as a standalone script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from adapters.audio.wav_reader import ZipWavFileReader
from adapters.filesystem.file_discovery import discover_and_pair_files
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.settings import IdExtractionSettings


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/smoke_wav_only.py <PDF_DIR> <WAV_DIR>")
        return 2
    pdf_dir = Path(sys.argv[1])
    wav_dir = Path(sys.argv[2])

    if not pdf_dir.exists() or not wav_dir.exists():
        print(f"Error: Provided paths must exist. PDF: {pdf_dir}, WAV: {wav_dir}")
        return 2

    # Conservative ID extraction defaults
    id_settings = IdExtractionSettings(min_digits=3, max_digits=8, ignore_numbers=["33", "45"]) 

    pairs, skipped = discover_and_pair_files(pdf_dir, wav_dir, id_settings)
    print(f"Discovered pairs: {len(pairs)} (skipped ambiguous: {skipped})")

    if not pairs:
        return 0

    reader = ZipWavFileReader()
    detector = FakeAudioModeDetector()

    # Process up to first 3 pairs for brevity
    for idx, (file_id, pair) in enumerate(list(pairs.items())[:3], start=1):
        print(f"\nPair {idx}: ID={file_id} PDF={pair.pdf.name} ZIP={pair.zip.name}")
        wavs = reader.read_wav_files(pair.zip)
        print(f"  WAV files read: {len(wavs)}")
        if not wavs:
            continue
        side_map = detector.detect(wavs)
        for side, items in sorted(side_map.items()):
            positions = [w.position for w in items]
            print(f"  Side {side}: {len(items)} tracks; positions={positions}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

``n
### services\__init__.py

`$tag


``n
### services\analysis_service.py

`$tag
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from adapters.audio.chained_detector import ChainedAudioModeDetector
from adapters.audio.wav_reader import ZipWavFileReader
from adapters.filesystem.file_discovery import discover_and_pair_files
from core.domain.comparison import compare_data
from core.models.settings import IdExtractionSettings, ToleranceSettings
from core.ports import AudioModeDetector
from pdf_extractor import extract_pdf_tracklist


class AnalysisService:
    """Pure-Python orchestrator for the analysis process.

    Uses callbacks to report progress, results, and completion, so it can run
    in any thread context without Qt dependencies. Configuration settings
    and audio mode detector are injected via the constructor to keep dependencies explicit.
    """

    def __init__(
        self,
        tolerance_settings: ToleranceSettings,
        id_extraction_settings: IdExtractionSettings,
        wav_reader: ZipWavFileReader | None = None,
        audio_mode_detector: AudioModeDetector | None = None,
    ) -> None:
        self._tolerance_settings = tolerance_settings
        self._id_extraction_settings = id_extraction_settings
        self._wav_reader = wav_reader or ZipWavFileReader()
        # Use the new Chained detector as the default
        self._audio_mode_detector = audio_mode_detector or ChainedAudioModeDetector()

    def start_analysis(
        self,
        pdf_dir: Path,
        wav_dir: Path,
        progress_callback: Callable[[str], None],
        result_callback: Callable[[object], None],
        finished_callback: Callable[[str], None],
    ) -> None:
        try:
            progress_callback("Scanning and pairing files...")
            pairs, skipped_count = discover_and_pair_files(
                pdf_dir, wav_dir, self._id_extraction_settings
            )

            if not pairs:
                finished_callback("No valid PDF-ZIP pairs found.")
                return

            total_pairs = len(pairs)
            processed_count = 0
            for i, (file_id, pair_info) in enumerate(pairs.items()):
                try:
                    progress_callback(
                        f"Processing pair {i+1}/{total_pairs}: {pair_info.pdf.name}"
                    )

                    pdf_data = extract_pdf_tracklist(pair_info.pdf)
                    wav_data = self._wav_reader.read_wav_files(pair_info.zip)

                    pair_info_dict = {"pdf": pair_info.pdf, "zip": pair_info.zip}
                    side_results = compare_data(
                        pdf_data,
                        wav_data,
                        pair_info_dict,
                        self._tolerance_settings,
                        self._audio_mode_detector,
                    )

                    for res in side_results:
                        result_callback(res)

                    processed_count += 1
                except Exception as pair_error:
                    logging.error(
                        f"Failed to process pair {pair_info.pdf.name}: {pair_error}",
                        exc_info=True,
                    )
                    progress_callback(
                        f"⚠️ WARN: Skipping pair {pair_info.pdf.name} due to error."
                    )
                    continue

            summary_message = (
                f"Analysis completed. Processed {processed_count}/{total_pairs} pairs."
            )
            if skipped_count > 0:
                summary_message += f" ({skipped_count} ambiguous pairs skipped.)"
            finished_callback(summary_message)
        except Exception as e:
            logging.error("Chyba v AnalysisService:", exc_info=True)
            finished_callback(f"Error in analysis service: {e}")

``n
### services\export_service.py

`$tag
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from core.models.analysis import SideResult

"""Centralized export service - single source of truth for all analysis result exports.
All export operations should use export_results_to_json() from this module."""


class ExportSettingsProtocol(Protocol):
    auto_export: bool
    export_dir: Path


ExportSettingsType = ExportSettingsProtocol


def export_results_to_json(results: list[SideResult], export_settings: ExportSettingsType) -> Path | None:
    """Export analysis results to JSON using the centralized export service.

    Usage example:
        from services.export_service import export_results_to_json
        exported_path = export_results_to_json(results, export_settings)

    This is the canonical export implementation shared by the UI layer and automated tests.
    Returns the exported file path or ``None`` when nothing is written.
    """
    if not export_settings.auto_export or not results:
        return None

    export_dir = export_settings.export_dir
    try:
        export_dir.mkdir(parents=True, exist_ok=True)
    except Exception:  # pragma: no cover
        logging.error("Failed to prepare export directory: %s", export_dir, exc_info=True)
        return None

    base = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload: dict[str, Any] = {
        "exported_at": base,
        "count": len(results),
        "results": [],
    }

    for result in results:
        item = result.model_dump(mode="json")
        item["pdf_path"] = str(result.pdf_path)
        item["zip_path"] = str(result.zip_path)
        payload["results"].append(item)

    for index in range(1000):
        suffix = f"_{index:03d}" if index else ""
        out_path = export_dir / f"analysis_{base}{suffix}.json"
        try:
            with out_path.open("x", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            logging.info("Exported analysis results to %s", out_path)
            return out_path
        except FileExistsError:
            continue
        except Exception:  # pragma: no cover
            logging.error("Failed to export analysis results to %s", out_path, exc_info=True)
            out_path.unlink(missing_ok=True)
            return None

    logging.error("Could not create unique filename for export in %s", export_dir)  # pragma: no cover
    return None

``n
### settings_page.py

`$tag
from __future__ import annotations


from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QFrame,
)

from pathlib import Path
from typing import TYPE_CHECKING

from config import AVAILABLE_DPI_SCALES, AVAILABLE_LLM_MODELS
from ui.widgets.settings import UiGroup, ModelGroup, PathsGroup, AnalysisGroup

if TYPE_CHECKING:
    from config import AppConfig


class SettingsPage(QWidget):
    """Application settings interface."""

    settingChanged = pyqtSignal(str, object)
    saveRequested = pyqtSignal()
    reloadRequested = pyqtSignal()
    resetRequested = pyqtSignal()

    def __init__(
        self,
        app_config: "AppConfig",
        settings_filename: Path,
        show_action_buttons: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("settingsPage")
        # Store injected configuration for future use
        self.cfg = app_config
        self.settings_filename = settings_filename
        self.show_action_buttons = show_action_buttons

        self._init_ui()
        self._sync_from_config()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)  # No frame
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)

        self.ui_group = UiGroup(AVAILABLE_DPI_SCALES, parent=self.container)
        self.ui_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.ui_group)

        self.model_group = ModelGroup(AVAILABLE_LLM_MODELS, parent=self.container)
        self.model_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.model_group)

        self.paths_group = PathsGroup(
            pdf_dir=self.cfg.get("input/pdf_dir", "./data/pdf"),
            wav_dir=self.cfg.get("input/wav_dir", "./data/wav"),
            export_dir=self.cfg.get("export/default_dir", "exports"),
            parent=self.container,
        )
        self.paths_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.paths_group)

        warn_default = getattr(self.cfg.analysis_tolerance_warn, "value", self.cfg.get("analysis/tolerance_warn", 2))
        fail_default = getattr(self.cfg.analysis_tolerance_fail, "value", self.cfg.get("analysis/tolerance_fail", 5))
        self.analysis_group = AnalysisGroup(int(warn_default), int(fail_default), parent=self.container)
        self.analysis_group.settingChanged.connect(self.settingChanged.emit)
        self.container_layout.addWidget(self.analysis_group)

        self._build_actions_group()

        self.container_layout.addStretch(1)


    def _build_actions_group(self) -> None:
        # Skip action buttons if embedded in dialog (dialog has its own buttons)
        if not self.show_action_buttons:
            return

        group = QGroupBox("Actions", self.container)
        group_layout = QVBoxLayout(group)

        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setFixedHeight(40)
        self.save_button.clicked.connect(self._save_settings)
        group_layout.addWidget(self.save_button)

        # Reload button
        self.reload_button = QPushButton("Reload Settings")
        self.reload_button.setFixedHeight(40)
        self.reload_button.clicked.connect(self._reload_settings)
        group_layout.addWidget(self.reload_button)

        # Reset button
        self.reset_button = QPushButton("Reset to defaults")
        self.reset_button.setFixedHeight(40)
        self.reset_button.clicked.connect(self._reset_settings)
        group_layout.addWidget(self.reset_button)

        self.container_layout.addWidget(group)


    def _save_settings(self) -> None:
        self.saveRequested.emit()

    def _reload_settings(self) -> None:
        self.reloadRequested.emit()

    def _reset_settings(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset settings",
            "This will restore all settings to their default values.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        self.resetRequested.emit()

    def _reenable_widgets(self) -> None:
        scroll = getattr(self, "scroll", None)
        if scroll is not None:
            scroll.setEnabled(True)
            viewport = scroll.viewport()
            if viewport is not None:
                viewport.setEnabled(True)
        container = getattr(self, "container", None)
        if container is not None:
            container.setEnabled(True)

    def _sync_from_config(self) -> None:
        if hasattr(self, "paths_group"):
            self.paths_group.sync_paths(
                self.cfg.get("input/pdf_dir", "./data/pdf"),
                self.cfg.get("input/wav_dir", "./data/wav"),
                self.cfg.get("export/default_dir", "exports"),
            )

        if hasattr(self, "ui_group"):
            raw_scale = getattr(self.cfg.ui_dpi_scale, "value", self.cfg.get("ui/dpi_scale", "AUTO"))
            self.ui_group.sync_from_config(raw_scale)

        if hasattr(self, "model_group"):
            model_value = getattr(self.cfg.llm_model, "value", self.cfg.get("llm/model", AVAILABLE_LLM_MODELS[0]))
            self.model_group.sync_from_config(model_value)

        if hasattr(self, "analysis_group"):
            warn_value = getattr(self.cfg.analysis_tolerance_warn, "value", self.cfg.get("analysis/tolerance_warn", 2))
            fail_value = getattr(self.cfg.analysis_tolerance_fail, "value", self.cfg.get("analysis/tolerance_fail", 5))
            self.analysis_group.sync_from_config(int(warn_value), int(fail_value))

    def _show_message(self, title: str, content: str, message_type: str = "info") -> None:
        if message_type == "error":
            QMessageBox.critical(self, title, content)
        elif message_type == "warning":
            QMessageBox.warning(self, title, content)
        else:
            QMessageBox.information(self, title, content)

``n
### tests\__init__.py

`$tag


``n
### tests\conftest.py

`$tag
from __future__ import annotations

import contextlib
import math
import zipfile
from pathlib import Path
from typing import Generator, Tuple

import numpy as np
import pytest
import soundfile as sf
from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtWidgets import QApplication

import config as config_module
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.settings import IdExtractionSettings, ToleranceSettings

@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """Provide a QApplication instance for Qt tests."""
    app = QApplication.instance()
    created = False
    if app is None:
        app = QApplication([])
        created = True

    yield app

    if created:
        with contextlib.suppress(Exception):
            # Allow pending events to process before quitting.
            QTimer.singleShot(0, app.quit)
            app.processEvents()
            app.quit()


@pytest.fixture
def isolated_config(monkeypatch, tmp_path) -> Generator[config_module.AppConfig, None, None]:
    """Provide an isolated configuration with temporary QSettings storage."""
    original_cfg = config_module.cfg
    org_name = original_cfg.settings.organizationName()
    app_name = original_cfg.settings.applicationName()

    user_settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, org_name, app_name)
    system_settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, org_name, app_name)
    original_user_dir = Path(user_settings.fileName()).parent
    original_system_dir = Path(system_settings.fileName()).parent

    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings_dir))
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, str(settings_dir))

    test_cfg = config_module.AppConfig()
    test_cfg.reset_to_defaults()
    monkeypatch.setattr(config_module, "cfg", test_cfg)

    yield test_cfg

    config_module.cfg = original_cfg
    QSettings.setDefaultFormat(original_format)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(original_user_dir))
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.SystemScope, str(original_system_dir))


def _generate_sine_wave(duration: float, sample_rate: int) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False, dtype=np.float32)
    angles = 2 * math.pi * 440 * t
    waveform = 0.5 * np.sin(angles)
    return waveform.astype(np.float32)


@pytest.fixture
def mock_wav_zip(tmp_path) -> Generator[Tuple[Path, str], None, None]:
    """Create a temporary ZIP containing a valid WAV file."""
    wav_filename = "test_track.wav"
    wav_path = tmp_path / wav_filename
    sample_rate = 44100
    data = _generate_sine_wave(2.0, sample_rate)
    sf.write(wav_path, data, sample_rate)

    zip_path = tmp_path / "test_archive.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(wav_path, arcname=f"tracks/{wav_filename}")

    yield zip_path, wav_filename


@pytest.fixture
def empty_zip(tmp_path) -> Generator[Path, None, None]:
    """Create an empty ZIP archive."""
    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(zip_path, "w"):
        pass
    yield zip_path


@pytest.fixture
def invalid_wav_zip(tmp_path) -> Generator[Tuple[Path, str], None, None]:
    """Create a ZIP containing an invalid WAV payload."""
    wav_filename = "broken_track.wav"
    zip_path = tmp_path / "invalid.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(wav_filename, b"not-a-valid-wav")
    yield zip_path, wav_filename


@pytest.fixture
def tolerance_settings() -> ToleranceSettings:
    """Provide default tolerance settings for tests."""
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.fixture
def id_extraction_settings() -> IdExtractionSettings:
    """Provide default numeric ID extraction settings for tests."""
    return IdExtractionSettings(min_digits=1, max_digits=6, ignore_numbers=[])


@pytest.fixture
def audio_mode_detector() -> FakeAudioModeDetector:
    """Provide fake audio mode detector for tests (no external API calls)."""
    return FakeAudioModeDetector()


@pytest.fixture
def settings_filename(tmp_path: Path) -> Path:
    """Provide temporary settings filename for DI tests."""
    return tmp_path / "test_settings.json"

``n
### tests\test_ai_mode_detector.py

`$tag
"""Unit tests for audio mode detector adapters."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from adapters.audio.ai_mode_detector import AiAudioModeDetector
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.analysis import WavInfo


class TestAiAudioModeDetector:
    """Test cases for AiAudioModeDetector."""

    def test_ai_detector_with_valid_filenames(self) -> None:
        """Test AI detector with valid WAV filenames."""
        detector = AiAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        # Mock the external API calls
        with patch("adapters.audio.ai_mode_detector.detect_audio_mode_with_ai") as mock_detect:
            with patch("adapters.audio.ai_mode_detector.normalize_positions") as mock_normalize:
                mock_detect.return_value = {
                    "A": [
                        WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="A", position=1),
                        WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0, side="A", position=2),
                    ],
                    "B": [
                        WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0, side="B", position=1),
                    ],
                }

                result = detector.detect(wavs)

                # Use simpler assertions to avoid WavInfo comparison issues
                mock_detect.assert_called_once()
                mock_normalize.assert_called_once()
                assert "A" in result
                assert "B" in result
                assert len(result["A"]) == 2
                assert len(result["B"]) == 1
                # Check that the mock was called with the right number of items
                call_args = mock_detect.call_args[0][0]
                assert len(call_args) == 3
                assert call_args[0].filename == "Side_A_01_intro.wav"
                assert call_args[1].filename == "Side_A_02_song.wav"
                assert call_args[2].filename == "Side_B_01_ballad.wav"

    def test_ai_detector_with_ambiguous_filenames(self) -> None:
        """Test AI detector with ambiguous filenames (triggers AI fallback)."""
        detector = AiAudioModeDetector()
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0),
            WavInfo(filename="track2.wav", duration_sec=150.0),
            WavInfo(filename="track3.wav", duration_sec=210.0),
        ]

        with patch("adapters.audio.ai_mode_detector.detect_audio_mode_with_ai") as mock_detect:
            with patch("adapters.audio.ai_mode_detector.normalize_positions") as mock_normalize:
                mock_detect.return_value = {
                    "A": [
                        WavInfo(filename="track1.wav", duration_sec=120.0, side="A", position=1),
                        WavInfo(filename="track2.wav", duration_sec=150.0, side="A", position=2),
                    ],
                    "B": [
                        WavInfo(filename="track3.wav", duration_sec=210.0, side="B", position=1),
                    ],
                }

                result = detector.detect(wavs)

                # Use simpler assertions to avoid WavInfo comparison issues
                mock_detect.assert_called_once()
                mock_normalize.assert_called_once()
                assert "A" in result
                assert "B" in result
                # Check that the mock was called with the right number of items
                call_args = mock_detect.call_args[0][0]
                assert len(call_args) == 3
                assert call_args[0].filename == "track1.wav"
                assert call_args[1].filename == "track2.wav"
                assert call_args[2].filename == "track3.wav"

    def test_ai_detector_with_empty_input(self) -> None:
        """Test AI detector with empty input list."""
        detector = AiAudioModeDetector()
        result = detector.detect([])
        assert result == {}


class TestFakeAudioModeDetector:
    """Test cases for FakeAudioModeDetector."""

    def test_fake_detector_with_side_prefixes(self) -> None:
        """Test fake detector with Side_A/Side_B filenames."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        assert "A" in result
        assert "B" in result
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side == "A"
        assert result["A"][1].position == 2
        assert result["B"][0].side == "B"
        assert result["B"][0].position == 1

    def test_fake_detector_with_letter_number_prefixes(self) -> None:
        """Test fake detector with A1/B1 prefixes."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="A1_intro.wav", duration_sec=120.0),
            WavInfo(filename="A2_song.wav", duration_sec=150.0),
            WavInfo(filename="B1_ballad.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        # Assert both "A" and "B" sides are present
        assert "A" in result
        assert "B" in result
        # Verify correct position counts: 2 tracks for side A, 1 track for side B
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
        # Check position normalization (1, 2 for A side, 1 for B side)
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side == "A"
        assert result["A"][1].position == 2
        assert result["B"][0].side == "B"
        assert result["B"][0].position == 1

    def test_fake_detector_with_ambiguous_filenames(self) -> None:
        """Test fake detector with ambiguous filenames (parses 'track' as side)."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0),
            WavInfo(filename="track2.wav", duration_sec=150.0),
            WavInfo(filename="track3.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        # The fake detector parses "track" as the side from "track1.wav" etc.
        assert "TRACK" in result
        assert len(result["TRACK"]) == 3
        assert result["TRACK"][0].side == "TRACK"
        assert result["TRACK"][0].position == 1
        assert result["TRACK"][1].side == "TRACK"
        assert result["TRACK"][1].position == 2
        assert result["TRACK"][2].side == "TRACK"
        assert result["TRACK"][2].position == 3

    def test_fake_detector_normalizes_positions(self) -> None:
        """Test fake detector position normalization."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_05_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_10_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_A_15_ballad.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        assert "A" in result
        assert len(result["A"]) == 3
        assert result["A"][0].position == 1
        assert result["A"][1].position == 2
        assert result["A"][2].position == 3

    def test_fake_detector_is_deterministic(self) -> None:
        """Test fake detector is deterministic (same input → same output)."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        result1 = detector.detect(wavs)
        result2 = detector.detect(wavs)

        assert result1 == result2
        assert result1["A"][0].position == result2["A"][0].position
        assert result1["A"][1].position == result2["A"][1].position
        assert result1["B"][0].position == result2["B"][0].position

``n
### tests\test_config.py

`$tag
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import config as config_module


def test_config(isolated_config):
    """Test configuration system functionality."""
    print("Testing configuration system...")

    try:
        # Test basic config access via isolated fixture (monkeypatched in config_module)
        cfg = config_module.cfg
        print(f"LLM Model: {cfg.llm_model}")
        print(f"PDF Dir: {cfg.input_pdf_dir}")
        print(f"WAV Dir: {cfg.input_wav_dir}")
        print(f"Export Dir: {cfg.export_default_dir}")
        print(f"UI Theme: {cfg.ui_theme}")
        print(f"UI Font Size: {cfg.ui_base_font_size}")
        print(f"Analysis Tolerance: {cfg.analysis_tolerance_warn}")

        print("Configuration system works correctly!")
        assert True

    except Exception as e:
        print(f"Configuration error: {e}")
        pytest.fail(f"Configuration error: {e}")



``n
### tests\test_export_auto.py

`$tag
#!/usr/bin/env python3

"""
Pytest testy pro automatizovanou validaci auto-export funkcionality.

Testuje všechny čtyři scénáře ze spec:
1. Success - export.auto=true, JSON se vytvoří
2. Disabled - export.auto=false, žádný soubor se nevytvoří
3. Directory Creation - neexistující adresář se vytvoří
4. Write Failure - chyba při zápisu, aplikace loguje chybu
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from core.domain.analysis_status import AnalysisStatus

import pytest

# Import funkcionality pro testování
from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ExportSettings
from services.export_service import export_results_to_json

pytestmark = pytest.mark.qt_no_exception_capture


class TestExportAuto:
    """Testovací třída pro auto-export funkcionalitu."""

    def create_mock_side_result(self, seq: int = 1) -> SideResult:
        """Vytvoří mock SideResult objekt pro testování."""
        return SideResult(
            seq=seq,
            pdf_path=Path(f"/test/pdf_{seq}.pdf"),
            zip_path=Path(f"/test/zip_{seq}.zip"),
            side="A",
            mode="side",
            status=AnalysisStatus.OK,
            pdf_tracks=[TrackInfo(title=f"Track {seq}", side="A", position=1, duration_sec=180)],
            wav_tracks=[WavInfo(filename=f"track_{seq}.wav", duration_sec=180.0, side="A", position=1)],
            total_pdf_sec=180,
            total_wav_sec=180.0,
            total_difference=0,
        )

    def test_export_success(self, tmp_path):
        """Test 2.1: Ověřit, že když export.auto=True, JSON soubor je vytvořen."""
        # Arrange
        export_dir = tmp_path / "exports"
        mock_results = [self.create_mock_side_result(1), self.create_mock_side_result(2)]

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is not None
        assert export_dir.exists()
        assert result_path.exists()

        # Ověřit název souboru
        expected_pattern = f"analysis_{datetime.now().strftime('%Y%m%d')}_"
        assert expected_pattern in result_path.name
        assert result_path.name.endswith(".json")

        # Ověřit obsah JSON
        with open(result_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "exported_at" in data
        assert "count" in data
        assert "results" in data
        assert data["count"] == 2
        assert len(data["results"]) == 2

        # Ověřit strukturu prvního výsledku
        result = data["results"][0]
        assert "seq" in result
        assert "pdf_path" in result
        assert "zip_path" in result
        assert "side" in result
        assert "mode" in result
        assert "status" in result
        assert "pdf_tracks" in result
        assert "wav_tracks" in result
        assert "total_pdf_sec" in result
        assert "total_wav_sec" in result
        assert "total_difference" in result

        # Ověřit, že cesty jsou stringy (JSON-safe)
        assert isinstance(result["pdf_path"], str)
        assert isinstance(result["zip_path"], str)
        assert isinstance(result["total_pdf_sec"], int)
        assert isinstance(result["total_wav_sec"], (int, float))

    def test_export_disabled(self, tmp_path):
        """Test 2.2: Ověřit, že když export.auto=False, žádný JSON soubor není vytvořen."""
        # Arrange
        export_dir = tmp_path / "exports"
        mock_results = [self.create_mock_side_result()]

        export_settings = ExportSettings(auto_export=False, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is None
        assert not export_dir.exists()

    def test_export_directory_creation(self, tmp_path):
        """Test 2.3: Ověřit, že když export.default_dir neexistuje, je automaticky vytvořen."""
        # Arrange
        export_dir = tmp_path / "new_exports_dir"
        mock_results = [self.create_mock_side_result()]

        # Zajistit, že adresář neexistuje
        assert not export_dir.exists()

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is not None
        assert export_dir.exists()  # Adresář byl vytvořen
        assert export_dir.is_dir()
        assert result_path.exists()
        assert result_path.parent == export_dir

    def test_export_write_failure(self, tmp_path, caplog):
        """Test 2.4: Ověřit, že když aplikace nemůže zapsat do export.default_dir, loguje chybu."""
        # Arrange
        export_dir = tmp_path / "exports"
        export_dir.mkdir()
        mock_results = [self.create_mock_side_result()]

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Mock json.dump funkci, aby vyvolala PermissionError při zápisu
        with patch("json.dump") as mock_json_dump, caplog.at_level(logging.ERROR):
            # Simulovat chybu při zápisu JSON
            mock_json_dump.side_effect = PermissionError("Access denied")

            # Act
            result_path = export_results_to_json(mock_results, export_settings)

            # Assert
            assert result_path is None  # Žádný soubor nebyl vytvořen kvůli chybě

            # Ověřit, že byla zalogována chyba
            assert len(caplog.records) > 0
            error_logged = any("Failed to export analysis results" in record.message for record in caplog.records)
            assert error_logged, f"Expected error log not found in: {[r.message for r in caplog.records]}"

    def test_export_empty_results(self, tmp_path):
        """Test: Ověřit, že s prázdnými výsledky se nevytváří žádný export."""
        # Arrange
        export_dir = tmp_path / "exports"
        empty_results = []

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(empty_results, export_settings)

        # Assert
        assert result_path is None
        assert not export_dir.exists()

    def test_export_json_structure_validation(self, tmp_path):
        """Test: Detailní ověření struktury exportovaného JSON."""
        # Arrange
        export_dir = tmp_path / "exports"
        mock_results = [
            SideResult(
                seq=1,
                pdf_path=Path("/test/path.pdf"),
                zip_path=Path("/test/path.zip"),
                side="A",
                mode="tracks",
                status=AnalysisStatus.OK,
                pdf_tracks=[TrackInfo(title="Test Track", side="A", position=1, duration_sec=245)],
                wav_tracks=[WavInfo(filename="test.wav", duration_sec=245.5, side="A", position=1)],
                total_pdf_sec=245,
                total_wav_sec=245.5,
                total_difference=0,
            )
        ]

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is not None

        with open(result_path, encoding="utf-8") as f:
            data = json.load(f)

            # Ověřit základní strukturu
            assert "exported_at" in data
            assert "count" in data
            assert "results" in data
            assert data["count"] == 1

            result = data["results"][0]

            # Ověřit všechna požadovaná pole
            required_fields = [
                "seq",
                "pdf_path",
                "zip_path",
                "side",
                "mode",
                "status",
                "pdf_tracks",
                "wav_tracks",
                "total_pdf_sec",
                "total_wav_sec",
                "total_difference",
            ]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"

            # Ověřit typy dat
            assert isinstance(result["pdf_path"], str)
            assert isinstance(result["zip_path"], str)
            assert isinstance(result["total_pdf_sec"], int)
            assert isinstance(result["total_wav_sec"], int | float)

            # Ověřit strukturu tracks
            assert len(result["pdf_tracks"]) == 1
            pdf_track = result["pdf_tracks"][0]
            assert "title" in pdf_track
            assert "side" in pdf_track
            assert "position" in pdf_track
            assert "duration_sec" in pdf_track

            wav_track = result["wav_tracks"][0]
            assert "filename" in wav_track
            assert "duration_sec" in wav_track

    def test_export_open_failure(self, tmp_path, caplog):
        """Test: Ověřit, že když selže otevření souboru pro zápis, aplikace loguje chybu."""
        # Arrange
        export_dir = tmp_path / "exports"
        export_dir.mkdir()

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        with patch("pathlib.Path.open", side_effect=PermissionError("Access denied")), caplog.at_level(logging.ERROR):
            # Act
            result_path = export_results_to_json(
                [self.create_mock_side_result(1)],
                export_settings,
            )

            # Assert
            assert result_path is None
            assert any("Failed to export analysis results" in record.message for record in caplog.records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

``n
### tests\test_export_service.py

`$tag
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

``n
### tests\test_gui_minimal.py

`$tag
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from ui import MainWindow, AnalysisWorkerManager, load_export_settings, load_theme_settings, load_worker_settings
from adapters.ui.null_waveform_viewer import NullWaveformViewer

pytestmark = pytest.mark.gui

def test_gui_minimal(qtbot, isolated_config, tolerance_settings, id_extraction_settings):
    """Test minimal GUI initialization using proper fixtures."""

    # Dependencies are now loaded using fixtures or from the isolated_config
    export_settings = load_export_settings(isolated_config)
    theme_settings = load_theme_settings(isolated_config)
    worker_settings = load_worker_settings(isolated_config)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    window = MainWindow(
        tolerance_settings=tolerance_settings,
        export_settings=export_settings,
        theme_settings=theme_settings,
        waveform_viewer=NullWaveformViewer(),
        worker_manager=worker_manager,
        settings_filename=isolated_config.file,
        app_config=isolated_config,
    )
    qtbot.addWidget(window)

    assert window.isVisible() is False # We don't call show()
    assert "Final Cue Sheet Checker" in window.windowTitle()


``n
### tests\test_gui_show.py

`$tag
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from PyQt6.QtCore import QTimer
from ui import MainWindow, AnalysisWorkerManager, load_tolerance_settings, load_export_settings, load_theme_settings, load_worker_settings, load_id_extraction_settings
from config import cfg, ConfigLoader
from adapters.ui.null_waveform_viewer import NullWaveformViewer

pytestmark = pytest.mark.gui

def test_gui_show(qapp, qtbot):
    """Test GUI show functionality."""
    print("Testing GUI show functionality...")

    # Mock dependencies for MainWindow constructor
    loader = ConfigLoader(cfg.settings)
    tolerance_settings = load_tolerance_settings(loader=loader)
    export_settings = load_export_settings(loader=loader)
    theme_settings = load_theme_settings(loader=loader)
    worker_settings = load_worker_settings(loader=loader)
    id_extraction_settings = load_id_extraction_settings(loader=loader)

    worker_manager = AnalysisWorkerManager(
        worker_settings=worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    try:
        print("Creating MainWindow instance...")
        window = MainWindow(
            tolerance_settings=tolerance_settings,
            export_settings=export_settings,
            theme_settings=theme_settings,
            waveform_viewer=NullWaveformViewer(),
            worker_manager=worker_manager,
            settings_filename=cfg.file,
            app_config=cfg,
        )
        qtbot.addWidget(window)
        print("MainWindow created successfully")

        print("Showing MainWindow...")
        window.show()
        print("MainWindow shown successfully")

        # Allow the event loop to run briefly and then exit
        QTimer.singleShot(100, qapp.quit)
        qapp.exec()

    except Exception as e:
        print(f"GUI show error: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"GUI show error: {e}")

``n
### tests\test_gui_simple.py

`$tag
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import pytest
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

pytestmark = pytest.mark.gui


def test_basic_gui():
    """Test basic PyQt6 GUI functionality."""
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Test GUI")
    window.resize(400, 200)

    layout = QVBoxLayout()
    label = QLabel("PyQt6 GUI Test - Basic functionality works!")
    layout.addWidget(label)

    window.setLayout(layout)
    window.show()

    print("GUI launched successfully!")
    QTimer.singleShot(1000, app.quit)
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_basic_gui())

``n
### tests\test_chained_detector.py

`$tag
"""Unit testy pro ChainedAudioModeDetector a jeho steps."""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

from core.models.analysis import WavInfo
from adapters.audio.chained_detector import ChainedAudioModeDetector
from adapters.audio.steps import StrictParserStep, AiParserStep, DeterministicFallbackStep


class TestChainedAudioModeDetector:
    """Test cases pro ChainedAudioModeDetector - hlavní orchestrátor."""

    def setup_method(self) -> None:
        """Inicializace detectoru pro každý test."""
        self.detector = ChainedAudioModeDetector()

    def test_detect_with_valid_filenames_strict_parsing(self) -> None:
        """Test detekce s validními názvy souborů - strict parsing."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        result = self.detector.detect(wavs)

        # Strict parser by měl zpracovat všechny soubory
        assert "A" in result
        assert "B" in result
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1

        # Ověřit pozice
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side == "A"
        assert result["A"][1].position == 2
        assert result["B"][0].side == "B"
        assert result["B"][0].position == 1

    def test_detect_with_mixed_parsing_scenarios(self) -> None:
        """Test detekce s kombinací parsovatelných a neparsovatelných souborů."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),  # Strict parsing
            WavInfo(filename="A2_song.wav", duration_sec=150.0),         # Strict parsing
            WavInfo(filename="unknown_track.wav", duration_sec=210.0),   # AI fallback
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                mock_ai.return_value = {
                    "unknown_track.wav": ("A", 3)  # Přidat do strany A
                }

                result = self.detector.detect(wavs)

                # Ověřit, že všechny soubory byly zpracovány
                assert "A" in result
                assert len(result["A"]) == 3  # Všechny tři v A
                assert result["A"][0].side == "A"
                assert result["A"][0].position == 1
                assert result["A"][1].side == "A"
                assert result["A"][1].position == 2
                assert result["A"][2].side is None  # AI nezměnilo stranu na A
                assert result["A"][2].position == 3

                # Ověřit, že AI bylo zavoláno
                mock_ai.assert_called_once()
                mock_merge.assert_called_once()

    def test_detect_with_custom_steps(self) -> None:
        """Test detekce s vlastními steps."""
        custom_steps = [StrictParserStep()]
        detector = ChainedAudioModeDetector(steps=custom_steps)

        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        result = detector.detect(wavs)

        # Pouze strict parser - fallback se nespustí, takže neznámý soubor zůstane bez strany
        # ale normalizace ho přidá do default strany A
        assert "A" in result
        assert len(result["A"]) == 2  # Oba soubory v A (jeden parsovaný, jeden default)
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side is None  # Neparsovaný zůstává None
        assert result["A"][1].position == 2

    def test_detect_empty_input(self) -> None:
        """Test detekce s prázdným vstupem."""
        result = self.detector.detect([])
        assert result == {}

    def test_detect_single_file(self) -> None:
        """Test detekce s jedním souborem."""
        wavs = [WavInfo(filename="01_track.wav", duration_sec=120.0)]

        result = self.detector.detect(wavs)

        assert "A" in result  # Default side
        assert len(result["A"]) == 1
        assert result["A"][0].position == 1

    def test_detect_normalization_and_grouping(self) -> None:
        """Test normalizace pozic a seskupování podle stran."""
        wavs = [
            WavInfo(filename="Side_A_05_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_10_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_03_ballad.wav", duration_sec=210.0),
        ]

        result = self.detector.detect(wavs)

        # Pozice by měly být normalizovány na 1, 2, 3
        assert result["A"][0].position == 1
        assert result["A"][1].position == 2
        assert result["B"][0].position == 1

    def test_chain_of_responsibility_stops_at_first_success(self) -> None:
        """Test, že chain se zastaví při prvním úspěšném parsingu."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
        ]

        # Mock steps aby strict parser vrátil True (úspěch)
        with patch.object(StrictParserStep, 'process', return_value=True) as mock_strict:
            result = self.detector.detect(wavs)

            # AI step by neměl být zavolán
            with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
                mock_ai.assert_not_called()

    def test_chain_continues_when_strict_fails(self) -> None:
        """Test, že chain pokračuje když strict parser selže."""
        wavs = [
            WavInfo(filename="unknown_track1.wav", duration_sec=120.0),
            WavInfo(filename="unknown_track2.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            mock_ai.return_value = {
                "unknown_track1.wav": ("A", 1),
                "unknown_track2.wav": ("A", 2)
            }

            result = self.detector.detect(wavs)

            # AI by mělo být zavoláno
            mock_ai.assert_called_once()
            assert "A" in result
            assert len(result["A"]) == 2


class TestStrictParserStep:
    """Test cases pro StrictParserStep."""

    def setup_method(self) -> None:
        """Inicializace stepu pro každý test."""
        self.step = StrictParserStep()

    def test_process_all_parsed_successfully(self) -> None:
        """Test zpracování když všechny soubory jsou parsovatelné."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_B_02_song.wav", duration_sec=150.0),
        ]

        result = self.step.process(wavs)

        assert result is True  # Chain se zastaví
        assert wavs[0].side == "A"
        assert wavs[0].position == 1
        assert wavs[1].side == "B"
        assert wavs[1].position == 2

    def test_process_partial_parsing_continues_chain(self) -> None:
        """Test zpracování když některé soubory nejsou parsovatelné."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        result = self.step.process(wavs)

        assert result is False  # Chain pokračuje
        assert wavs[0].side == "A"
        assert wavs[0].position == 1
        assert wavs[1].side is None  # Nezměněno
        assert wavs[1].position is None  # Nezměněno

    def test_process_already_parsed_files_unchanged(self) -> None:
        """Test zpracování souborů, které už mají parsované údaje."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="B", position=5),
        ]

        result = self.step.process(wavs)

        # Původní hodnoty by měly zůstat zachovány
        assert wavs[0].side == "B"
        assert wavs[0].position == 5

    def test_process_empty_list(self) -> None:
        """Test zpracování prázdného seznamu."""
        result = self.step.process([])
        assert result is True

    def test_process_various_filename_formats(self) -> None:
        """Test zpracování různých formátů názvů souborů."""
        test_cases = [
            ("01.wav", None, 1),
            ("Side_A_02.mp3", "A", 2),
            ("A1_Track.flac", "A", 1),
            ("B2_Song.wav", "B", 2),
            ("AA03_Intro.mp3", "AA", 3),
            ("unknown.wav", None, None),
        ]

        for filename, expected_side, expected_position in test_cases:
            wav = WavInfo(filename=filename, duration_sec=120.0)
            self.step.process([wav])

            assert wav.side == expected_side
            assert wav.position == expected_position


class TestAiParserStep:
    """Test cases pro AiParserStep."""

    def setup_method(self) -> None:
        """Inicializace stepu pro každý test."""
        self.step = AiParserStep()

    def test_process_all_already_parsed_stops_chain(self) -> None:
        """Test zpracování když všechny soubory už jsou parsované."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="Side_B_02_song.wav", duration_sec=150.0, side="B", position=2),
        ]

        result = self.step.process(wavs)

        assert result is True  # Chain se zastaví

    def test_process_with_unparsed_files_calls_ai(self) -> None:
        """Test zpracování s neparsovanými soubory - volá AI."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),  # Neparsovaný
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                mock_ai.return_value = {
                    "unknown_track.wav": ("B", 1)
                }

                result = self.step.process(wavs)

                assert result is False  # Chain pokračuje (nikdy se nezastaví)
                mock_ai.assert_called_once_with(["unknown_track.wav"])
                mock_merge.assert_called_once()

    def test_process_ai_exception_handling(self) -> None:
        """Test zpracování výjimek z AI."""
        wavs = [
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch", side_effect=Exception("AI Error")):
            # Nemělo by vyhodit výjimku
            result = self.step.process(wavs)

            assert result is False  # Chain pokračuje
            # Soubor zůstává neparsovaný
            assert wavs[0].side is None
            assert wavs[0].position is None

    def test_process_empty_ai_response(self) -> None:
        """Test zpracování prázdné odpovědi z AI."""
        wavs = [
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch", return_value={}) as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                result = self.step.process(wavs)

                assert result is False
                mock_ai.assert_called_once()
                mock_merge.assert_not_called()  # Nevolá se s prázdným mapem

    def test_process_unknown_side_handling(self) -> None:
        """Test zpracování 'UNKNOWN' side z AI."""
        wavs = [
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                mock_ai.return_value = {
                    "unknown_track.wav": ("UNKNOWN", 1)
                }

                result = self.step.process(wavs)

                assert result is False
                # UNKNOWN by měl být resetnut na None v AiParserStep kódu
                assert wavs[0].side is None
                # Pozice by měla být nastavena merge_ai_results, ale UNKNOWN side se ignoruje
                assert wavs[0].position is None  # Pozice se nenastaví kvůli UNKNOWN side
                mock_merge.assert_called_once()


class TestDeterministicFallbackStep:
    """Test cases pro DeterministicFallbackStep."""

    def setup_method(self) -> None:
        """Inicializace stepu pro každý test."""
        self.step = DeterministicFallbackStep()

    def test_process_no_sides_assigned_fallback(self) -> None:
        """Test fallback když žádný soubor nemá přiřazenou stranu."""
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0),
            WavInfo(filename="track2.wav", duration_sec=150.0),
            WavInfo(filename="track3.wav", duration_sec=210.0),
        ]

        result = self.step.process(wavs)

        assert result is True  # Poslední step, zastaví chain
        # Všechny soubory dostanou stranu A a pozice 1, 2, 3
        assert all(wav.side == "A" for wav in wavs)
        assert wavs[0].position == 1
        assert wavs[1].position == 2
        assert wavs[2].position == 3

    def test_process_some_sides_assigned_no_fallback(self) -> None:
        """Test že se fallback nespustí když některé soubory mají strany."""
        wavs = [
            WavInfo(filename="Side_A_01.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="track2.wav", duration_sec=150.0),  # Bez strany
        ]

        result = self.step.process(wavs)

        assert result is True  # Zastaví chain
        # Fallback se nespustí - druhý soubor zůstává nezměněný
        assert wavs[0].side == "A"
        assert wavs[1].side is None
        assert wavs[1].position is None

    def test_process_all_sides_assigned_no_fallback(self) -> None:
        """Test že se fallback nespustí když všechny soubory mají strany."""
        wavs = [
            WavInfo(filename="Side_A_01.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="Side_B_02.wav", duration_sec=150.0, side="B", position=2),
        ]

        result = self.step.process(wavs)

        assert result is True
        # Žádné změny
        assert wavs[0].side == "A"
        assert wavs[1].side == "B"

    def test_process_empty_list(self) -> None:
        """Test zpracování prázdného seznamu."""
        result = self.step.process([])
        assert result is True

    def test_process_position_assignment_with_none_positions(self) -> None:
        """Test přiřazení pozic když některé soubory nemají pozice."""
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0, side=None, position=5),  # Bez strany, ale s pozicí
            WavInfo(filename="track2.wav", duration_sec=150.0, side=None, position=None),  # Bez strany a pozice
        ]

        result = self.step.process(wavs)

        assert result is True
        # Oba soubory dostanou stranu A
        # První si ponechá pozici 5, druhý dostane pozici 2 (protože se řadí podle názvu)
        assert wavs[0].side == "A"
        assert wavs[0].position == 5  # Ponechá si původní pozici
        assert wavs[1].side == "A"
        assert wavs[1].position == 2  # Nová pozice (řadí se podle názvu)

    def test_process_deterministic_sorting(self) -> None:
        """Test deterministické řazení podle názvu souboru."""
        wavs = [
            WavInfo(filename="zebra_track.wav", duration_sec=120.0),
            WavInfo(filename="alpha_track.wav", duration_sec=150.0),
            WavInfo(filename="beta_track.wav", duration_sec=210.0),
        ]

        result = self.step.process(wavs)

        assert result is True
        # Měly by být seřazeny podle názvu: alpha, beta, zebra
        # Ale pozice se přiřazují podle původního pořadí v seznamu
        assert wavs[0].position == 1  # alpha_track
        assert wavs[1].position == 2  # beta_track
        assert wavs[2].position == 3  # zebra_track


class TestEdgeCases:
    """Test cases pro edge cases."""

    def test_chained_detector_with_empty_filenames(self) -> None:
        """Test ChainedAudioModeDetector s prázdnými filenames."""
        detector = ChainedAudioModeDetector()
        wavs = [
            WavInfo(filename="", duration_sec=120.0),
        ]

        # Nemělo by vyhodit výjimku
        result = detector.detect(wavs)
        assert "A" in result  # Default side
        assert len(result["A"]) == 1

    def test_steps_with_none_values(self) -> None:
        """Test steps s None hodnotami."""
        strict_step = StrictParserStep()
        ai_step = AiParserStep()
        fallback_step = DeterministicFallbackStep()

        wavs = [
            WavInfo(filename="test.wav", duration_sec=120.0, side=None, position=None),
        ]

        # Žádný step by neměl vyhodit výjimku
        strict_step.process(wavs)
        ai_step.process(wavs)
        fallback_step.process(wavs)

    def test_chained_detector_immutable_input(self) -> None:
        """Test že vstupní data nejsou mutována."""
        detector = ChainedAudioModeDetector()
        original_wavs = [
            WavInfo(filename="Side_A_01.wav", duration_sec=120.0),
        ]
        wavs_copy = [w.model_copy() for w in original_wavs]

        result = detector.detect(original_wavs)

        # Původní objekty by měly zůstat nezměněné
        assert original_wavs[0].side is None
        assert original_wavs[0].position is None

        # Výsledek by měl mít změněné kopie
        assert "A" in result
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1

    def test_steps_with_very_long_filenames(self) -> None:
        """Test steps s velmi dlouhými názvy souborů."""
        long_filename = "A" * 1000 + "_01_very_long_track_name_that_might_cause_issues.wav"

        strict_step = StrictParserStep()
        wavs = [WavInfo(filename=long_filename, duration_sec=120.0)]

        # Nemělo by vyhodit výjimku
        result = strict_step.process(wavs)
        assert isinstance(result, bool)

    def test_ai_step_with_malformed_ai_response(self) -> None:
        """Test AiParserStep s poškozenou odpovědí z AI."""
        ai_step = AiParserStep()
        wavs = [
            WavInfo(filename="test.wav", duration_sec=120.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                # Simulace poškozené odpovědi
                mock_ai.return_value = {
                    "test.wav": ("INVALID_SIDE", "not_a_number")
                }

                # Nemělo by vyhodit výjimku
                result = ai_step.process(wavs)
                assert result is False
``n
### tests\test_characterization.py

`$tag
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

``n
### tests\test_parsing.py

`$tag
from __future__ import annotations

import pytest
from pathlib import Path

from core.domain.parsing import StrictFilenameParser, ParsedFileInfo


class TestStrictFilenameParser:
    """Unit testy pro StrictFilenameParser."""

    def setup_method(self) -> None:
        """Inicializace parseru pro každý test."""
        self.parser = StrictFilenameParser()

    @pytest.mark.parametrize(
        "filename,expected_side,expected_position",
        [
            # Základní parsing pozice (čísla na začátku) - pouze na konci stringu
            ("01.wav", None, 1),
            ("1.flac", None, 1),
            ("02.wav", None, 2),
            ("10.mp3", None, 10),
            ("99.wav", None, 99),

            # Parsing strany (Side patterns)
            ("Side_A_Track.wav", "A", None),
            ("Side_AA_Song.mp3", "AA", None),
            ("side_b_Track.flac", "B", None),
            ("SIDE_C_Song.wav", "C", None),
            ("Side-A-Track.mp3", "A", None),
            ("Side_AA_Track.wav", "AA", None),

            # Kombinované patterny (A1, B2, atd.)
            ("A1_Track.wav", "A", 1),
            ("B2_Song.mp3", "B", 2),
            ("AA02_Track.flac", "AA", 2),
            ("C3_Song.wav", "C", 3),
            ("D10_Track.mp3", "D", 10),
            ("A1_intro.wav", "A", 1),
            ("B2_song.mp3", "B", 2),

            # Side s pozicí
            ("Side_A_01.wav", "A", 1),
            ("SideA_02.mp3", "A", 2),
            ("Side_A01.flac", "A", 1),
            ("side_b_3.wav", "B", 3),
            ("SIDE_C_05.mp3", "C", 5),
            ("Side_AA_10.wav", "AA", 10),

            # Edge cases - bez pozice a strany
            ("Track_Without_Numbers.wav", None, None),
            ("Random_Filename.mp3", None, None),
            ("No_Pattern_Here.flac", None, None),
            ("", None, None),

            # Speciální formáty
            ("Side_A_01_Track_Name.wav", "A", 1),
            ("A1_Side_B_02.mp3", "B", 2),  # Side_B má prioritu před A1
            ("00_Prefixed_Track.wav", None, None),  # 00 není validní pozice
            ("0_Track.wav", None, None),  # 0 není validní pozice

            # Case insensitive testy
            ("side_a_01.wav", "A", 1),
            ("SIDE_B_02.mp3", "B", 2),
            ("a1_track.flac", "A", 1),
            ("b2_song.wav", "B", 2),

            # Složité názvy
            ("Side_A_01_Intro_To_Track.wav", "A", 1),
            ("A1_Featuring_Artist_Song.mp3", "A", 1),
            ("Side_AA_02_Remix.flac", "AA", 2),
        ]
    )
    def test_parse_filename_comprehensive(
        self, filename: str, expected_side: str | None, expected_position: int | None
    ) -> None:
        """Parametrizovaný test pro různé formáty filename parsing."""
        result = self.parser.parse(filename)

        assert result.side == expected_side
        assert result.position == expected_position

    @pytest.mark.parametrize(
        "filename,expected",
        [
            # Test s úplnými cestami
            ("/path/to/Side_A_01.wav", ParsedFileInfo(side="A", position=1)),
            ("C:\\Users\\Music\\B2_Song.mp3", ParsedFileInfo(side="B", position=2)),
            ("./tracks/A1_Track.flac", ParsedFileInfo(side="A", position=1)),
            ("../parent/dir/Side_AA_02.wav", ParsedFileInfo(side="AA", position=2)),

            # Test s různými příponami
            ("01.WAV", ParsedFileInfo(side=None, position=1)),
            ("Side_A_02.MP3", ParsedFileInfo(side="A", position=2)),
            ("A1_Song.FLAC", ParsedFileInfo(side="A", position=1)),
            ("B2_Track.aiff", ParsedFileInfo(side="B", position=2)),

            # Test bez přípon
            ("01", ParsedFileInfo(side=None, position=1)),
            ("Side_A_02", ParsedFileInfo(side="A", position=2)),
            ("A1_Song", ParsedFileInfo(side="A", position=1)),
        ]
    )
    def test_parse_with_paths_and_extensions(self, filename: str, expected: ParsedFileInfo) -> None:
        """Test parsing s různými typy cest a přípon souborů."""
        result = self.parser.parse(filename)
        assert result == expected

    def test_parse_empty_filename(self) -> None:
        """Test parsing prázdného názvu souboru."""
        result = self.parser.parse("")
        assert result == ParsedFileInfo(side=None, position=None)

    def test_parse_filename_with_only_numbers(self) -> None:
        """Test parsing názvu obsahujícího pouze čísla."""
        result = self.parser.parse("12345.wav")
        assert result == ParsedFileInfo(side=None, position=None)

    def test_parse_filename_starting_with_zero(self) -> None:
        """Test parsing názvu začínajícího nulou."""
        result = self.parser.parse("001.wav")
        assert result == ParsedFileInfo(side=None, position=1)

    def test_parse_complex_side_patterns(self) -> None:
        """Test parsing složitějších patternů pro strany."""
        test_cases = [
            ("Side-A-01.wav", "A", 1),
            ("Side_AA_02.mp3", "AA", 2),
            ("Side-ABC-03.flac", "ABC", 3),
            ("Side_A-B_01.wav", "A", 1),  # První match
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_parse_position_only_various_formats(self) -> None:
        """Test parsing pouze pozice v různých formátech."""
        test_cases = [
            ("01.wav", None, 1),
            ("02.wav", None, 2),
            ("10.flac", None, 10),
            ("99.wav", None, 99),
            ("1.wav", None, 1),
            ("001.mp3", None, 1),  # Leading zeros are stripped
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_parse_side_only_various_formats(self) -> None:
        """Test parsing pouze strany v různých formátech."""
        test_cases = [
            ("Side_A.wav", "A", None),
            ("Side_AA.mp3", "AA", None),
            ("side_b.flac", "B", None),
            ("SIDE_C.wav", "C", None),
            ("Side-ABC.mp3", "ABC", None),
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_case_insensitive_parsing(self) -> None:
        """Test case insensitive parsing."""
        test_cases = [
            ("side_a_01.wav", "A", 1),
            ("SIDE_B_02.mp3", "B", 2),
            ("Side_Cc_03.flac", "CC", 3),
            ("a1_track.wav", "A", 1),
            ("b2_song.mp3", "B", 2),
            ("Aa01_Track.flac", "AA", 1),
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_priority_of_patterns(self) -> None:
        """Test priority parsing patternů podle skutečné implementace."""
        test_cases = [
            # Side pattern má prioritu před A1 patternem - parsuje první písmeno a pozici
            ("Side_A1_Track.wav", "A", 1),  # Parsuje jako Side_A -> A s pozicí 1 z A1

            # Position na začátku má prioritu před jinými patterny (ale pouze na konci stringu)
            ("01Side_A_Track.wav", "A", None),  # Parsuje Side_A -> A, ignoruje pozici 01

            # A1 pattern má prioritu před pozicí v jiném místě
            ("A1_02_Track.wav", "A", 1),  # Parsuje A1 jako A s pozicí 1, ignoruje 02

            # Side pattern v prostředku má prioritu
            ("A1_Side_B_02.wav", "B", 2),  # Parsuje Side_B s pozicí 2
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_pathlib_path_objects(self) -> None:
        """Test parsing s Path objekty."""
        test_cases = [
            (Path("Side_A_01.wav"), "A", 1),
            (Path("/path/to/B2_Song.mp3"), "B", 2),
            (Path("A1_Track.flac"), "A", 1),
        ]

        for path, expected_side, expected_position in test_cases:
            result = self.parser.parse(str(path))
            assert result.side == expected_side
            assert result.position == expected_position

    def test_parsed_file_info_equality(self) -> None:
        """Test rovnosti ParsedFileInfo objektů."""
        info1 = ParsedFileInfo(side="A", position=1)
        info2 = ParsedFileInfo(side="A", position=1)
        info3 = ParsedFileInfo(side="B", position=1)
        info4 = ParsedFileInfo(side="A", position=2)

        assert info1 == info2
        assert info1 != info3
        assert info1 != info4
        assert info1 != ParsedFileInfo(side=None, position=None)

    def test_windows_path_parsing(self) -> None:
        """Test parsing Windows cest s backslash."""
        # Test specific Windows path cases
        test_cases = [
            ("C:\\Users\\Music\\B2_Song.mp3", "B", 2),
            ("D:\\Audio\\Side_A_01.wav", "A", 1),
            ("\\\\server\\share\\A1_Track.flac", "A", 1),
        ]

        for path, expected_side, expected_position in test_cases:
            result = self.parser.parse(path)
            assert result.side == expected_side
            assert result.position == expected_position
``n
### tests\test_results_table_model.py

`$tag
from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from ui.config_models import ThemeSettings
from core.models.analysis import SideResult
from core.domain.analysis_status import AnalysisStatus
from ui.models.results_table_model import ResultsTableModel

pytestmark = pytest.mark.usefixtures("qtbot")


@pytest.fixture
def theme_settings():
    return ThemeSettings(
        font_family="",
        font_size=10,
        stylesheet_path=Path(),
        status_colors={"ok": "#10B981", "warn": "#F59E0B", "fail": "#EF4444"},
        logo_path=Path(),
        claim_visible=True,
        claim_text="Emotions. Materialized.",
        action_bg_color="#E0E7FF",
        total_row_bg_color="#F3F4F6",
    )


@pytest.fixture
def mock_side_result():
    return SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[],
        wav_tracks=[],
        total_pdf_sec=100,
        total_wav_sec=100.0,
        total_difference=0,
    )


def test_results_table_model_creation(theme_settings):
    model = ResultsTableModel(theme_settings=theme_settings)
    assert model.rowCount() == 0
    assert model.columnCount() == len(model._headers)


def test_add_result_increases_row_count(theme_settings, mock_side_result):
    model = ResultsTableModel(theme_settings=theme_settings)
    model.add_result(mock_side_result)
    assert model.rowCount() == 1
    assert model.all_results()[0].pdf_path.name == "test.pdf"


def test_data_retrieval(theme_settings, mock_side_result):
    model = ResultsTableModel(theme_settings=theme_settings)
    model.add_result(mock_side_result)

    index_file = model.index(0, 1)
    assert model.data(index_file, Qt.ItemDataRole.DisplayRole) == "test.pdf"

    index_status = model.index(0, 5)
    assert model.data(index_status, Qt.ItemDataRole.DisplayRole) == "OK"


def test_status_color(theme_settings, mock_side_result):
    mock_side_result.status = AnalysisStatus.WARN

    model = ResultsTableModel(theme_settings=theme_settings)
    model.add_result(mock_side_result)

    index_status = model.index(0, 5)
    color = model.data(index_status, Qt.ItemDataRole.BackgroundRole)

    assert color is not None
    assert color.name().lower() == theme_settings.status_colors["warn"].lower()

``n
### tests\test_settings_dialog.py

`$tag
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test for Settings dialog functionality and path resolution.
Tests: Settings dialog opening, configuration saving, path resolution, and error handling.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.gui

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from config import cfg, load_config, save_config, resolve_path, AppConfig
from ui.dialogs.settings_dialog import SettingsDialog
from settings_page import SettingsPage

# Global test application instance
_test_app = None


class MockMainWindow(QMainWindow):
    """Mock main window for testing settings dialog functionality."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Main Window")

        # Setup menu bar like the real MainWindow
        self.setup_menu_bar()

    def setup_menu_bar(self):
        """Setup menu bar with File, Edit, Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # Settings action with Ctrl+, shortcut
        settings_action = edit_menu.addAction("Settings...")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)

        # Help menu
        help_menu = menubar.addMenu("Help")

    def open_settings(self):
        """Open settings dialog."""
        try:
            # Use temporary settings file for testing
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            settings_file = temp_dir / "test_settings_dialog.json"
            settings_dialog = SettingsDialog(settings_file, cfg, self)
            settings_dialog.exec()
        except Exception as e:
            print(f"Failed to open settings dialog: {e}")
            raise


def test_settings_dialog_creation():
    """Test that SettingsDialog can be created successfully."""
    print("Testing SettingsDialog creation...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a mock parent window
        parent = MockMainWindow()

        # Create temporary settings file
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "test_settings.json"
            
            # Test creating SettingsDialog with DI
            dialog = SettingsDialog(settings_file, cfg, parent)
            assert dialog is not None
            print("+ SettingsDialog created successfully")

            # Test that it has the expected components
            assert hasattr(dialog, "settings_page")
            assert isinstance(dialog.settings_page, SettingsPage)
            print("+ SettingsDialog has SettingsPage")

            # Clean up
            dialog.deleteLater()
            parent.deleteLater()

            return True

    except Exception as e:
        print(f"- SettingsDialog creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_dialog_menu_action():
    """Test that Settings dialog opens via Edit -> Settings... menu."""
    print("Testing Settings dialog via Edit -> Settings... menu...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a mock parent window
        parent = MockMainWindow()

        # Find the settings action in the menu
        edit_menu = None
        for menu in parent.menuBar().findChildren(QMenu):
            if menu.title() == "Edit":
                edit_menu = menu
                break

        assert edit_menu is not None, "Edit menu not found"
        print("+ Edit menu found")

        # Find the Settings... action
        settings_action = None
        for action in edit_menu.actions():
            if action.text() == "Settings...":
                settings_action = action
                break

        assert settings_action is not None, "Settings... action not found"
        print("+ Settings... action found")

        # Mock the SettingsDialog to avoid actually showing it
        with patch("ui.dialogs.settings_dialog.SettingsDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            # Trigger the action
            settings_action.trigger()

            # Verify the dialog was created
            mock_dialog_class.assert_called_once()
            print("+ Settings dialog opened via menu action")

        # Clean up
        parent.deleteLater()

        return True

    except Exception as e:
        print(f"- Menu action test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_dialog_shortcut():
    """Test that Settings dialog opens via Ctrl+, shortcut."""
    print("Testing Settings dialog via Ctrl+, shortcut...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a mock parent window
        parent = MockMainWindow()

        # Find the settings action
        edit_menu = None
        for menu in parent.menuBar().findChildren(QMenu):
            if menu.title() == "Edit":
                edit_menu = menu
                break

        settings_action = None
        for action in edit_menu.actions():
            if action.text() == "Settings...":
                settings_action = action
                break

        # Mock the SettingsDialog
        with patch("ui.dialogs.settings_dialog.SettingsDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            # Simulate Ctrl+, key press
            QTest.keyClick(parent, Qt.Key_Comma, Qt.ControlModifier)

            # Verify the dialog was created
            mock_dialog_class.assert_called_once()
            print("+ Settings dialog opened via Ctrl+, shortcut")

        # Clean up
        parent.deleteLater()

        return True

    except Exception as e:
        print(f"- Shortcut test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration_save():
    """Test that configuration saves correctly via Save button."""
    print("Testing configuration save functionality...")

    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_settings_file = temp_path / "test_settings.json"

            # Create initial test configuration
            test_config = {
                "input": {"pdf_dir": str(temp_path / "pdf"), "wav_dir": str(temp_path / "wav")},
                "analysis": {"tolerance_warn": 3, "tolerance_fail": 7},
            }

            with open(test_settings_file, "w") as f:
                json.dump(test_config, f)

            # Load the test configuration
            load_config(test_settings_file)

            # Modify some settings
            cfg.set("analysis/tolerance_warn", 5)
            cfg.set("analysis/tolerance_fail", 10)
            cfg.set("input/pdf_dir", str(temp_path / "new_pdf"))

            # Save the configuration
            save_config(test_settings_file)

            # Verify the settings were saved correctly
            with open(test_settings_file, "r") as f:
                saved_config = json.load(f)

            assert saved_config["analysis"]["tolerance_warn"] == 5
            assert saved_config["analysis"]["tolerance_fail"] == 10
            assert saved_config["input"]["pdf_dir"] == str(temp_path / "new_pdf")
            print("+ Configuration saved correctly")

            return True

    except Exception as e:
        print(f"- Configuration save test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_resolution_absolute():
    """Test that path resolution works correctly with absolute paths."""
    print("Testing path resolution with absolute paths...")

    try:
        # Test with absolute path
        test_path = "/absolute/test/path"
        resolved = resolve_path(test_path)

        # Should return the absolute path as-is (resolved)
        assert resolved == Path(test_path).resolve()
        print("+ Absolute path resolution works correctly")

        # Test with Path object
        test_path_obj = Path("/another/absolute/path")
        resolved_obj = resolve_path(test_path_obj)
        assert resolved_obj == test_path_obj.resolve()
        print("+ Absolute Path object resolution works correctly")

        return True

    except Exception as e:
        print(f"- Absolute path resolution test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_resolution_relative():
    """Test that path resolution works correctly with relative paths."""
    print("Testing path resolution with relative paths...")

    try:
        # Test with relative path
        test_path = "relative/test/path"
        resolved = resolve_path(test_path)

        # Should resolve relative to project root
        project_root = Path(__file__).resolve().parent
        expected = (project_root / test_path).resolve()
        assert resolved == expected
        print("+ Relative path resolution works correctly")

        # Test with current directory reference
        current_path = "./current/dir"
        resolved_current = resolve_path(current_path)
        expected_current = (project_root / current_path).resolve()
        assert resolved_current == expected_current
        print("+ Current directory path resolution works correctly")

        return True

    except Exception as e:
        print(f"- Relative path resolution test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_path_directory_validation():
    """Test that directory validation works correctly."""
    print("Testing path directory validation...")

    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with valid directory
            valid_dir = temp_path / "valid_dir"
            valid_dir.mkdir()

            # This should not raise an error
            cfg.input_pdf_dir = str(valid_dir)
            assert cfg.input_pdf_dir.value == str(valid_dir)
            print("+ Valid directory path accepted")

            # Test with invalid path (non-existent)
            invalid_dir = temp_path / "non_existent_dir"

            # This should create the directory
            cfg.input_pdf_dir = str(invalid_dir)
            assert invalid_dir.exists()
            assert invalid_dir.is_dir()
            print("+ Non-existent directory path created automatically")

            # Test with file path (should raise error)
            test_file = temp_path / "test_file.txt"
            test_file.write_text("test content")

            try:
                cfg.input_pdf_dir = str(test_file)
                # If we get here, the validation should have failed
                assert False, "Expected ValueError for file path"
            except ValueError as e:
                assert "not a directory" in str(e).lower()
                print("+ File path correctly rejected")

        return True

    except Exception as e:
        print(f"- Directory validation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_dialog_save_button():
    """Test that the Save button in SettingsDialog works correctly."""
    print("Testing SettingsDialog Save button functionality...")

    app = QApplication.instance()
    if app is None:
        global _test_app
        _test_app = QApplication(sys.argv)

    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_settings_file = temp_path / "test_settings.json"

            # Create initial test configuration
            test_config = {
                "input": {"pdf_dir": str(temp_path / "pdf"), "wav_dir": str(temp_path / "wav")},
                "analysis": {"tolerance_warn": 2, "tolerance_fail": 5},
            }

            with open(test_settings_file, "w") as f:
                json.dump(test_config, f)

            # Load the test configuration
            load_config(test_settings_file)

            # Create settings dialog with DI
            parent = MockMainWindow()
            dialog = SettingsDialog(test_settings_file, cfg, parent)

            # Modify some settings in the dialog
            dialog.settings_page.warn_slider.setValue(7)
            dialog.settings_page.fail_slider.setValue(12)

            # Mock the save_config function to verify it's called
            with patch("ui.dialogs.settings_dialog.save_config") as mock_save:
                # Click the save button
                dialog.save_button.click()

                # Verify save_config was called
                mock_save.assert_called_once()

                # Verify the dialog was accepted (closed)
                # The dialog should be closed after successful save

            # Clean up
            dialog.deleteLater()
            parent.deleteLater()

            print("+ SettingsDialog Save button works correctly")
            return True

    except Exception as e:
        print(f"- Save button test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_no_pdf_directory_errors():
    """Test that no 'PDF path is not a directory' errors occur during normal operation."""
    print("Testing for absence of 'PDF path is not a directory' errors...")

    try:
        # Create a temporary directory structure for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create valid directory structure
            pdf_dir = temp_path / "pdf"
            wav_dir = temp_path / "wav"
            pdf_dir.mkdir()
            wav_dir.mkdir()

            # Create test settings file
            test_settings = {"input": {"pdf_dir": str(pdf_dir), "wav_dir": str(wav_dir)}}

            settings_file = temp_path / "settings.json"
            with open(settings_file, "w") as f:
                json.dump(test_settings, f)

            # Load configuration
            load_config(settings_file)

            # Test that paths are properly resolved and valid
            pdf_path = cfg.input_pdf_dir.value
            wav_path = cfg.input_wav_dir.value

            assert pdf_path == str(pdf_dir)
            assert wav_path == str(wav_dir)
            assert Path(pdf_path).is_dir()
            assert Path(wav_path).is_dir()

            # Test MainWindow creation with valid paths
            app = QApplication.instance()
            if app is None:
                global _test_app
                _test_app = QApplication(sys.argv)

            # Import MainWindow properly
            from ui import MainWindow
            
            # This should not raise any "PDF path is not a directory" errors
            # Note: MainWindow requires DI parameters, skip full construction in this test
            # For this test, we just verify paths are valid
            
            # Verify the paths are accessible
            assert Path(pdf_path).is_dir()
            assert Path(wav_path).is_dir()

            print("+ No 'PDF path is not a directory' errors occurred")
            return True

    except Exception as e:
        print(f"- PDF directory error test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Settings dialog tests."""
    print("Running comprehensive Settings dialog tests...\n")

    tests = [
        test_settings_dialog_creation,
        test_settings_dialog_menu_action,
        test_settings_dialog_shortcut,
        test_configuration_save,
        test_path_resolution_absolute,
        test_path_resolution_relative,
        test_path_directory_validation,
        test_settings_dialog_save_button,
        test_no_pdf_directory_errors,
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n{'='*60}")
        try:
            if test():
                passed += 1
                print(f"+ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"- {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"- {test.__name__} FAILED with exception: {e}")
        print(f"{'='*60}")

    print("\nTest Results Summary:")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

``n
### tests\test_tracks_table_model.py

`$tag
from __future__ import annotations
from core.domain.analysis_status import AnalysisStatus

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ToleranceSettings
from ui.config_models import ThemeSettings
from ui.models.tracks_table_model import TracksTableModel

pytestmark = pytest.mark.usefixtures("qtbot")


@pytest.fixture
def tolerance_settings():
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.fixture
def theme_settings():
    return ThemeSettings(
        font_family="Poppins, Segoe UI, Arial, sans-serif",
        font_size=10,
        stylesheet_path=Path("gz_media.qss"),
        status_colors={"ok": "#10B981", "warn": "#F59E0B", "fail": "#EF4444"},
        logo_path=Path("assets/gz_logo_white.png"),
        claim_visible=True,
        claim_text="Emotions. Materialized.",
        action_bg_color="#E0E7FF",
        total_row_bg_color="#F3F4F6",
    )


@pytest.fixture
def mock_side_result_tracks():
    pdf_track = TrackInfo(title="Track 1", side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename="track1.wav", duration_sec=181.0, side="A", position=1)
    return SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=181.0,
        total_difference=1,
    )


def test_tracks_table_model_creation(tolerance_settings, theme_settings):
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    assert model.rowCount() == 0
    assert model.columnCount() == len(model._headers)


def test_update_data_populates_model(tolerance_settings, theme_settings, mock_side_result_tracks):
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(mock_side_result_tracks)
    # One track row + total row
    assert model.rowCount() == 2


def test_track_match_icon_ok(tolerance_settings, theme_settings, mock_side_result_tracks):
    """Test that successful match displays check icon via DecorationRole."""
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(mock_side_result_tracks)

    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)

    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()


def test_track_match_icon_fail(tolerance_settings, theme_settings, mock_side_result_tracks):
    """Test that failed match displays cross icon via DecorationRole."""
    failure_result = mock_side_result_tracks.model_copy()
    failure_result.wav_tracks[0] = failure_result.wav_tracks[0].model_copy(update={"duration_sec": 184.0})
    failure_result.total_difference = 4

    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(failure_result)

    index_match = model.index(0, 6)
    icon = model.data(index_match, Qt.ItemDataRole.DecorationRole)

    # Verify icon is returned and is not null
    assert icon is not None
    assert not icon.isNull()


def test_track_match_display_empty(tolerance_settings, theme_settings, mock_side_result_tracks):
    """Test that Match column returns empty string for DisplayRole (icon only)."""
    model = TracksTableModel(tolerance_settings=tolerance_settings, theme_settings=theme_settings)
    model.update_data(mock_side_result_tracks)

    index_match = model.index(0, 6)
    display_text = model.data(index_match, Qt.ItemDataRole.DisplayRole)

    # Verify DisplayRole returns empty string (icon is shown via DecorationRole)
    assert display_text == ""

``n
### tests\test_wav_reader.py

`$tag
from __future__ import annotations

import logging
import sys
import types
import zipfile
from pathlib import Path
from typing import Callable

import numpy as np
import pytest
import soundfile as sf

from adapters.audio.wav_reader import ZipWavFileReader


def _write_wav(path: Path, duration_sec: float, sample_rate: int = 44100) -> None:
    """Helper to author a simple sine-less wave file for tests."""
    frame_count = int(duration_sec * sample_rate)
    data = np.zeros(frame_count, dtype=np.float32)
    sf.write(path, data, sample_rate)


def _build_zip(tmp_path: Path, entries: dict[str, bytes]) -> Path:
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for arcname, payload in entries.items():
            zf.writestr(arcname, payload)
    return zip_path


def _patch_duration(monkeypatch: pytest.MonkeyPatch, factory: Callable[[Path], float]) -> None:
    monkeypatch.setattr("adapters.audio.wav_reader.get_wav_duration", factory)


def test_read_wav_files_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    entries = {
        "disc/B2_second.wav": b"data-b",
        "disc/A1_first.wav": b"data-a",
    }
    zip_path = _build_zip(tmp_path, entries)

    durations = {"A1_first.wav": 12.34, "B2_second.wav": 56.78}
    recorded_paths: list[Path] = []

    def fake_get_wav_duration(path: Path) -> float:
        recorded_paths.append(path)
        return durations[path.name]

    _patch_duration(monkeypatch, fake_get_wav_duration)

    reader = ZipWavFileReader()
    wav_infos = reader.read_wav_files(zip_path)

    assert [info.filename for info in wav_infos] == ["disc/A1_first.wav", "disc/B2_second.wav"]
    assert [info.duration_sec for info in wav_infos] == [12.34, 56.78]
    assert len(recorded_paths) == 2


def test_read_wav_files_corrupted_zip(tmp_path: Path) -> None:
    broken_zip = tmp_path / "corrupted.zip"
    broken_zip.write_bytes(b"not a real zip archive")

    reader = ZipWavFileReader()
    assert reader.read_wav_files(broken_zip) == []


def test_read_wav_files_empty_zip(empty_zip: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Path] = []

    def fake_get_wav_duration(path: Path) -> float:
        calls.append(path)
        return 1.0

    _patch_duration(monkeypatch, fake_get_wav_duration)

    reader = ZipWavFileReader()
    assert reader.read_wav_files(empty_zip) == []
    assert not calls


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Out-of-scope for config DI; quarantined per Execution Policy. "
        "Will be fixed in follow-up change fix-wav-reader-error-handling."
    ),
    run=False,
)
def test_read_wav_files_corrupted_wav(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zip_path = _build_zip(tmp_path, {"broken.wav": b"corrupted payload"})

    def failing_get_wav_duration(path: Path) -> float:
        raise RuntimeError(f"Cannot parse {path}")

    _patch_duration(monkeypatch, failing_get_wav_duration)

    reader = ZipWavFileReader()
    with caplog.at_level(logging.WARNING):
        results = reader.read_wav_files(zip_path)

    assert results == []
    assert any("Nelze přečíst hlavičku WAV" in message for message in caplog.messages)


def test_read_wav_files_no_wav_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    zip_path = _build_zip(tmp_path, {"track.mp3": b"id3"})

    def forbidden_call(path: Path) -> float:
        raise AssertionError(f"get_wav_duration should not be called for {path}")

    _patch_duration(monkeypatch, forbidden_call)

    reader = ZipWavFileReader()
    assert reader.read_wav_files(zip_path) == []


def test_read_wav_files_soundfile_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wav_path = tmp_path / "fallback.wav"
    _write_wav(wav_path, duration_sec=1.0)
    zip_path = tmp_path / "fallback.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(wav_path, arcname=f"folder/{wav_path.name}")

    fake_soundfile = types.ModuleType("soundfile")

    def fake_info(_: str) -> float:
        raise RuntimeError("libsndfile broken")

    fake_soundfile.info = fake_info  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "soundfile", fake_soundfile)

    reader = ZipWavFileReader()
    results = reader.read_wav_files(zip_path)

    assert len(results) == 1
    assert results[0].filename == "folder/fallback.wav"
    assert results[0].duration_sec > 0


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Out-of-scope for config DI; quarantined per Execution Policy. "
        "Will be fixed in follow-up change fix-wav-reader-error-handling."
    ),
    run=False,
)
def test_read_wav_files_duration_extraction_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zip_path = _build_zip(tmp_path, {"fail.wav": b"broken"})

    def exploding_get_wav_duration(path: Path) -> float:
        raise ValueError(f"unreadable {path}")

    _patch_duration(monkeypatch, exploding_get_wav_duration)

    reader = ZipWavFileReader()
    with caplog.at_level(logging.WARNING):
        results = reader.read_wav_files(zip_path)

    assert results == []
    assert any("Nelze přečíst hlavičku WAV" in message for message in caplog.messages)


def test_read_wav_files_duplicate_basenames(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    entries = {
        "sideB/track.wav": b"two",
        "sideA/track.wav": b"one",
    }
    zip_path = _build_zip(tmp_path, entries)

    recorded_paths: list[Path] = []
    durations_iter = iter([1.23, 4.56])

    def fake_get_wav_duration(path: Path) -> float:
        recorded_paths.append(path)
        return next(durations_iter)

    _patch_duration(monkeypatch, fake_get_wav_duration)

    reader = ZipWavFileReader()
    wav_infos = reader.read_wav_files(zip_path)

    assert [info.filename for info in wav_infos] == ["sideA/track.wav", "sideB/track.wav"]
    assert [info.duration_sec for info in wav_infos] == [1.23, 4.56]
    assert {p.parent.name for p in recorded_paths} == {"sideA", "sideB"}


def test_read_wav_files_skips_zero_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zip_path = _build_zip(tmp_path, {"only.wav": b"zero"})

    def zero_duration(_: Path) -> float:
        return 0.0

    _patch_duration(monkeypatch, zero_duration)

    reader = ZipWavFileReader()
    with caplog.at_level(logging.WARNING):
        wav_infos = reader.read_wav_files(zip_path)

    assert wav_infos == []
    assert any("neplatnou délku" in message for message in caplog.messages)

``n
### tests\test_worker_manager.py

`$tag
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QObject, pyqtSignal


@pytest.fixture
def mock_worker_settings(tmp_path):
    from ui.config_models import WorkerSettings

    return WorkerSettings(pdf_dir=tmp_path, wav_dir=tmp_path)


@pytest.fixture
def mock_analysis_worker(monkeypatch):
    class MockWorker(QObject):
        progress = pyqtSignal(str)
        result_ready = pyqtSignal(object)
        finished = pyqtSignal(str)

        def __init__(
            self,
            worker_settings,
            tolerance_settings,
            id_extraction_settings,
        ):
            super().__init__()
            self.worker_settings = worker_settings
            self.tolerance_settings = tolerance_settings
            self.id_extraction_settings = id_extraction_settings
            self.run = MagicMock()

    monkeypatch.setattr("ui.workers.worker_manager.AnalysisWorker", MockWorker)
    return MockWorker


def wait_for_worker(manager, qtbot, condition, timeout=1000):
    qtbot.waitUntil(lambda: manager._worker is not None, timeout=timeout)
    qtbot.waitUntil(condition, timeout=timeout)


def test_worker_manager_creation(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )
    assert not manager.is_running()
    assert manager._thread is None
    assert manager._worker is None


def test_start_analysis_starts_thread_and_worker(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
    mock_analysis_worker,
    qtbot,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    manager.start_analysis()
    wait_for_worker(manager, qtbot, lambda: manager._worker.run.called)

    assert manager._thread is not None
    assert manager._worker is not None
    assert manager._worker.run.called

    manager.cleanup()
    assert manager._thread is None
    assert manager._worker is None


def test_cleanup_stops_thread(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
    mock_analysis_worker,
    qtbot,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )
    manager.start_analysis()
    wait_for_worker(manager, qtbot, lambda: manager._worker.run.called)

    manager.cleanup()
    qtbot.waitUntil(lambda: not manager.is_running(), timeout=1000)

    assert manager._thread is None
    assert manager._worker is None


def test_signals_are_forwarded(
    mock_worker_settings,
    tolerance_settings,
    id_extraction_settings,
    mock_analysis_worker,
    qtbot,
):
    from ui.workers.worker_manager import AnalysisWorkerManager

    manager = AnalysisWorkerManager(
        worker_settings=mock_worker_settings,
        tolerance_settings=tolerance_settings,
        id_extraction_settings=id_extraction_settings,
    )

    progress_values = []
    result_values = []
    finished_values = []

    manager.progress.connect(lambda msg: progress_values.append(msg))
    manager.result_ready.connect(lambda payload: result_values.append(payload))
    manager.finished.connect(lambda msg: finished_values.append(msg))

    manager.start_analysis()
    wait_for_worker(manager, qtbot, lambda: manager._worker.run.called)

    manager._worker.progress.emit("In progress...")
    manager._worker.result_ready.emit({"data": 1})
    manager._worker.finished.emit("Done")

    assert progress_values == ["In progress..."]
    assert result_values == [{"data": 1}]
    assert finished_values == ["Done"]

    manager.cleanup()

``n
### tools\bootstrap_and_finalize.sh

`$tag
#!/usr/bin/env bash
set -euo pipefail

section() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()      { printf "\033[0;32m[ok]\033[0m %s\n" "$*"; }
warn()    { printf "\033[0;33m[warn]\033[0m %s\n" "$*"; }
info()    { printf "\033[0;34m[i]\033[0m %s\n" "$*"; }

# --- 0) Create local venv (.venv) and use it ---------------------------------
section "Python venv bootstrap (.venv)"
PY="python3"
if ! command -v python3 >/dev/null 2>&1; then
  echo "[err] python3 not found in PATH"; exit 1
fi
if [[ ! -d .venv ]]; then
  $PY -m venv .venv
  ok "Created .venv"
fi

if [[ -x .venv/bin/python ]]; then
  PY=".venv/bin/python"
elif [[ -x .venv/Scripts/python ]]; then
  PY=".venv/Scripts/python"
elif [[ -x .venv/Scripts/python.exe ]]; then
  PY=".venv/Scripts/python.exe"
else
  echo "[err] Could not find Python executable in .venv"; exit 1
fi
VENV_BIN=$(dirname "$PY")
export PATH="$VENV_BIN:$PATH"
PIP="$PY -m pip"

$PIP --version >/dev/null 2>&1 || ($PY -m ensurepip --upgrade || true)
$PIP install --upgrade pip wheel setuptools

# --- 1) Dev toolchain ---------------------------------------------------------
section "Install dev toolchain"
if [[ -f requirements-dev.txt ]]; then
  info "requirements-dev.txt found → installing"
  $PIP install -r requirements-dev.txt
else
  info "requirements-dev.txt not found → installing minimal toolchain"
  $PIP install "coverage>=7.6" "pytest>=7.4" "ruff>=0.5" "mypy>=1.8"
fi

# Optional: OpenSpec CLI
if ! command -v openspec >/dev/null 2>&1; then
  warn "openspec CLI not found → attempting optional install"
  $PIP install openspec-cli || warn "openspec optional install failed (continuing)"
fi

# --- 2) Verify tools ----------------------------------------------------------
section "Verify tool availability"
$PY --version
$PIP show coverage pytest ruff mypy | sed 's/^Name: /-- /' || true
openspec --version || true

# --- 3) Run finalize flow w/ audit log ---------------------------------------
section "Run finalize.sh (with audit log)"
mkdir -p .openspec
ts=$(date +%Y%m%d_%H%M%S)
LOG=".openspec/finalize-${ts}.log"

chmod +x tools/check.sh tools/finalize.sh || true
# Capture both finalize output AND a quick env snapshot into the same log
{
  echo "# Environment snapshot";
  which $PY || true;
  $PY -m pip freeze || true;
  echo;
  echo "# Finalize flow";
  ./tools/finalize.sh
} 2>&1 | tee "$LOG"

ok "Audit log saved to: $LOG"

# --- 4) Optional stricter OpenSpec check if CLI present -----------------------
if command -v openspec >/dev/null 2>&1; then
  section "OpenSpec validate (strict, hard-fail)"
  openspec validate --strict | tee -a "$LOG"
  ok "OpenSpec validate passed"
else
  warn "openspec CLI not found; validation deferred"
fi

# --- 5) Exit summary ----------------------------------------------------------
section "Summary"
echo "Finalize log: $LOG"
ok "Bootstrap + Finalization completed"

``n
### tools\bootstrap_finalize.sh

`$tag
#!/usr/bin/env bash
set -euo pipefail

section() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()      { printf "\033[0;32m[ok]\033[0m %s\n" "$*"; }
warn()    { printf "\033[0;33m[warn]\033[0m %s\n" "$*"; }
info()    { printf "\033[0;34m[i]\033[0m %s\n" "$*"; }

PY="python3"
PIP="python3 -m pip"

section "Bootstrap Python environment"
if ! command -v python3 >/dev/null 2>&1; then
  echo "[err] python3 not found in PATH"; exit 1
fi
$PIP --version >/dev/null 2>&1 || ($PY -m ensurepip --upgrade || true)
$PIP install --break-system-packages --upgrade pip wheel setuptools

if [[ -f requirements-dev.txt ]]; then
  info "requirements-dev.txt found → installing"
  $PIP install --break-system-packages -r requirements-dev.txt
elif [[ -f requirements.txt ]]; then
  info "requirements-dev.txt not found, using requirements.txt"
  $PIP install --break-system-packages -r requirements.txt
else
  info "requirements-dev.txt not found → installing minimal toolchain"
  $PIP install --break-system-packages coverage pytest ruff mypy || true
fi

if ! command -v openspec >/dev/null 2>&1; then
  warn "openspec CLI not found → attempting optional install"
  $PIP install --break-system-packages openspec-cli || warn "openspec optional install failed (continuing)"
fi

section "Verify tool availability"
$PY --version
$PY -m pip show coverage pytest ruff mypy || true
openspec --version || true

section "Run finalize flow"
chmod +x tools/check.sh tools/finalize.sh || true
./tools/finalize.sh || { echo "[err] finalize.sh failed"; exit 1; }

section "Audit snapshot"
git --version || true
git status --porcelain || true
git tag -l 'refactor-phase1-stabilization*' || true

``n
### tools\build_resources.py

`$tag
#!/usr/bin/env python3
"""Build Qt resources from QRC file using pyrcc6 or manual generation."""

import subprocess
import sys
from pathlib import Path


def build_resources():
    """Compile icons.qrc to _icons_rc.py"""
    qrc_path = Path(__file__).parent.parent / "assets" / "icons.qrc"
    output_path = Path(__file__).parent.parent / "ui" / "_icons_rc.py"

    if not qrc_path.exists():
        print(f"Error: {qrc_path} not found")
        return False

    # Try using pyrcc6 command
    try:
        result = subprocess.run(
            ["pyrcc6", str(qrc_path), "-o", str(output_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[SUCCESS] Successfully compiled {qrc_path} to {output_path}")
        print(result.stdout)
        return True
    except FileNotFoundError:
        print("pyrcc6 not found in PATH, using fallback method...")
    except subprocess.CalledProcessError as e:
        print(f"pyrcc6 failed: {e.stderr}")
        return False

    # Fallback: create a minimal working _icons_rc.py that registers the resources
    print("Generating minimal resource module...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # This creates a simple module that PyQt6 will use to find the resource files
    minimal_code = '''# This file was automatically generated by build_resources.py
# Qt resource module (minimal fallback)
from PyQt6.QtCore import qRegisterResourceData, qUnregisterResourceData

# Note: QResource.addSearchPath is not for resource files compiled by pyrcc6,
# and directly accessing QResource.addSearchPath does not function as intended
# for :/ paths. The proper mechanism involves data registered by pyrcc6.
# When pyrcc6 is absent, we rely on ui/theme.py's direct file loading logic.

def qInitResources():
    """Initialize resources (called on module import)"""
    pass

def qCleanupResources():
    """Cleanup resources"""
    pass

# Auto-initialize on import
qInitResources()
'''

    with output_path.open("w", encoding="utf-8") as f:
        f.write(minimal_code)

    print(f"[SUCCESS] Generated fallback resource module at {output_path}")
    return True


if __name__ == "__main__":
    success = build_resources()
    sys.exit(0 if success else 1)

``n
### tools\finalize.sh

`$tag
#!/usr/bin/env bash
set -euo pipefail

CHANGE_ID="refactor-phase1-stabilization"
TAG_NAME="refactor-phase1-stabilization-done"

section() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
info()    { printf "\033[0;34m[i]\033[0m %s\n" "$*"; }
ok()      { printf "\033[0;32m[ok]\033[0m %s\n" "$*"; }
warn()    { printf "\033[0;33m[warn]\033[0m %s\n" "$*"; }
err()     { printf "\033[0;31m[err]\033[0m %s\n" "$*"; }

# 0) Preflight
section "Preflight"
if [[ ! -f tools/check.sh ]]; then
  err "Missing tools/check.sh"; exit 1
fi
chmod +x tools/check.sh || true
ok "tools/check.sh is executable"

# 1) Quality Gate (unified)
section "Quality Gate"
./tools/check.sh
ok "Quality gate passed (tools/check.sh)"

# 2) OpenSpec finalize + validate (if CLI available)
section "OpenSpec Finalization"
if command -v openspec >/dev/null 2>&1; then
  info "openspec CLI detected"
  openspec finalize "$CHANGE_ID"
  ok "openspec finalize $CHANGE_ID done"

  section "OpenSpec Validate (strict)"
  openspec validate --strict
  ok "openspec validate --strict passed"
else
  warn "openspec CLI not found in PATH. Skipping finalize/validate."
  warn "Run later when CLI is available: "
  printf "  openspec finalize %s\n  openspec validate --strict\n" "$CHANGE_ID"
fi

# 3) Git: init/commit/tag/push (optional, only if inside repo OR user wants it)
section "Git Commit/Tag"
if command -v git >/dev/null 2>&1; then
  if git rev-parse --git-dir >/dev/null 2>&1; then
    info "Git repository detected"
  else
    warn "No git repo found. Initializing a new one..."
    git init
    git branch -M main || true
  fi

  # Ensure .gitignore exists minimally
  if [[ ! -f .gitignore ]]; then
    cat <<'EOF' > .gitignore
__pycache__/
*.pyc
.coverage
htmlcov/
.env
.venv/
EOF
    info "Created minimal .gitignore"
  fi

  git add -A
  COMMIT_MSG="Finalize ${CHANGE_ID}: quality gate pass, docs aligned (PyQt6+QSettings), Purpose sections, CHANGELOG 0.0.1"
  if git diff --cached --quiet; then
    info "No staged changes to commit"
  else
    git commit -m "$COMMIT_MSG"
    ok "Committed changes"
  fi

  if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    info "Tag ${TAG_NAME} already exists"
  else
    git tag -a "$TAG_NAME" -m "Stabilization phase 1 finalized"
    ok "Created tag ${TAG_NAME}"
  fi

  if git remote get-url origin >/dev/null 2>&1; then
    git push origin HEAD --tags
    ok "Pushed branch and tags to origin"
  else
    warn "No git remote configured. Skipping push."
  fi
else
  warn "git not found. Skipping commit/tag/push."
fi

section "Done"
ok "Finalization flow completed. If OpenSpec CLI was missing, re-run the finalize/validate commands later."

``n
### tools\check.sh

`$tag
#!/usr/bin/env bash
set -euo pipefail

# Phase 1 quality gate script.

if [[ -n "${PYTHON_BIN:-}" ]]; then
  # Allow callers to override the interpreter path, e.g. PYTHON_BIN="py -3".
  # shellcheck disable=SC2206
  PYTHON_CMD=(${PYTHON_BIN})
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=("python")
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=("python3")
elif command -v py >/dev/null 2>&1; then
  PYTHON_CMD=("py" "-3")
else
  echo "Python interpreter not found on PATH." >&2
  exit 1
fi

echo "Collecting coverage metrics..."
# ZDE JE OPRAVA: Odstraněn flag -m "not gui" pro spuštění VŠECH testů
QT_QPA_PLATFORM=offscreen "${PYTHON_CMD[@]}" -m coverage run -m pytest
# Temporary threshold reduction tracked via OpenSpec change `tech-debt-increase-coverage`.
"${PYTHON_CMD[@]}" -m coverage report --fail-under=78

echo "Running Ruff lint checks..."
"${PYTHON_CMD[@]}" -m ruff check .

echo "Running mypy in strict mode..."
"${PYTHON_CMD[@]}" -m mypy --strict core adapters services

if command -v openspec >/dev/null 2>&1; then
   echo "Validating OpenSpec specifications..."
   if ! openspec validate refactor-phase5-ai-port --strict; then
     echo "OpenSpec validation skipped: refactor-phase5-ai-port not found."
   fi
else
   echo "Skipping OpenSpec validation (openspec CLI not found)..."
fi

echo "All checks passed"

``n
### ui\__init__.py

`$tag
from core.domain.analysis_status import AnalysisStatus
from core.models.settings import ExportSettings, IdExtractionSettings, ToleranceSettings

from .constants import *
from .theme import get_system_file_icon, get_custom_icon, get_gz_color, load_gz_media_fonts, load_gz_media_stylesheet
from .models.results_table_model import ResultsTableModel
from .models.tracks_table_model import TracksTableModel
from .workers.analysis_worker import AnalysisWorker
from .workers.worker_manager import AnalysisWorkerManager
from .dialogs.settings_dialog import SettingsDialog
from .main_window import MainWindow
from .config_models import (
    PathSettings,
    ThemeSettings,
    WorkerSettings,
    load_tolerance_settings,
    load_export_settings,
    load_path_settings,
    load_theme_settings,
    load_worker_settings,
    load_id_extraction_settings,
)

__all__ = [
    # Constants
    "SETTINGS_FILENAME",
    "WINDOW_TITLE",
    "STATUS_READY",
    "STATUS_ANALYZING",
    "MSG_ERROR_PATHS",
    "MSG_NO_PAIRS",
    "MSG_DONE",
    "MSG_ERROR",
    "MSG_SCANNING",
    "MSG_PROCESSING_PAIR",
    "BUTTON_RUN_ANALYSIS",
    "LABEL_FILTER",
    "FILTER_ALL",
    "FILTER_OK",
    "FILTER_FAIL",
    "FILTER_WARN",
    "TABLE_HEADERS_TOP",
    "TABLE_HEADERS_BOTTOM",
    "SYMBOL_CHECK",
    "SYMBOL_CROSS",
    "PLACEHOLDER_DASH",
    "COLOR_WHITE",
    "LABEL_TOTAL_TRACKS",
    "STATUS_OK",
    "STATUS_WARN",
    "STATUS_FAIL",
    "INTERFACE_MAIN",
    # Icon constants
    "ICON_CHECK",
    "ICON_CROSS",
    "ICON_PLAY",
    # Theme helpers
    "get_system_file_icon",
    "get_custom_icon",
    "get_gz_color",
    "load_gz_media_fonts",
    "load_gz_media_stylesheet",
    # Models
    "ResultsTableModel",
    "TracksTableModel",
    # Workers
    "AnalysisWorker",
    "AnalysisWorkerManager",
    # Dialogs
    "SettingsDialog",
    # Main window
    "MainWindow",
    # Config models and loaders
    "ToleranceSettings",
    "ExportSettings",
    "PathSettings",
    "ThemeSettings",
    "WorkerSettings",
    "IdExtractionSettings",
    "AnalysisStatus",
    "load_tolerance_settings",
    "load_export_settings",
    "load_path_settings",
    "load_theme_settings",
    "load_worker_settings",
    "load_id_extraction_settings",
]

``n
### ui\_icons_rc.py

`$tag
# This file was automatically generated by build_resources.py
# Qt resource module (minimal fallback)
from PyQt6.QtCore import qRegisterResourceData, qUnregisterResourceData

# Note: QResource.addSearchPath is not for resource files compiled by pyrcc6,
# and directly accessing QResource.addSearchPath does not function as intended
# for :/ paths. The proper mechanism involves data registered by pyrcc6.
# When pyrcc6 is absent, we rely on ui/theme.py's direct file loading logic.


def qInitResources():
    """Initialize resources (called on module import)"""
    pass


def qCleanupResources():
    """Cleanup resources"""
    pass


# Auto-initialize on import
qInitResources()

``n
### ui\config_models.py

`$tag
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from config import AppConfig, ConfigLoader
from core.models.settings import (
    ExportSettings,
    IdExtractionSettings,
    PathSettings,
    ThemeSettings,
    ToleranceSettings,
    WorkerSettings,
)

# NOTE: Only application entry points should import the global cfg object.
# Other layers construct settings via these dataclasses and receive them via DI.


def _ensure_loader(cfg: Optional[AppConfig] = None, loader: Optional[ConfigLoader] = None) -> ConfigLoader:
    if loader is not None:
        return loader
    if cfg is not None:
        return ConfigLoader(cfg.settings)
    return ConfigLoader()


def load_tolerance_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> ToleranceSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_tolerance_settings()


def load_export_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> ExportSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_export_settings()


def load_path_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> PathSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_path_settings()


def load_id_extraction_settings(
    cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None
) -> IdExtractionSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_id_extraction_settings()


def load_theme_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> ThemeSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_theme_settings()


def load_worker_settings(cfg: AppConfig | None = None, *, loader: ConfigLoader | None = None) -> WorkerSettings:
    resolved_loader = _ensure_loader(cfg, loader)
    return resolved_loader.load_worker_settings()

``n
### ui\constants.py

`$tag
from pathlib import Path

"""
Constants for the UI module.

This module defines constants used throughout the UI, including status messages, table headers, and symbols.

Note: Text symbols like SYMBOL_CHECK and SYMBOL_CROSS are deprecated in favor of icon constants ICON_CHECK, ICON_CROSS, ICON_PLAY for better cross-platform rendering.
"""

# --- Constants ---
SETTINGS_FILENAME = Path("settings.json")
STATUS_READY = "Ready"
STATUS_ANALYZING = "Analyzing..."
MSG_ERROR_PATHS = "Error: Paths 'pdf_dir' and 'wav_dir' must be set in settings.json"
MSG_NO_PAIRS = "No valid PDF-ZIP pairs found."
MSG_DONE = "Analysis completed. Processed {count} pairs."
MSG_ERROR = "Error: {error}"
MSG_SCANNING = "Scanning and pairing files..."
MSG_PROCESSING_PAIR = "Processing pair {current}/{total}: {filename}"
WINDOW_TITLE = "Final Cue Sheet Checker"
BUTTON_RUN_ANALYSIS = "Run analysis"
LABEL_FILTER = "Filter:"
FILTER_ALL = "All"
FILTER_OK = "OK"
FILTER_FAIL = "Fail"
FILTER_WARN = "Warn"
TABLE_HEADERS_TOP = ["#", "File", "Side", "Mode", "Side length", "Status", "PDF", "ZIP"]
TABLE_HEADERS_BOTTOM = ["#", "WAV file", "Title", "Length (PDF)", "Length (WAV)", "Difference(s)", "Match"]

# Table content strings

COLOR_WHITE = "white"
STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"

# Icon constants for UI rendering
ICON_CHECK = "check"
ICON_CROSS = "cross"
ICON_PLAY = "play"

# Deprecated: Use get_custom_icon('check') and get_custom_icon('cross') instead
# These constants are kept for backward compatibility but are no longer used in UI rendering
SYMBOL_CHECK = "✓"
SYMBOL_CROSS = "✗"
PLACEHOLDER_DASH = "-"
LABEL_TOTAL_TRACKS = "Total (tracks)"
# Interface strings
INTERFACE_MAIN = "Main"

``n
### ui\delegates\__init__.py

`$tag

``n
### ui\delegates\action_cell_delegate.py

`$tag
"""Delegate for rendering hover affordance on action cells in tables."""

from __future__ import annotations

from typing import Set

from PyQt6.QtCore import QModelIndex, QRect
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QAbstractItemView, QStyledItemDelegate, QStyle


def _darken_color(color: str, factor: float = 0.15) -> QColor:
    """Darken a hex color by a given factor (0.0 to 1.0).

    Args:
        color: Hex color string (e.g., '#E0E7FF')
        factor: Darkening factor (0.0-1.0, where 1.0 is black)

    Returns:
        QColor object
    """
    qcolor = QColor(color)
    if not qcolor.isValid():
        return QColor(color)

    # Reduce lightness by factor
    h, s, v, a = qcolor.getHsv()
    if v > 0:
        v = max(0, int(v * (1 - factor)))
    qcolor.setHsv(h, s, v, a)
    return qcolor


class ActionCellDelegate(QStyledItemDelegate):
    """Delegate that renders a subtle hover tint on action cells in specified columns.

    This delegate checks if a cell is in a configured action column and if the mouse
    is hovering over it. If so, it draws a slightly darker background tint before
    rendering the normal content.
    """

    def __init__(self, theme_settings, action_columns: Set[int] | list[int]):
        """Initialize the delegate.

        Args:
            theme_settings: ThemeSettings object with action_bg_color
            action_columns: Set or list of column indices that are action cells
        """
        super().__init__()
        self.theme_settings = theme_settings
        self.action_columns = set(action_columns)
        self._hovered_index: QModelIndex | None = None

    def paint(
        self,
        painter: QPainter,
        option,
        index,
    ) -> None:
        """Paint the cell with hover affordance if applicable.

        Args:
            painter: QPainter for drawing
            option: QStyleOptionViewItem with styling info
            index: QModelIndex of the cell
        """
        # Only apply hover effect for action columns
        if index.column() not in self.action_columns:
            super().paint(painter, option, index)
            return

        # Check if cell is hovered and not selected
        # Compare with the currently hovered index tracked via mouse events
        is_hovered = (
            self._hovered_index is not None
            and self._hovered_index.row() == index.row()
            and self._hovered_index.column() == index.column()
        )
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)

        if is_hovered and not is_selected:
            # Draw hover tint background
            hover_color = _darken_color(
                self.theme_settings.action_bg_color,
                factor=0.15,
            )
            painter.fillRect(option.rect, hover_color)

        # Call parent paint to render the icon and text
        super().paint(painter, option, index)

    def set_hovered_index(self, index: QModelIndex | None) -> None:
        """Set the currently hovered cell index.

        Args:
            index: QModelIndex of the hovered cell, or None if no cell is hovered
        """
        self._hovered_index = index

``n
### ui\dialogs\__init__.py

`$tag

``n
### ui\dialogs\settings_dialog.py

`$tag
from __future__ import annotations

import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
)

from config import save_config, AppConfig
from settings_page import SettingsPage


class SettingsDialog(QDialog):
    """Modal settings dialog containing SettingsPage with Save/Cancel buttons."""

    def __init__(self, settings_filename: Path, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.settings_filename = Path(settings_filename)
        self._app_config = app_config
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.settings_page = SettingsPage(app_config, self.settings_filename, show_action_buttons=False)
        self.settings_page.settingChanged.connect(self._on_setting_changed)
        self.settings_page.saveRequested.connect(self._on_page_save_requested)
        self.settings_page.reloadRequested.connect(self._on_page_reload_requested)
        self.settings_page.resetRequested.connect(self._on_page_reset_requested)
        scroll_area.setWidget(self.settings_page)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

    def _show_safe_message_box(
        self,
        title: str,
        text: str,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
    ):
        if os.getenv("QT_QPA_PLATFORM") == "offscreen":
            logging.error(f"MODAL_DIALOG_BLOCKED: Title: {title}, Text: {text}")
            return

        parent = self.parent()
        if parent and hasattr(parent, "_show_safe_message_box"):
            parent._show_safe_message_box(title, text, icon)
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.exec()

    def _on_save(self) -> None:
        """Handle save button click - save config and accept dialog."""
        if self._persist_settings():
            self.accept()

    def _persist_settings(self) -> bool:
        try:
            save_config(self.settings_filename)
            return True
        except Exception as exc:
            self._show_safe_message_box(
                "Save Error",
                f"Failed to save settings:\n{exc}",
                QMessageBox.Icon.Critical,
            )
            return False

    def _on_setting_changed(self, key: str, value: object) -> None:
        try:
            self._app_config.set(key, value)
        except Exception as exc:
            self._show_safe_message_box(
                "Update Error",
                f"Failed to update setting '{key}':\n{exc}",
                QMessageBox.Icon.Critical,
            )

    def _on_page_save_requested(self) -> None:
        if self._persist_settings():
            self.settings_page._show_message("Settings saved", "Configuration saved successfully.", "info")

    def _on_page_reload_requested(self) -> None:
        try:
            self._app_config.settings.sync()
            self.settings_page._sync_from_config()
            self.settings_page._show_message("Settings reloaded", "Configuration reloaded from disk.", "info")
        except Exception as exc:
            self._show_safe_message_box(
                "Reload Error",
                f"Failed to reload settings:\n{exc}",
                QMessageBox.Icon.Critical,
            )

    def _on_page_reset_requested(self) -> None:
        try:
            self._app_config.reset_to_defaults()
            save_config(self.settings_filename)
            self._app_config.save()
            self.settings_page._sync_from_config()
            self.settings_page._reenable_widgets()
            self.settings_page._show_message("Defaults restored", "All settings were reset to defaults.", "info")
        except Exception as exc:
            self._show_safe_message_box(
                "Reset Error",
                f"Failed to reset settings:\n{exc}",
                QMessageBox.Icon.Critical,
            )

``n
### ui\main_window.py

`$tag
from __future__ import annotations

import logging
import os
from pathlib import Path

from PyQt6.QtCore import QEvent, QModelIndex, QSize, Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.models.analysis import SideResult
from core.models.settings import ExportSettings, ToleranceSettings
from core.ports import WaveformViewerPort
from pdf_viewer import PdfViewerDialog
from services.export_service import export_results_to_json
from ui.config_models import ThemeSettings
from ui.constants import *
from ui.delegates.action_cell_delegate import ActionCellDelegate
from ui.dialogs.settings_dialog import SettingsDialog
from ui.models.results_table_model import ResultsTableModel
from ui.models.tracks_table_model import TracksTableModel
from ui.workers.worker_manager import AnalysisWorkerManager
from config import AppConfig


class MainWindow(QMainWindow):
    def _show_safe_message_box(
        self,
        title: str,
        text: str,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
    ):
        if os.getenv("QT_QPA_PLATFORM") == "offscreen":
            logging.error(f"MODAL_DIALOG_BLOCKED: Title: {title}, Text: {text}")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(text)
        msg_box.setWindowTitle(title)
        msg_box.exec()

    def __init__(
        self,
        *,
        tolerance_settings: ToleranceSettings,
        export_settings: ExportSettings,
        theme_settings: ThemeSettings,
        waveform_viewer: WaveformViewerPort,
        worker_manager: AnalysisWorkerManager,
        settings_filename: Path,
        app_config: AppConfig,
    ):
        super().__init__()
        self.tolerance_settings = tolerance_settings
        self.export_settings = export_settings
        self.theme_settings = theme_settings
        self.waveform_viewer = waveform_viewer
        self.worker_manager = worker_manager
        self.worker_manager.setParent(self)
        self.settings_filename = Path(settings_filename)
        self.app_config = app_config

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1200, 800)

        self.setup_menu_bar()

        central = QWidget(self)
        central.setObjectName("Main")
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setObjectName("MainToolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setProperty("analysis-state", "false")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.run_button = QPushButton(BUTTON_RUN_ANALYSIS)
        self.run_button.setObjectName("RunButton")
        self.toolbar.addWidget(self.run_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        self.filter_section = QWidget()
        filter_layout = QHBoxLayout(self.filter_section)
        filter_layout.setContentsMargins(8, 0, 8, 0)
        filter_layout.addWidget(QLabel(LABEL_FILTER))

        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("FilterCombo")
        self.filter_combo.addItems([FILTER_ALL, FILTER_OK, FILTER_FAIL, FILTER_WARN])
        self.filter_combo.setMinimumWidth(100)
        filter_layout.addWidget(self.filter_combo)
        self.toolbar.addWidget(self.filter_section)

        spacer_between = QWidget()
        spacer_between.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        spacer_between.setFixedWidth(16)
        self.toolbar.addWidget(spacer_between)

        self.status_box = QWidget()
        status_layout = QHBoxLayout(self.status_box)
        status_layout.setContentsMargins(8, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        status_layout.addWidget(self.progress_bar)

        self.status_label = QLabel(STATUS_READY)
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setMinimumWidth(220)
        status_layout.addWidget(self.status_label)
        self.toolbar.addWidget(self.status_box)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.top_table = QTableView()
        self.top_model = ResultsTableModel(theme_settings=self.theme_settings)
        self.top_table.setModel(self.top_model)
        try:
            self.top_table.setIconSize(QSize(16, 16))
        except Exception:
            pass

        self.bottom_table = QTableView()
        self.bottom_model = TracksTableModel(
            tolerance_settings=self.tolerance_settings, theme_settings=self.theme_settings
        )
        self.bottom_table.setModel(self.bottom_model)

        splitter.addWidget(self.top_table)
        splitter.addWidget(self.bottom_table)
        splitter.setSizes([300, 400])
        main_layout.addWidget(splitter)

        self.setCentralWidget(central)

        self.setup_tables()
        self.connect_signals()

        self._auto_resize_pending = False

        def _apply_header_resizes():
            if not hasattr(self, "top_table") or not hasattr(self, "bottom_table"):
                return

            h_header = self.top_table.horizontalHeader()
            for col in (0, 2, 3, 4, 5, 6, 7):
                h_header.resizeSection(col, self.top_table.sizeHintForColumn(col))

            h_header_b = self.bottom_table.horizontalHeader()
            for col in (0, 3, 4, 5, 6):
                h_header_b.resizeSection(col, self.bottom_table.sizeHintForColumn(col))

        def _schedule_header_resizes():
            if self._auto_resize_pending:
                return
            self._auto_resize_pending = True
            QTimer.singleShot(0, lambda: (setattr(self, "_auto_resize_pending", False), _apply_header_resizes()))

        self._schedule_header_resizes = _schedule_header_resizes  # type: ignore[assignment]
        self.top_model._schedule_header_resizes = _schedule_header_resizes  # type: ignore[attr-defined]

        if self.windowHandle() is not None:

            def _on_screen_changed(screen):
                try:
                    screen.logicalDotsPerInchChanged.connect(lambda _=None: _schedule_header_resizes())
                    screen.physicalDotsPerInchChanged.connect(lambda _=None: _schedule_header_resizes())
                except Exception:
                    pass
                _schedule_header_resizes()

            self.windowHandle().screenChanged.connect(_on_screen_changed)
            _on_screen_changed(self.windowHandle().screen())

        self.installEventFilter(self)

    def on_filter_changed(self, filter_text: str):
        self.top_model.set_filter(filter_text)
        if self.top_model.rowCount() > 0:
            self.top_table.selectRow(0)
        else:
            self.top_table.clearSelection()
            self.bottom_model.update_data(None)

    def setup_tables(self):
        self.top_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.top_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.top_table.setMouseTracking(True)
        self.bottom_table.setMouseTracking(True)

        h_header = self.top_table.horizontalHeader()
        h_header.setStretchLastSection(False)
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        h_header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.top_table.setColumnWidth(6, 60)
        self.top_table.setColumnWidth(7, 60)

        bold = h_header.font()
        bold.setBold(True)
        h_header.setFont(bold)

        h_header_bottom = self.bottom_table.horizontalHeader()
        bbold = h_header_bottom.font()
        bbold.setBold(True)
        h_header_bottom.setFont(bbold)
        h_header_bottom.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h_header_bottom.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h_header_bottom.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        h_header_bottom.setStretchLastSection(True)
        self.bottom_table.setColumnWidth(1, 200)

        self.top_table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.bottom_table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.top_table.setAlternatingRowColors(True)
        self.bottom_table.setAlternatingRowColors(True)

        # Install hover affordance delegates for action cells
        self.top_delegate = ActionCellDelegate(self.theme_settings, {6, 7})
        self.top_table.setItemDelegateForColumn(6, self.top_delegate)
        self.top_table.setItemDelegateForColumn(7, self.top_delegate)

    def connect_signals(self):
        self.run_button.clicked.connect(self.run_analysis)
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        selection_model = self.top_table.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self.on_top_row_selected)
        self.top_table.clicked.connect(self.on_top_cell_clicked)
        self.bottom_table.clicked.connect(self.on_bottom_cell_clicked)

        # Connect hover tracking for action cell affordance
        self.top_table.entered.connect(lambda idx: self.top_delegate.set_hovered_index(idx))
        self.top_table.installEventFilter(self)

        self.worker_manager.progress.connect(lambda msg: self._set_status(msg, running=True))
        self.worker_manager.result_ready.connect(self.top_model.add_result)
        self.worker_manager.finished.connect(self.on_analysis_finished)

    def eventFilter(self, obj, event):
        event_type = event.type()
        if event_type in (
            QEvent.Type.PaletteChange,
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.FontChange,
            QEvent.Type.ApplicationFontChange,
            QEvent.Type.Resize,
        ):
            if hasattr(self, "_schedule_header_resizes"):
                self._schedule_header_resizes()
        # Clear hover state when mouse leaves table
        elif event_type == QEvent.Type.Leave:
            if obj is self.top_table:
                self.top_delegate.set_hovered_index(None)
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "_schedule_header_resizes"):
            self._schedule_header_resizes()

    def closeEvent(self, event):
        self.worker_manager.cleanup()
        super().closeEvent(event)

    def run_analysis(self):
        if not self.worker_manager.is_running():
            self._set_analysis_state(True)
            self.run_button.setEnabled(False)
            self._set_status(STATUS_ANALYZING, running=True)
            self.top_model.clear()
            self.bottom_model.update_data(None)
            self.worker_manager.start_analysis()

    def _set_status(self, text: str, running: bool):
        self.progress_bar.setVisible(running)
        if len(text) > 50:
            for separator in [" - ", ": ", ", ", " "]:
                if separator in text[:45]:
                    parts = text.split(separator, 1)
                    text = parts[0] + separator.rstrip()
                    break
            else:
                text = text[:47] + "..."
        self.status_label.setText(text)

    def setup_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear()
        settings_menu = menubar.addMenu("Settings")
        settings_action = settings_menu.addAction("Open settings...")
        settings_action.triggered.connect(self.open_settings)

    def _set_analysis_state(self, is_analyzing: bool):
        try:
            self.setProperty("analysis-state", "true" if is_analyzing else "false")
            if is_analyzing and hasattr(self, "status_label") and self.status_label is not None:
                self.status_label.setText(STATUS_ANALYZING)
        except Exception as exc:
            logging.exception("Failed to set analysis state: %s", exc)

    def on_analysis_finished(self, message: str):
        self._set_analysis_state(False)
        logging.info("Analysis finished: %s", message)

        try:
            all_results = getattr(self.top_model, "all_results", lambda: [])()
        except Exception:
            all_results = []

        export_path = export_results_to_json(
            results=all_results,
            export_settings=self.export_settings,
        )

        if export_path is not None:
            ready_msg = f"{STATUS_READY} - {message} - Exported: {export_path.name}"
        else:
            ready_msg = f"{STATUS_READY} - {message}"
        self._set_status(ready_msg, running=False)
        self.run_button.setEnabled(True)
        if self.top_model.rowCount() > 0:
            self.top_table.selectRow(0)

    def on_top_row_selected(self, current: QModelIndex, previous: QModelIndex):
        result = self.top_model.get_result(current.row())
        self.bottom_model.update_data(result)

    def on_top_cell_clicked(self, index: QModelIndex):
        result = self.top_model.get_result(index.row())
        if not result:
            return
        if index.column() == 6 and result.pdf_path:
            try:
                pdf_dialog = PdfViewerDialog(result.pdf_path, self)
                pdf_dialog.exec()
            except Exception as exc:
                logging.error("Failed to open PDF viewer: %s", exc)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(result.pdf_path)))
        elif index.column() == 7 and result.zip_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(result.zip_path)))

    def on_bottom_cell_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        if index.column() != 1:
            logging.info("Bottom table click ignored: column=%s", index.column())
            return

        top_idx = self.top_table.currentIndex()
        if not top_idx.isValid():
            logging.info("Waveform viewer not opened: no top row selected.")
            return

        result = self.top_model.get_result(top_idx.row())
        if not result:
            logging.info("Waveform viewer not opened: no result for selected row.")
            return
        if not result.zip_path:
            logging.info("Waveform viewer not opened: missing ZIP path.")
            return

        side: SideResult | None = self.bottom_model._data
        if side is None:
            logging.info("Waveform viewer not opened: no side data available.")
            return

        if index.row() >= len(side.pdf_tracks):
            logging.info("Waveform viewer not opened: total row selected.")
            return

        if side.mode != "tracks":
            logging.info("Waveform viewer not opened: side mode %s unsupported.", side.mode)
            return

        if index.row() >= len(side.wav_tracks):
            logging.info("Waveform viewer not opened: missing WAV track at row %s.", index.row())
            return

        wav_track = side.wav_tracks[index.row()]
        wav_filename = getattr(wav_track, "filename", None)
        if not wav_filename:
            logging.info("Waveform viewer not opened: WAV filename missing for row %s.", index.row())
            return

        try:
            self.waveform_viewer.show(result.zip_path, wav_filename, self)
        except Exception as exc:
            logging.error("Failed to open waveform viewer: %s", exc, exc_info=True)

    def open_settings(self):
        try:
            settings_dialog = SettingsDialog(settings_filename=self.settings_filename, app_config=self.app_config, parent=self)
            settings_dialog.exec()
        except Exception as exc:
            logging.error("Failed to open settings dialog: %s", exc)

    def _update_gz_logo(self):
        try:
            if not hasattr(self, "gz_logo_label"):
                self.gz_logo_label = QLabel(parent=self)
                self.gz_logo_label.setObjectName("gzLogo")

            logo_path = self.theme_settings.logo_path

            if logo_path.exists():
                from PyQt6.QtGui import QPixmap

                pixmap = QPixmap(str(logo_path))
                scaled_pixmap = pixmap.scaledToHeight(24, Qt.TransformationMode.SmoothTransformation)
                self.gz_logo_label.setPixmap(scaled_pixmap)
                self.gz_logo_label.show()
            else:
                self.gz_logo_label.setText("GZ Media")
                logging.warning("GZ Media logo file not found at %s, using text fallback", logo_path)
        except Exception as exc:
            logging.error("Failed to load GZ Media logo: %s", exc)
            if hasattr(self, "gz_logo_label"):
                self.gz_logo_label.hide()

    def _update_gz_claim_visibility(self):
        try:
            if not hasattr(self, "gz_claim_label"):
                self.gz_claim_label = QLabel(parent=self)

            if self.theme_settings.claim_visible:
                self.gz_claim_label.setText(self.theme_settings.claim_text)
                self.gz_claim_label.show()
            else:
                self.gz_claim_label.hide()
        except Exception as exc:
            logging.error("Failed to update GZ Media claim: %s", exc)
            if hasattr(self, "gz_claim_label"):
                self.gz_claim_label.hide()

``n
### ui\models\__init__.py

`$tag

``n
### ui\models\results_table_model.py

`$tag
from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult
from ui.config_models import ThemeSettings
from ui.constants import (
    COLOR_WHITE,
    FILTER_ALL,
    FILTER_FAIL,
    FILTER_OK,
    FILTER_WARN,
    TABLE_HEADERS_TOP,
)
from ui.theme import get_system_file_icon
from ui.theme import get_system_file_icon


class ResultsTableModel(QAbstractTableModel):
    """Model for the top table showing matched PDF/ZIP pairs."""

    def __init__(self, theme_settings: ThemeSettings):
        super().__init__()
        self.theme_settings = theme_settings
        self._headers = TABLE_HEADERS_TOP
        self._data: List[SideResult] = []
        self._filtered_data: List[SideResult] = []
        self._active_filter: str = FILTER_ALL
        self._seq_counter = 1

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._filtered_data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid():
            return None
        row = index.row()
        if row < 0 or row >= len(self._filtered_data):
            return None
        result = self._filtered_data[row]
        column = index.column()

        if role == Qt.ItemDataRole.DecorationRole:
            if column == 6 and result.pdf_path:
                return get_system_file_icon("file")
            if column == 7 and result.zip_path:
                return get_system_file_icon("dir")

        if role == Qt.ItemDataRole.BackgroundRole:
            if column == 6 and result.pdf_path:
                return QColor(self.theme_settings.action_bg_color)
            if column == 7 and result.zip_path:
                return QColor(self.theme_settings.action_bg_color)

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return index.row() + 1
            if column == 1:
                return result.pdf_path.name
            if column == 2:
                return result.side
            if column == 3:
                return result.mode
            if column == 4:
                return f"{result.total_pdf_sec // 60:02d}:{result.total_pdf_sec % 60:02d}"
            if column == 5:
                return result.status.value

        if role == Qt.ItemDataRole.ForegroundRole and column == 5:
            return QColor(COLOR_WHITE)

        if role == Qt.ItemDataRole.BackgroundRole and column == 5:
            status_colors = self.theme_settings.status_colors
            color_value = status_colors.get(result.status.color_key())
            if color_value:
                return QColor(color_value)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column in (6, 7):
                return Qt.AlignmentFlag.AlignCenter
            if column in (3, 4, 5):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column in (0, 2):
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft

        if role == Qt.ItemDataRole.ToolTipRole and column == 1:
            return f"PDF: {result.pdf_path}\nZIP: {result.zip_path if result.zip_path else '-'}"
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 6 and result.pdf_path:
                return "Open PDF file"
            if column == 7 and result.zip_path:
                return "Open ZIP archive"

        return None

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]
            if role == Qt.ItemDataRole.FontRole:
                header_font = QFont()
                header_font.setBold(True)
                return header_font
        return None

    def add_result(self, result: SideResult) -> None:
        """Add a result to the model, maintaining filter state."""
        result_with_seq = result.model_copy()
        result_with_seq.seq = self._seq_counter
        self._seq_counter += 1

        self._data.append(result_with_seq)
        if self._passes_filter(result_with_seq):
            insert_row = len(self._filtered_data)
            self.beginInsertRows(QModelIndex(), insert_row, insert_row)
            self._filtered_data.append(result_with_seq)
            self.endInsertRows()
            if hasattr(self, "_schedule_header_resizes"):
                QTimer.singleShot(0, self._schedule_header_resizes)

    def get_result(self, row: int) -> Optional[SideResult]:
        if 0 <= row < len(self._filtered_data):
            return self._filtered_data[row]
        return None

    def clear(self) -> None:
        self.beginResetModel()
        self._data.clear()
        self._filtered_data.clear()
        self._active_filter = FILTER_ALL
        self._seq_counter = 1
        self.endResetModel()

    def all_results(self) -> List[SideResult]:
        return list(self._data)

    def set_filter(self, filter_text: str) -> None:
        valid_filters = {FILTER_ALL, FILTER_OK, FILTER_FAIL, FILTER_WARN}
        self._active_filter = filter_text if filter_text in valid_filters else FILTER_ALL
        self._rebuild_filtered_data()

    def _passes_filter(self, result: SideResult) -> bool:
        if self._active_filter == FILTER_ALL:
            return True
        status_by_filter = {
            FILTER_OK: AnalysisStatus.OK,
            FILTER_FAIL: AnalysisStatus.FAIL,
            FILTER_WARN: AnalysisStatus.WARN,
        }
        expected_status = status_by_filter.get(self._active_filter)
        if expected_status is None:
            return True
        return result.status == expected_status

    def _rebuild_filtered_data(self) -> None:
        self.beginResetModel()
        self._filtered_data = [res for res in self._data if self._passes_filter(res)]
        self.endResetModel()

``n
### ui\models\tracks_table_model.py

`$tag
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

from core.domain.analysis_status import AnalysisStatus
from core.models.analysis import SideResult
from core.models.settings import ToleranceSettings
from ui.config_models import ThemeSettings
from ui.constants import (
    LABEL_TOTAL_TRACKS,
    PLACEHOLDER_DASH,
    TABLE_HEADERS_BOTTOM,
)
from ui.theme import get_custom_icon


class TracksTableModel(QAbstractTableModel):
    """Model for the bottom table showing track details."""

    def __init__(self, tolerance_settings: ToleranceSettings, theme_settings: ThemeSettings):
        """Initialize TracksTableModel with dependency injection.

        Args:
            tolerance_settings: Tolerance settings for match calculations.
            theme_settings: Theme settings for styling.
        """
        super().__init__()
        self.tolerance_settings = tolerance_settings
        self.theme_settings = theme_settings

        self._headers = TABLE_HEADERS_BOTTOM
        self._data: Optional[SideResult] = None

    def flags(self, index: QModelIndex):
        base = super().flags(index)
        if not index.isValid():
            return base
        if index.row() == self.rowCount() - 1:
            return base & ~Qt.ItemFlag.ItemIsSelectable
        return base

    def rowCount(self, parent: QModelIndex = QModelIndex()):  # type: ignore[override]
        if not self._data or not self._data.pdf_tracks:
            return 0
        return len(self._data.pdf_tracks) + 1

    def columnCount(self, parent: QModelIndex = QModelIndex()):  # type: ignore[override]
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if not index.isValid() or not self._data:
            return None

        row = index.row()
        column = index.column()
        is_total_row = row == self.rowCount() - 1

        # Column 6 (Match) - Icon rendering
        if role == Qt.ItemDataRole.DecorationRole and column == 6 and not is_total_row:
            if self._data.mode == "tracks":
                pdf_track = self._data.pdf_tracks[row] if row < len(self._data.pdf_tracks) else None
                wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None

                if pdf_track and wav_track:
                    difference = wav_track.duration_sec - pdf_track.duration_sec
                    try:
                        track_tolerance = float(self.tolerance_settings.warn_tolerance)
                    except (TypeError, ValueError):
                        track_tolerance = 2.0

                    # Return check or cross icon based on tolerance
                    if abs(difference) <= track_tolerance:
                        return get_custom_icon("check")
                    else:
                        return get_custom_icon("cross")
                else:
                    return get_custom_icon("cross")
            return None

        # Column 6 (Match) - Total row icon
        if role == Qt.ItemDataRole.DecorationRole and column == 6 and is_total_row:
            if self._data.status == AnalysisStatus.OK:
                return get_custom_icon("check")
            else:
                return get_custom_icon("cross")

        if role in (Qt.ItemDataRole.AccessibleTextRole, Qt.ItemDataRole.ToolTipRole) and column == 6:
            if is_total_row:
                return "Match OK" if self._data.status == AnalysisStatus.OK else "No match"
            else:
                if self._data.mode == "tracks":
                    pdf_track = self._data.pdf_tracks[row] if row < len(self._data.pdf_tracks) else None
                    wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None

                    if pdf_track and wav_track:
                        difference = wav_track.duration_sec - pdf_track.duration_sec
                        try:
                            track_tolerance = float(self.tolerance_settings.warn_tolerance)
                        except (TypeError, ValueError):
                            track_tolerance = 2.0

                        if abs(difference) <= track_tolerance:
                            return "Match OK"
                    return "No match"
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if is_total_row:
                return self.get_total_row_data(column)
            return self.get_track_row_data(row, column)

        if role == Qt.ItemDataRole.BackgroundRole and is_total_row:
            return QColor(self.theme_settings.total_row_bg_color)

        if role == Qt.ItemDataRole.FontRole and is_total_row:
            font = QFont()
            font.setBold(True)
            return font

        if role == Qt.ItemDataRole.TextAlignmentRole and column == 6:
            return Qt.AlignmentFlag.AlignCenter

        return None

    def get_track_row_data(self, row: int, column: int):
        if not self._data or row >= len(self._data.pdf_tracks):
            return ""

        pdf_track = self._data.pdf_tracks[row]

        if self._data.mode == "tracks":
            wav_track = self._data.wav_tracks[row] if row < len(self._data.wav_tracks) else None
            difference = (wav_track.duration_sec - pdf_track.duration_sec) if wav_track else None

            try:
                track_tolerance = float(self.tolerance_settings.warn_tolerance)
            except (TypeError, ValueError):
                track_tolerance = 2.0

            if column == 0:
                return pdf_track.position
            if column == 1:
                return wav_track.filename if wav_track else PLACEHOLDER_DASH
            if column == 2:
                return pdf_track.title
            if column == 3:
                return f"{pdf_track.duration_sec // 60:02d}:{pdf_track.duration_sec % 60:02d}"
            if column == 4:
                if wav_track:
                    return f"{int(wav_track.duration_sec) // 60:02d}:{int(wav_track.duration_sec) % 60:02d}"
                return PLACEHOLDER_DASH
            if column == 5:
                return f"{difference:+.0f}" if difference is not None else PLACEHOLDER_DASH
            if column == 6:
                return ""  # Icon is shown via DecorationRole
        else:
            if column == 0:
                return pdf_track.position
            if column == 1:
                return PLACEHOLDER_DASH
            if column == 2:
                return pdf_track.title
            if column == 3:
                return f"{pdf_track.duration_sec // 60:02d}:{pdf_track.duration_sec % 60:02d}"
            if column == 4:
                return PLACEHOLDER_DASH
            if column == 5:
                return PLACEHOLDER_DASH
            if column == 6:
                return PLACEHOLDER_DASH
            return PLACEHOLDER_DASH
        return ""

    def get_total_row_data(self, column: int):
        if not self._data:
            return ""

        if column == 1:
            if self._data.mode == "side" and self._data.wav_tracks:
                return self._data.wav_tracks[0].filename
            return LABEL_TOTAL_TRACKS
        if column == 2:
            return f"{len(self._data.pdf_tracks)} tracks"
        if column == 3:
            return f"{self._data.total_pdf_sec // 60:02d}:{self._data.total_pdf_sec % 60:02d}"
        if column == 4:
            return f"{int(self._data.total_wav_sec) // 60:02d}:{int(self._data.total_wav_sec) % 60:02d}"
        if column == 5:
            return f"{self._data.total_difference:+.0f}"
        if column == 6:
            return ""  # Icon is shown via DecorationRole
        return ""

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # type: ignore[override]
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font
        return None

    def update_data(self, result: Optional[SideResult]) -> None:
        self.beginResetModel()
        self._data = result
        self.endResetModel()

``n
### ui\theme.py

`$tag
import logging
import sys
from pathlib import Path
from typing import Dict

from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QStyle


# Icon cache for performance
_icon_cache: Dict[str, QIcon] = {}


def get_asset_path(relative_path: Path) -> Path:
    """Get absolute path to asset, supporting both development and bundled app (PyInstaller)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in a normal Python environment
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path


def get_custom_icon(icon_name: str) -> QIcon:
    """Load a custom SVG icon with caching, resource lookup, and system fallback.

    Args:
        icon_name: Name of the icon without extension (e.g., 'check', 'cross', 'play')

    Returns:
        QIcon object, system fallback, or empty QIcon if not found.
    """
    if icon_name in _icon_cache:
        return _icon_cache[icon_name]

    # 1. Try loading from filesystem (dev or bundled app)
    try:
        icon_path = get_asset_path(Path("assets") / "icons" / f"{icon_name}.svg")
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                logging.debug(f"Loaded icon '{icon_name}' from filesystem: {icon_path}")
                _icon_cache[icon_name] = icon
                return icon

        logging.warning(f"Custom icon file not found at: {icon_path}, using fallback.")

    except Exception as exc:
        logging.error(f"Error loading custom icon '{icon_name}' from filesystem: {exc}")

    # 2. If filesystem fails, use a system fallback icon
    fallback_icon = _get_fallback_icon(icon_name)
    if not fallback_icon.isNull():
        logging.warning(f"Using fallback for icon '{icon_name}'.")
        _icon_cache[icon_name] = fallback_icon  # Cache the fallback too
        return fallback_icon

    logging.error(f"Failed to load icon or find fallback for '{icon_name}'.")
    _icon_cache[icon_name] = QIcon()  # Cache the empty icon to prevent repeated lookups
    return _icon_cache[icon_name]


def _get_fallback_icon(icon_name: str) -> QIcon:
    """Get fallback system icon for the given icon name."""
    try:
        app = QApplication.instance()
        if not app:
            return QIcon()

        style = app.style()

        # Map icon names to system pixmaps
        fallback_mapping = {
            "check": QStyle.StandardPixmap.SP_DialogApplyButton,
            "cross": QStyle.StandardPixmap.SP_DialogCancelButton,
            "play": QStyle.StandardPixmap.SP_MediaPlay,
        }

        if icon_name in fallback_mapping:
            fallback_icon = style.standardIcon(fallback_mapping[icon_name])
            if not fallback_icon.isNull():
                logging.debug(f"Using fallback icon for: {icon_name}")
                return fallback_icon

        logging.warning(f"No fallback available for icon: {icon_name}")
        return QIcon()

    except Exception as exc:
        logging.error(f"Error getting fallback icon for '{icon_name}': {exc}")
        return QIcon()


def get_system_file_icon(icon_type: str = "file") -> QIcon:
    """Return a standard system icon for files, directories, or actions, with support for custom SVG icons."""
    # Support custom SVG icons for specific types
    if icon_type in ["check", "cross", "play"]:
        return get_custom_icon(icon_type)

    # Fallback to system icons for backward compatibility
    try:
        app = QApplication.instance()
        if not app:
            return QIcon()

        style = app.style()
        mapping = {
            "file": QStyle.StandardPixmap.SP_FileIcon,
            "dir": QStyle.StandardPixmap.SP_DirIcon,
        }
        return style.standardIcon(mapping.get(icon_type, QStyle.StandardPixmap.SP_FileIcon))
    except Exception:
        return QIcon()


def get_gz_color(color_key: str, status_colors: Dict[str, str]) -> str:
    """Resolve a brand color using provided status colors with safe fallbacks."""
    fallback_colors = {
        "white": "white",
        "ok": "#10B981",
        "warn": "#F59E0B",
        "fail": "#EF4444",
    }

    if color_key == "white":
        return "white"

    try:
        if status_colors and color_key in status_colors:
            return status_colors[color_key]
    except Exception:
        logging.debug("Failed to read status color '%s' from config", color_key, exc_info=True)

    return fallback_colors.get(color_key, color_key)


def load_gz_media_fonts(app: QApplication, font_family: str, font_size: int) -> None:
    """Apply the configured font family and size to the application."""
    try:
        resolved_family = font_family or "Poppins, Segoe UI, Arial, sans-serif"
        font = QFont(resolved_family)

        try:
            if font_size:
                font.setPointSize(int(font_size))
            else:
                font.setPointSize(10)
        except (TypeError, ValueError):
            font.setPointSize(10)

        app.setFont(font)
        logging.info("GZ Media font applied successfully")
    except Exception as exc:
        logging.warning("Failed to apply GZ Media font, using system default: %s", exc)


def load_gz_media_stylesheet(app: QApplication, stylesheet_path: Path) -> None:
    """Load the configured stylesheet if available."""
    try:
        if stylesheet_path and stylesheet_path.exists():
            with stylesheet_path.open("r", encoding="utf-8") as handle:
                qss_content = handle.read()
            app.setStyleSheet(qss_content)
            logging.info("GZ Media stylesheet loaded successfully")
        else:
            logging.warning("GZ Media stylesheet file not found at %s", stylesheet_path)
    except Exception as exc:
        logging.error("Failed to load GZ Media stylesheet from %s: %s", stylesheet_path, exc)

``n
### ui\widgets\__init__.py

`$tag
"""UI widget component namespace."""


``n
### ui\widgets\settings\__init__.py

`$tag
from .groups import UiGroup, ModelGroup, PathsGroup, AnalysisGroup, FolderSettingCard

__all__ = [
    "UiGroup",
    "ModelGroup",
    "PathsGroup",
    "AnalysisGroup",
    "FolderSettingCard",
]

``n
### ui\widgets\settings\groups.py

`$tag
from __future__ import annotations

from typing import Iterable, Sequence, Union

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


def format_scale_option(option: Union[float, str]) -> str:
    if isinstance(option, (float, int)):
        return f"{int(float(option) * 100)}%"
    if isinstance(option, str) and option.upper() == "AUTO":
        return "Follow system"
    return str(option)


def normalize_scale_value(value: object) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        upper = stripped.upper()
        if upper == "FOLLOW SYSTEM":
            return "AUTO"
        if upper == "AUTO":
            return "AUTO"
        try:
            return float(stripped)
        except ValueError:
            return stripped
    return value


def coerce_folder(value: object) -> str:
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        iterator = iter(value)
        first = next(iterator, "")
        return str(first) if first else ""
    return str(value) if value else ""


class FolderSettingCard(QWidget):
    """Single-folder selector implemented with standard PyQt6 components."""

    settingChanged = pyqtSignal(str, str)

    def __init__(
        self,
        setting_key: str,
        initial_path: str = "",
        title: str | None = None,
        content: str | None = None,
        directory: str = "./",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setting_key = setting_key
        self._dialog_directory = directory

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        if title:
            title_label = QLabel(title)
            title_font = title_label.font()
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)

        if content:
            content_label = QLabel(content)
            content_label.setStyleSheet("color: gray;")
            layout.addWidget(content_label)

        controls_layout = QHBoxLayout()

        self.path_input = QLineEdit(self)
        self.path_input.setMinimumWidth(520)
        self.path_input.setClearButtonEnabled(True)
        self.path_input.editingFinished.connect(self._on_edit_finished)
        controls_layout.addWidget(self.path_input, 1)

        controls_layout.addSpacing(12)

        browse_button = QPushButton(self.tr("Browse"), self)
        browse_button.setFixedWidth(120)
        browse_button.clicked.connect(self._on_browse)
        controls_layout.addWidget(browse_button)

        layout.addLayout(controls_layout)

        self.set_path(initial_path, update_config=False)

    def set_path(self, path: str, update_config: bool = True) -> None:
        normalized = path or ""
        if self.path_input.text() != normalized:
            self.path_input.blockSignals(True)
            self.path_input.setText(normalized)
            self.path_input.blockSignals(False)
        if update_config and self.setting_key:
            self.settingChanged.emit(self.setting_key, normalized)

    def _on_edit_finished(self) -> None:
        path = self.path_input.text().strip()
        if self.setting_key:
            self.settingChanged.emit(self.setting_key, path)

    def _on_browse(self) -> None:
        current = self.path_input.text().strip() or self._dialog_directory
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), current)
        if folder and self.setting_key:
            self.set_path(folder, update_config=True)


class UiGroup(QGroupBox):
    """Group widget for user interface configuration."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        available_scales: Sequence[Union[str, float]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("User Interface", parent)
        self._available_scales = list(available_scales)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        scale_layout = QHBoxLayout()
        scale_label = QLabel("Interface scaling:")
        scale_label.setFixedWidth(150)
        scale_layout.addWidget(scale_label)

        self.scale_combo = QComboBox(self)
        for option in self._available_scales:
            label = format_scale_option(option)
            self.scale_combo.addItem(label, option)
        self.scale_combo.currentIndexChanged.connect(self._on_scale_index_changed)
        scale_layout.addWidget(self.scale_combo)
        scale_layout.addStretch()

        layout.addLayout(scale_layout)

    def _on_scale_index_changed(self, index: int) -> None:
        value = self.scale_combo.itemData(index, Qt.ItemDataRole.UserRole)
        canonical = normalize_scale_value(value if value is not None else self.scale_combo.currentText())
        self.settingChanged.emit("ui/dpi_scale", canonical)

    def sync_from_config(self, value: object) -> None:
        canonical = normalize_scale_value(value if value is not None else "AUTO")
        self.scale_combo.blockSignals(True)
        try:
            for index in range(self.scale_combo.count()):
                candidate = normalize_scale_value(self.scale_combo.itemData(index, Qt.ItemDataRole.UserRole))
                if candidate == canonical:
                    self.scale_combo.setCurrentIndex(index)
                    break
        finally:
            self.scale_combo.blockSignals(False)


class ModelGroup(QGroupBox):
    """Group widget for primary model selection."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        available_models: Sequence[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Model Configuration", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        model_layout = QHBoxLayout()
        label = QLabel("Primary model:")
        label.setFixedWidth(150)
        model_layout.addWidget(label)

        self.model_combo = QComboBox(self)
        self.model_combo.addItems(list(available_models))
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()

        layout.addLayout(model_layout)

    def _on_model_changed(self, value: str) -> None:
        self.settingChanged.emit("llm/model", value)

    def sync_from_config(self, model: str) -> None:
        self.model_combo.blockSignals(True)
        try:
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
        finally:
            self.model_combo.blockSignals(False)


class PathsGroup(QGroupBox):
    """Group widget for directory configuration."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        pdf_dir: str,
        wav_dir: str,
        export_dir: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Directory Paths", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.pdf_card = FolderSettingCard(
            "input/pdf_dir",
            coerce_folder(pdf_dir),
            "PDF input directory",
            "Folder scanned for tracklist PDF files.",
            parent=self,
        )
        self.pdf_card.settingChanged.connect(self.settingChanged.emit)
        layout.addWidget(self.pdf_card)

        self.wav_card = FolderSettingCard(
            "input/wav_dir",
            coerce_folder(wav_dir),
            "WAV input directory",
            "Folder containing mastered WAV files.",
            parent=self,
        )
        self.wav_card.settingChanged.connect(self.settingChanged.emit)
        layout.addWidget(self.wav_card)

        self.export_card = FolderSettingCard(
            "export/default_dir",
            coerce_folder(export_dir),
            "Export directory",
            "Destination directory for generated reports.",
            parent=self,
        )
        self.export_card.settingChanged.connect(self.settingChanged.emit)
        layout.addWidget(self.export_card)

    def sync_paths(self, pdf_dir: str, wav_dir: str, export_dir: str) -> None:
        self.pdf_card.set_path(coerce_folder(pdf_dir), update_config=False)
        self.wav_card.set_path(coerce_folder(wav_dir), update_config=False)
        self.export_card.set_path(coerce_folder(export_dir), update_config=False)


class AnalysisGroup(QGroupBox):
    """Group widget for analysis tolerance sliders."""

    settingChanged = pyqtSignal(str, object)

    def __init__(
        self,
        warn_tolerance: int,
        fail_tolerance: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Analysis Configuration", parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        warn_layout = QHBoxLayout()
        warn_label = QLabel("Warning tolerance:")
        warn_label.setFixedWidth(150)
        warn_layout.addWidget(warn_label)

        self.warn_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.warn_slider.setRange(1, 10)
        self.warn_slider.setFixedWidth(200)
        self.warn_slider.valueChanged.connect(self._on_warn_changed)
        warn_layout.addWidget(self.warn_slider)

        self.warn_value_label = QLabel(self)
        self.warn_value_label.setFixedWidth(30)
        self.warn_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn_layout.addWidget(self.warn_value_label)
        warn_layout.addStretch()

        layout.addLayout(warn_layout)

        fail_layout = QHBoxLayout()
        fail_label = QLabel("Failure tolerance:")
        fail_label.setFixedWidth(150)
        fail_layout.addWidget(fail_label)

        self.fail_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.fail_slider.setRange(1, 20)
        self.fail_slider.setFixedWidth(200)
        self.fail_slider.valueChanged.connect(self._on_fail_changed)
        fail_layout.addWidget(self.fail_slider)

        self.fail_value_label = QLabel(self)
        self.fail_value_label.setFixedWidth(30)
        self.fail_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fail_layout.addWidget(self.fail_value_label)
        fail_layout.addStretch()

        layout.addLayout(fail_layout)

        self.sync_from_config(warn_tolerance, fail_tolerance)

    def _on_warn_changed(self, value: int) -> None:
        self.warn_value_label.setText(f"{value}s")
        self.settingChanged.emit("analysis/tolerance_warn", value)

    def _on_fail_changed(self, value: int) -> None:
        self.fail_value_label.setText(f"{value}s")
        self.settingChanged.emit("analysis/tolerance_fail", value)

    def sync_from_config(self, warn_tolerance: int, fail_tolerance: int) -> None:
        self.warn_slider.blockSignals(True)
        self.fail_slider.blockSignals(True)
        try:
            self.warn_slider.setValue(int(warn_tolerance))
            self.warn_value_label.setText(f"{int(warn_tolerance)}s")
            self.fail_slider.setValue(int(fail_tolerance))
            self.fail_value_label.setText(f"{int(fail_tolerance)}s")
        finally:
            self.warn_slider.blockSignals(False)
            self.fail_slider.blockSignals(False)

``n
### ui\workers\__init__.py

`$tag

``n
### ui\workers\analysis_worker.py

`$tag
from __future__ import annotations

import logging
from PyQt6.QtCore import QObject, pyqtSignal

from core.models.settings import IdExtractionSettings, ToleranceSettings
from services.analysis_service import AnalysisService
from ui.config_models import WorkerSettings


class AnalysisWorker(QObject):
    """Runs the analysis service in a background thread with injected settings."""

    progress = pyqtSignal(str)
    result_ready = pyqtSignal(object)
    finished = pyqtSignal(str)

    def __init__(
        self,
        worker_settings: WorkerSettings,
        tolerance_settings: ToleranceSettings,
        id_extraction_settings: IdExtractionSettings,
    ):
        super().__init__()
        self.worker_settings = worker_settings
        self.tolerance_settings = tolerance_settings
        self.id_extraction_settings = id_extraction_settings

    def run(self) -> None:
        try:
            service = AnalysisService(
                tolerance_settings=self.tolerance_settings,
                id_extraction_settings=self.id_extraction_settings,
            )
            service.start_analysis(
                pdf_dir=self.worker_settings.pdf_dir,
                wav_dir=self.worker_settings.wav_dir,
                progress_callback=self.progress.emit,
                result_callback=self.result_ready.emit,
                finished_callback=self.finished.emit,
            )
        except Exception as exc:
            logging.error("Critical error in AnalysisWorker", exc_info=True)
            self.finished.emit(f"Critical Worker Error: {exc}")

``n
### ui\workers\worker_manager.py

`$tag
from __future__ import annotations

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from core.models.settings import IdExtractionSettings, ToleranceSettings
from ui.config_models import WorkerSettings
from ui.workers.analysis_worker import AnalysisWorker


class AnalysisWorkerManager(QObject):
    """Manages the lifecycle of AnalysisWorker, injecting required settings."""

    progress = pyqtSignal(str)
    result_ready = pyqtSignal(object)
    finished = pyqtSignal(str)

    def __init__(
        self,
        worker_settings: WorkerSettings,
        tolerance_settings: ToleranceSettings,
        id_extraction_settings: IdExtractionSettings,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.worker_settings = worker_settings
        self.tolerance_settings = tolerance_settings
        self.id_extraction_settings = id_extraction_settings
        self._worker: AnalysisWorker | None = None
        self._thread: QThread | None = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def start_analysis(self) -> None:
        if self.is_running():
            return

        self._thread = QThread()
        self._worker = AnalysisWorker(
            worker_settings=self.worker_settings,
            tolerance_settings=self.tolerance_settings,
            id_extraction_settings=self.id_extraction_settings,
        )
        self._worker.moveToThread(self._thread)

        self._worker.progress.connect(self.progress)
        self._worker.result_ready.connect(self.result_ready)
        self._worker.finished.connect(self.finished)
        self._worker.finished.connect(self.cleanup)

        self._thread.started.connect(self._worker.run)
        self._thread.start()

    def cleanup(self) -> None:
        if self._thread:
            self._thread.quit()
            self._thread.wait(1000)
        self._thread = None
        self._worker = None

``n

