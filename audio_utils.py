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
