#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from PyQt6.QtCore import Qt

from ui.models.results_table_model import ResultsTableModel
from ui.models.tracks_table_model import TracksTableModel
from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.domain.analysis_status import AnalysisStatus
from core.domain.parsing import TracklistParser

pytestmark = pytest.mark.gui


@pytest.fixture
def unicode_theme_settings():
    """Basic theme settings for Unicode tests."""
    from core.models.settings import ThemeSettings
    return ThemeSettings(
        status_colors={"ok": "#10B981", "warn": "#F59E0B", "fail": "#EF4444"},
        action_bg_color="#E0E7FF",
        total_row_bg_color="#F3F4F6",
    )


@pytest.fixture
def tolerance_settings():
    """Tolerance settings for tracks table."""
    from core.models.settings import ToleranceSettings
    return ToleranceSettings(warn_tolerance=2, fail_tolerance=5)


@pytest.mark.gui
def test_unicode_diacritics_in_pdf_filename(unicode_theme_settings):
    """
    Scenario: Diacritics in PDF filename
    GIVEN a SideResult with pdf_path containing diacritics
    WHEN added to ResultsTableModel
    THEN DisplayRole for column 1 returns the filename with diacritics intact
    AND no replacement characters () appear
    """
    # GIVEN
    pdf_path = Path("Tracklist_Café_Müller.pdf")
    result = SideResult(
        seq=1,
        pdf_path=pdf_path,
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[],
        wav_tracks=[],
        total_pdf_sec=100,
        total_wav_sec=100.0,
        total_difference=0,
    )

    # WHEN added to model
    model = ResultsTableModel(unicode_theme_settings)
    model.add_result(result)

    # THEN DisplayRole returns intact filename
    index = model.index(0, 1)  # File column
    display_text = model.data(index, Qt.ItemDataRole.DisplayRole)

    assert display_text == "Tracklist_Café_Müller.pdf"
    assert "Café" in display_text
    assert "Müller" in display_text
    assert "\uFFFD" not in display_text  # No replacement characters


@pytest.mark.gui
def test_unicode_emoji_in_track_title(tolerance_settings, unicode_theme_settings):
    """
    Scenario: Emoji in track title
    GIVEN a TrackInfo with title containing emoji
    WHEN displayed in TracksTableModel
    THEN DisplayRole returns the title with emoji intact
    AND rendering doesn't crash
    """
    # GIVEN
    emoji_title = "🎵 Summer Vibes 🌊"
    pdf_track = TrackInfo(title=emoji_title, side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename="track1.wav", duration_sec=180.0, side="A", position=1)

    result = SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=180.0,
        total_difference=0,
    )

    # WHEN displayed in model
    model = TracksTableModel(tolerance_settings, unicode_theme_settings)
    model.update_data(result)

    # THEN emoji are preserved
    index = model.index(0, 2)  # Title column
    display_text = model.data(index, Qt.ItemDataRole.DisplayRole)

    assert display_text == emoji_title
    assert "🎵" in display_text
    assert "🌊" in display_text


@pytest.mark.gui
def test_unicode_mixed_in_wav_filename(tolerance_settings, unicode_theme_settings):
    """
    Scenario: Mixed Unicode in WAV filename
    GIVEN a WavInfo with filename containing mixed Unicode
    WHEN displayed in TracksTableModel
    THEN DisplayRole returns the filename correctly
    """
    # GIVEN
    mixed_unicode_filename = "Track_01_Naïve_Café☕.wav"
    pdf_track = TrackInfo(title="Test Track", side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename=mixed_unicode_filename, duration_sec=180.0, side="A", position=1)

    result = SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=180.0,
        total_difference=0,
    )

    # WHEN displayed in model
    model = TracksTableModel(tolerance_settings, unicode_theme_settings)
    model.update_data(result)

    # THEN filename is preserved intact
    index = model.index(0, 1)  # WAV filename column
    display_text = model.data(index, Qt.ItemDataRole.DisplayRole)

    assert display_text == mixed_unicode_filename
    assert "Naïve" in display_text
    assert "Café" in display_text
    assert "☕" in display_text
    assert "\uFFFD" not in display_text


def test_unicode_round_trip_through_parser():
    """
    Scenario: Unicode round-trip through parser
    GIVEN raw track data with Unicode
    WHEN parsed by TracklistParser
    THEN the resulting TrackInfo.title preserves Unicode characters
    """
    # GIVEN
    raw_track_data = {
        'title': 'Café Müller',
        'side': 'A',
        'position': 1,
        'duration_formatted': '03:45'
    }

    # WHEN parsed
    parser = TracklistParser()
    track_info = parser.parse_single_track(raw_track_data)

    # THEN Unicode is preserved
    assert track_info.title == 'Café Müller'
    assert "Café" in track_info.title
    assert "Müller" in track_info.title
    assert track_info.duration_sec == 225  # 3:45 = 225 seconds


