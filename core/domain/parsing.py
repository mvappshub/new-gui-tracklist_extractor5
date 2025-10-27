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

        Examples:
            >>> parser = StrictFilenameParser()
            >>> parser.parse("Side_A_01.wav")
            ParsedFileInfo(side='A', position=1)
            >>> parser.parse("mixdown-final.wav")
            ParsedFileInfo(side=None, position=None)
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

        Examples:
            >>> parser = TracklistParser()
            >>> parser.parse([{"title": "Song", "side": "A", "position": 1, "duration_formatted": "03:15"}])
            [TrackInfo(title='Song', side='A', position=1, duration_sec=195)]
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
