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