@pytest.mark.gui
def test_unicode_in_tooltips(unicode_theme_settings):
    """
    Scenario: Unicode in tooltips
    GIVEN a result with Unicode filename
    WHEN ToolTipRole is requested
    THEN tooltip text contains Unicode without corruption
    """
    # GIVEN
    unicode_filename = "Playlist_Été_2023.pdf"
    result = SideResult(
        seq=1,
        pdf_path=Path(unicode_filename),
        zip_path=Path("archive.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[],
        wav_tracks=[],
        total_pdf_sec=100,
        total_wav_sec=100.0,
        total_difference=0,
    )

    # WHEN tooltip requested
    model = ResultsTableModel(unicode_theme_settings)
    model.add_result(result)

    index = model.index(0, 1)  # File column where tooltip shows PDF path
    tooltip_text = model.data(index, Qt.ItemDataRole.ToolTipRole)

    # THEN Unicode preserved in tooltip
    assert tooltip_text is not None
    assert "Playlist_Été_2023.pdf" in tooltip_text
    assert "Été" in tooltip_text
    assert "\uFFFD" not in tooltip_text


@pytest.mark.parametrize("unicode_text", [
    "",  # Empty string
    "a",  # Single character
    "🚀🌟💫🎯🎪🎨🎭🖼️🏺⚱️",  # Many emoji
    "e\u0301",  # Combining acute accent (é as e + combining character)
    "Zürich München naïve résumé",  # Various diacritics
])
@pytest.mark.gui
def test_unicode_edge_cases_in_filenames(unicode_theme_settings, unicode_text):
    """
    Test Unicode edge cases in filenames and track data.
    """
    # GIVEN filename with various Unicode edge cases
    if unicode_text:  # Skip empty for filename
        filename = f"test_{unicode_text}.pdf"
        pdf_path = Path(filename)
    else:
        pdf_path = Path("test.pdf")

    result = SideResult(
        seq=1,
        pdf_path=pdf_path,
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[],
        wav_tracks=[],
        total_pdf_sec=100,
        total_wav_sec=100.0,
        total_difference=0,
    )

    # WHEN displayed
    model = ResultsTableModel(unicode_theme_settings)
    model.add_result(result)

    # THEN no crashes and Unicode preserved
    index = model.index(0, 1)
    display_text = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert isinstance(display_text, str)  # No exceptions thrown
    assert "\uFFFD" not in display_text  # No corruption


@pytest.mark.parametrize("unicode_title", [
    "",  # Empty title
    "🚀",  # Single emoji
    "Zürich & München - naïve résumé of été 🎵🎶🎵",  # Complex Unicode mix
])
@pytest.mark.gui
def test_unicode_edge_cases_in_track_titles(tolerance_settings, unicode_theme_settings, unicode_title):
    """
    Test Unicode edge cases in track titles.
    """
    # GIVEN
    pdf_track = TrackInfo(title=unicode_title, side="A", position=1, duration_sec=180)
    wav_track = WavInfo(filename="track1.wav", duration_sec=180.0, side="A", position=1)

    result = SideResult(
        seq=1,
        pdf_path=Path("test.pdf"),
        zip_path=Path("test.zip"),
        side="A",
        mode="tracks",
        status=AnalysisStatus.OK,
        pdf_tracks=[pdf_track],
        wav_tracks=[wav_track],
        total_pdf_sec=180,
        total_wav_sec=180.0,
        total_difference=0,
    )

    # WHEN displayed
    model = TracksTableModel(tolerance_settings, unicode_theme_settings)
    model.update_data(result)

    # THEN no crashes and title preserved
    index = model.index(0, 2)  # Title column
    display_text = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert isinstance(display_text, str)  # No exceptions thrown
    assert display_text == unicode_title
    assert "\uFFFD" not in display_text  # No corruption


def test_unicode_parser_edge_cases():
    """
    Test parser preserves Unicode in various edge cases.
    """
    test_cases = [
        {'title': '', 'side': 'A', 'position': 1, 'duration_formatted': '00:00'},  # Empty
        {'title': '🚀⭐💫', 'side': 'A', 'position': 1, 'duration_formatted': '00:01'},  # Emoji
        {'title': 'e\u0301', 'side': 'A', 'position': 1, 'duration_formatted': '00:02'},  # Combining char
    ]

    parser = TracklistParser()
    for case in test_cases:
        track_info = parser.parse_single_track(case)
        assert track_info.title == case['title'], f"Failed to preserve Unicode: {case['title']}"
        assert "\uFFFD" not in track_info.title
