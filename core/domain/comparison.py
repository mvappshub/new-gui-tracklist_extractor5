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
        if abs(difference) >= tolerance_fail:
            status = AnalysisStatus.FAIL
        elif abs(difference) >= tolerance_warn:
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
