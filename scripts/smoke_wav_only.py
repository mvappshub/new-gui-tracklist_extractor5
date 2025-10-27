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
