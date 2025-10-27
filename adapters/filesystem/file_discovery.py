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
