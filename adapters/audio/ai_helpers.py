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
