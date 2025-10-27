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
