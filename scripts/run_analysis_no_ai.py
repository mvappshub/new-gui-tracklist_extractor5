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
