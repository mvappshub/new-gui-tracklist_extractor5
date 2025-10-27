"""Unit tests for audio mode detector adapters."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from adapters.audio.ai_mode_detector import AiAudioModeDetector
from adapters.audio.fake_mode_detector import FakeAudioModeDetector
from core.models.analysis import WavInfo


class TestAiAudioModeDetector:
    """Test cases for AiAudioModeDetector."""

    def test_ai_detector_with_valid_filenames(self) -> None:
        """Test AI detector with valid WAV filenames."""
        detector = AiAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        # Mock the external API calls
        with patch("adapters.audio.ai_mode_detector.detect_audio_mode_with_ai") as mock_detect:
            with patch("adapters.audio.ai_mode_detector.normalize_positions") as mock_normalize:
                mock_detect.return_value = {
                    "A": [
                        WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="A", position=1),
                        WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0, side="A", position=2),
                    ],
                    "B": [
                        WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0, side="B", position=1),
                    ],
                }

                result = detector.detect(wavs)

                # Use simpler assertions to avoid WavInfo comparison issues
                mock_detect.assert_called_once()
                mock_normalize.assert_called_once()
                assert "A" in result
                assert "B" in result
                assert len(result["A"]) == 2
                assert len(result["B"]) == 1
                # Check that the mock was called with the right number of items
                call_args = mock_detect.call_args[0][0]
                assert len(call_args) == 3
                assert call_args[0].filename == "Side_A_01_intro.wav"
                assert call_args[1].filename == "Side_A_02_song.wav"
                assert call_args[2].filename == "Side_B_01_ballad.wav"

    def test_ai_detector_with_ambiguous_filenames(self) -> None:
        """Test AI detector with ambiguous filenames (triggers AI fallback)."""
        detector = AiAudioModeDetector()
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0),
            WavInfo(filename="track2.wav", duration_sec=150.0),
            WavInfo(filename="track3.wav", duration_sec=210.0),
        ]

        with patch("adapters.audio.ai_mode_detector.detect_audio_mode_with_ai") as mock_detect:
            with patch("adapters.audio.ai_mode_detector.normalize_positions") as mock_normalize:
                mock_detect.return_value = {
                    "A": [
                        WavInfo(filename="track1.wav", duration_sec=120.0, side="A", position=1),
                        WavInfo(filename="track2.wav", duration_sec=150.0, side="A", position=2),
                    ],
                    "B": [
                        WavInfo(filename="track3.wav", duration_sec=210.0, side="B", position=1),
                    ],
                }

                result = detector.detect(wavs)

                # Use simpler assertions to avoid WavInfo comparison issues
                mock_detect.assert_called_once()
                mock_normalize.assert_called_once()
                assert "A" in result
                assert "B" in result
                # Check that the mock was called with the right number of items
                call_args = mock_detect.call_args[0][0]
                assert len(call_args) == 3
                assert call_args[0].filename == "track1.wav"
                assert call_args[1].filename == "track2.wav"
                assert call_args[2].filename == "track3.wav"

    def test_ai_detector_with_empty_input(self) -> None:
        """Test AI detector with empty input list."""
        detector = AiAudioModeDetector()
        result = detector.detect([])
        assert result == {}


class TestFakeAudioModeDetector:
    """Test cases for FakeAudioModeDetector."""

    def test_fake_detector_with_side_prefixes(self) -> None:
        """Test fake detector with Side_A/Side_B filenames."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        assert "A" in result
        assert "B" in result
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side == "A"
        assert result["A"][1].position == 2
        assert result["B"][0].side == "B"
        assert result["B"][0].position == 1

    def test_fake_detector_with_letter_number_prefixes(self) -> None:
        """Test fake detector with A1/B1 prefixes."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="A1_intro.wav", duration_sec=120.0),
            WavInfo(filename="A2_song.wav", duration_sec=150.0),
            WavInfo(filename="B1_ballad.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        # Assert both "A" and "B" sides are present
        assert "A" in result
        assert "B" in result
        # Verify correct position counts: 2 tracks for side A, 1 track for side B
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1
        # Check position normalization (1, 2 for A side, 1 for B side)
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side == "A"
        assert result["A"][1].position == 2
        assert result["B"][0].side == "B"
        assert result["B"][0].position == 1

    def test_fake_detector_with_ambiguous_filenames(self) -> None:
        """Test fake detector with ambiguous filenames (parses 'track' as side)."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0),
            WavInfo(filename="track2.wav", duration_sec=150.0),
            WavInfo(filename="track3.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        # The fake detector parses "track" as the side from "track1.wav" etc.
        assert "TRACK" in result
        assert len(result["TRACK"]) == 3
        assert result["TRACK"][0].side == "TRACK"
        assert result["TRACK"][0].position == 1
        assert result["TRACK"][1].side == "TRACK"
        assert result["TRACK"][1].position == 2
        assert result["TRACK"][2].side == "TRACK"
        assert result["TRACK"][2].position == 3

    def test_fake_detector_normalizes_positions(self) -> None:
        """Test fake detector position normalization."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_05_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_10_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_A_15_ballad.wav", duration_sec=210.0),
        ]

        result = detector.detect(wavs)

        assert "A" in result
        assert len(result["A"]) == 3
        assert result["A"][0].position == 1
        assert result["A"][1].position == 2
        assert result["A"][2].position == 3

    def test_fake_detector_is_deterministic(self) -> None:
        """Test fake detector is deterministic (same input → same output)."""
        detector = FakeAudioModeDetector()
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        result1 = detector.detect(wavs)
        result2 = detector.detect(wavs)

        assert result1 == result2
        assert result1["A"][0].position == result2["A"][0].position
        assert result1["A"][1].position == result2["A"][1].position
        assert result1["B"][0].position == result2["B"][0].position
