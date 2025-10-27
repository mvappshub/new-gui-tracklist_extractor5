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
