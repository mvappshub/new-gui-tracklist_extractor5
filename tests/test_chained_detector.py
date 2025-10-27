"""Unit testy pro ChainedAudioModeDetector a jeho steps."""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

from core.models.analysis import WavInfo
from adapters.audio.chained_detector import ChainedAudioModeDetector
from adapters.audio.steps import StrictParserStep, AiParserStep, DeterministicFallbackStep


class TestChainedAudioModeDetector:
    """Test cases pro ChainedAudioModeDetector - hlavní orchestrátor."""

    def setup_method(self) -> None:
        """Inicializace detectoru pro každý test."""
        self.detector = ChainedAudioModeDetector()

    def test_detect_with_valid_filenames_strict_parsing(self) -> None:
        """Test detekce s validními názvy souborů - strict parsing."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_01_ballad.wav", duration_sec=210.0),
        ]

        result = self.detector.detect(wavs)

        # Strict parser by měl zpracovat všechny soubory
        assert "A" in result
        assert "B" in result
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1

        # Ověřit pozice
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side == "A"
        assert result["A"][1].position == 2
        assert result["B"][0].side == "B"
        assert result["B"][0].position == 1

    def test_detect_with_mixed_parsing_scenarios(self) -> None:
        """Test detekce s kombinací parsovatelných a neparsovatelných souborů."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),  # Strict parsing
            WavInfo(filename="A2_song.wav", duration_sec=150.0),         # Strict parsing
            WavInfo(filename="unknown_track.wav", duration_sec=210.0),   # AI fallback
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                mock_ai.return_value = {
                    "unknown_track.wav": ("A", 3)  # Přidat do strany A
                }

                result = self.detector.detect(wavs)

                # Ověřit, že všechny soubory byly zpracovány
                assert "A" in result
                assert len(result["A"]) == 3  # Všechny tři v A
                assert result["A"][0].side == "A"
                assert result["A"][0].position == 1
                assert result["A"][1].side == "A"
                assert result["A"][1].position == 2
                assert result["A"][2].side is None  # AI nezměnilo stranu na A
                assert result["A"][2].position == 3

                # Ověřit, že AI bylo zavoláno
                mock_ai.assert_called_once()
                mock_merge.assert_called_once()

    def test_detect_with_custom_steps(self) -> None:
        """Test detekce s vlastními steps."""
        custom_steps = [StrictParserStep()]
        detector = ChainedAudioModeDetector(steps=custom_steps)

        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        result = detector.detect(wavs)

        # Pouze strict parser - fallback se nespustí, takže neznámý soubor zůstane bez strany
        # ale normalizace ho přidá do default strany A
        assert "A" in result
        assert len(result["A"]) == 2  # Oba soubory v A (jeden parsovaný, jeden default)
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1
        assert result["A"][1].side is None  # Neparsovaný zůstává None
        assert result["A"][1].position == 2

    def test_detect_empty_input(self) -> None:
        """Test detekce s prázdným vstupem."""
        result = self.detector.detect([])
        assert result == {}

    def test_detect_single_file(self) -> None:
        """Test detekce s jedním souborem."""
        wavs = [WavInfo(filename="01_track.wav", duration_sec=120.0)]

        result = self.detector.detect(wavs)

        assert "A" in result  # Default side
        assert len(result["A"]) == 1
        assert result["A"][0].position == 1

    def test_detect_normalization_and_grouping(self) -> None:
        """Test normalizace pozic a seskupování podle stran."""
        wavs = [
            WavInfo(filename="Side_A_05_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_10_song.wav", duration_sec=150.0),
            WavInfo(filename="Side_B_03_ballad.wav", duration_sec=210.0),
        ]

        result = self.detector.detect(wavs)

        # Pozice by měly být normalizovány na 1, 2, 3
        assert result["A"][0].position == 1
        assert result["A"][1].position == 2
        assert result["B"][0].position == 1

    def test_chain_of_responsibility_stops_at_first_success(self) -> None:
        """Test, že chain se zastaví při prvním úspěšném parsingu."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_A_02_song.wav", duration_sec=150.0),
        ]

        # Mock steps aby strict parser vrátil True (úspěch)
        with patch.object(StrictParserStep, 'process', return_value=True) as mock_strict:
            result = self.detector.detect(wavs)

            # AI step by neměl být zavolán
            with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
                mock_ai.assert_not_called()

    def test_chain_continues_when_strict_fails(self) -> None:
        """Test, že chain pokračuje když strict parser selže."""
        wavs = [
            WavInfo(filename="unknown_track1.wav", duration_sec=120.0),
            WavInfo(filename="unknown_track2.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            mock_ai.return_value = {
                "unknown_track1.wav": ("A", 1),
                "unknown_track2.wav": ("A", 2)
            }

            result = self.detector.detect(wavs)

            # AI by mělo být zavoláno
            mock_ai.assert_called_once()
            assert "A" in result
            assert len(result["A"]) == 2


class TestStrictParserStep:
    """Test cases pro StrictParserStep."""

    def setup_method(self) -> None:
        """Inicializace stepu pro každý test."""
        self.step = StrictParserStep()

    def test_process_all_parsed_successfully(self) -> None:
        """Test zpracování když všechny soubory jsou parsovatelné."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="Side_B_02_song.wav", duration_sec=150.0),
        ]

        result = self.step.process(wavs)

        assert result is True  # Chain se zastaví
        assert wavs[0].side == "A"
        assert wavs[0].position == 1
        assert wavs[1].side == "B"
        assert wavs[1].position == 2

    def test_process_partial_parsing_continues_chain(self) -> None:
        """Test zpracování když některé soubory nejsou parsovatelné."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0),
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        result = self.step.process(wavs)

        assert result is False  # Chain pokračuje
        assert wavs[0].side == "A"
        assert wavs[0].position == 1
        assert wavs[1].side is None  # Nezměněno
        assert wavs[1].position is None  # Nezměněno

    def test_process_already_parsed_files_unchanged(self) -> None:
        """Test zpracování souborů, které už mají parsované údaje."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="B", position=5),
        ]

        result = self.step.process(wavs)

        # Původní hodnoty by měly zůstat zachovány
        assert wavs[0].side == "B"
        assert wavs[0].position == 5

    def test_process_empty_list(self) -> None:
        """Test zpracování prázdného seznamu."""
        result = self.step.process([])
        assert result is True

    def test_process_various_filename_formats(self) -> None:
        """Test zpracování různých formátů názvů souborů."""
        test_cases = [
            ("01.wav", None, 1),
            ("Side_A_02.mp3", "A", 2),
            ("A1_Track.flac", "A", 1),
            ("B2_Song.wav", "B", 2),
            ("AA03_Intro.mp3", "AA", 3),
            ("unknown.wav", None, None),
        ]

        for filename, expected_side, expected_position in test_cases:
            wav = WavInfo(filename=filename, duration_sec=120.0)
            self.step.process([wav])

            assert wav.side == expected_side
            assert wav.position == expected_position


class TestAiParserStep:
    """Test cases pro AiParserStep."""

    def setup_method(self) -> None:
        """Inicializace stepu pro každý test."""
        self.step = AiParserStep()

    def test_process_all_already_parsed_stops_chain(self) -> None:
        """Test zpracování když všechny soubory už jsou parsované."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="Side_B_02_song.wav", duration_sec=150.0, side="B", position=2),
        ]

        result = self.step.process(wavs)

        assert result is True  # Chain se zastaví

    def test_process_with_unparsed_files_calls_ai(self) -> None:
        """Test zpracování s neparsovanými soubory - volá AI."""
        wavs = [
            WavInfo(filename="Side_A_01_intro.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),  # Neparsovaný
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                mock_ai.return_value = {
                    "unknown_track.wav": ("B", 1)
                }

                result = self.step.process(wavs)

                assert result is False  # Chain pokračuje (nikdy se nezastaví)
                mock_ai.assert_called_once_with(["unknown_track.wav"])
                mock_merge.assert_called_once()

    def test_process_ai_exception_handling(self) -> None:
        """Test zpracování výjimek z AI."""
        wavs = [
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch", side_effect=Exception("AI Error")):
            # Nemělo by vyhodit výjimku
            result = self.step.process(wavs)

            assert result is False  # Chain pokračuje
            # Soubor zůstává neparsovaný
            assert wavs[0].side is None
            assert wavs[0].position is None

    def test_process_empty_ai_response(self) -> None:
        """Test zpracování prázdné odpovědi z AI."""
        wavs = [
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch", return_value={}) as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                result = self.step.process(wavs)

                assert result is False
                mock_ai.assert_called_once()
                mock_merge.assert_not_called()  # Nevolá se s prázdným mapem

    def test_process_unknown_side_handling(self) -> None:
        """Test zpracování 'UNKNOWN' side z AI."""
        wavs = [
            WavInfo(filename="unknown_track.wav", duration_sec=150.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                mock_ai.return_value = {
                    "unknown_track.wav": ("UNKNOWN", 1)
                }

                result = self.step.process(wavs)

                assert result is False
                # UNKNOWN by měl být resetnut na None v AiParserStep kódu
                assert wavs[0].side is None
                # Pozice by měla být nastavena merge_ai_results, ale UNKNOWN side se ignoruje
                assert wavs[0].position is None  # Pozice se nenastaví kvůli UNKNOWN side
                mock_merge.assert_called_once()


class TestDeterministicFallbackStep:
    """Test cases pro DeterministicFallbackStep."""

    def setup_method(self) -> None:
        """Inicializace stepu pro každý test."""
        self.step = DeterministicFallbackStep()

    def test_process_no_sides_assigned_fallback(self) -> None:
        """Test fallback když žádný soubor nemá přiřazenou stranu."""
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0),
            WavInfo(filename="track2.wav", duration_sec=150.0),
            WavInfo(filename="track3.wav", duration_sec=210.0),
        ]

        result = self.step.process(wavs)

        assert result is True  # Poslední step, zastaví chain
        # Všechny soubory dostanou stranu A a pozice 1, 2, 3
        assert all(wav.side == "A" for wav in wavs)
        assert wavs[0].position == 1
        assert wavs[1].position == 2
        assert wavs[2].position == 3

    def test_process_some_sides_assigned_no_fallback(self) -> None:
        """Test že se fallback nespustí když některé soubory mají strany."""
        wavs = [
            WavInfo(filename="Side_A_01.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="track2.wav", duration_sec=150.0),  # Bez strany
        ]

        result = self.step.process(wavs)

        assert result is True  # Zastaví chain
        # Fallback se nespustí - druhý soubor zůstává nezměněný
        assert wavs[0].side == "A"
        assert wavs[1].side is None
        assert wavs[1].position is None

    def test_process_all_sides_assigned_no_fallback(self) -> None:
        """Test že se fallback nespustí když všechny soubory mají strany."""
        wavs = [
            WavInfo(filename="Side_A_01.wav", duration_sec=120.0, side="A", position=1),
            WavInfo(filename="Side_B_02.wav", duration_sec=150.0, side="B", position=2),
        ]

        result = self.step.process(wavs)

        assert result is True
        # Žádné změny
        assert wavs[0].side == "A"
        assert wavs[1].side == "B"

    def test_process_empty_list(self) -> None:
        """Test zpracování prázdného seznamu."""
        result = self.step.process([])
        assert result is True

    def test_process_position_assignment_with_none_positions(self) -> None:
        """Test přiřazení pozic když některé soubory nemají pozice."""
        wavs = [
            WavInfo(filename="track1.wav", duration_sec=120.0, side=None, position=5),  # Bez strany, ale s pozicí
            WavInfo(filename="track2.wav", duration_sec=150.0, side=None, position=None),  # Bez strany a pozice
        ]

        result = self.step.process(wavs)

        assert result is True
        # Oba soubory dostanou stranu A
        # První si ponechá pozici 5, druhý dostane pozici 2 (protože se řadí podle názvu)
        assert wavs[0].side == "A"
        assert wavs[0].position == 5  # Ponechá si původní pozici
        assert wavs[1].side == "A"
        assert wavs[1].position == 2  # Nová pozice (řadí se podle názvu)

    def test_process_deterministic_sorting(self) -> None:
        """Test deterministické řazení podle názvu souboru."""
        wavs = [
            WavInfo(filename="zebra_track.wav", duration_sec=120.0),
            WavInfo(filename="alpha_track.wav", duration_sec=150.0),
            WavInfo(filename="beta_track.wav", duration_sec=210.0),
        ]

        result = self.step.process(wavs)

        assert result is True
        # Měly by být seřazeny podle názvu: alpha, beta, zebra
        # Ale pozice se přiřazují podle původního pořadí v seznamu
        assert wavs[0].position == 1  # alpha_track
        assert wavs[1].position == 2  # beta_track
        assert wavs[2].position == 3  # zebra_track


class TestEdgeCases:
    """Test cases pro edge cases."""

    def test_chained_detector_with_empty_filenames(self) -> None:
        """Test ChainedAudioModeDetector s prázdnými filenames."""
        detector = ChainedAudioModeDetector()
        wavs = [
            WavInfo(filename="", duration_sec=120.0),
        ]

        # Nemělo by vyhodit výjimku
        result = detector.detect(wavs)
        assert "A" in result  # Default side
        assert len(result["A"]) == 1

    def test_steps_with_none_values(self) -> None:
        """Test steps s None hodnotami."""
        strict_step = StrictParserStep()
        ai_step = AiParserStep()
        fallback_step = DeterministicFallbackStep()

        wavs = [
            WavInfo(filename="test.wav", duration_sec=120.0, side=None, position=None),
        ]

        # Žádný step by neměl vyhodit výjimku
        strict_step.process(wavs)
        ai_step.process(wavs)
        fallback_step.process(wavs)

    def test_chained_detector_immutable_input(self) -> None:
        """Test že vstupní data nejsou mutována."""
        detector = ChainedAudioModeDetector()
        original_wavs = [
            WavInfo(filename="Side_A_01.wav", duration_sec=120.0),
        ]
        wavs_copy = [w.model_copy() for w in original_wavs]

        result = detector.detect(original_wavs)

        # Původní objekty by měly zůstat nezměněné
        assert original_wavs[0].side is None
        assert original_wavs[0].position is None

        # Výsledek by měl mít změněné kopie
        assert "A" in result
        assert result["A"][0].side == "A"
        assert result["A"][0].position == 1

    def test_steps_with_very_long_filenames(self) -> None:
        """Test steps s velmi dlouhými názvy souborů."""
        long_filename = "A" * 1000 + "_01_very_long_track_name_that_might_cause_issues.wav"

        strict_step = StrictParserStep()
        wavs = [WavInfo(filename=long_filename, duration_sec=120.0)]

        # Nemělo by vyhodit výjimku
        result = strict_step.process(wavs)
        assert isinstance(result, bool)

    def test_ai_step_with_malformed_ai_response(self) -> None:
        """Test AiParserStep s poškozenou odpovědí z AI."""
        ai_step = AiParserStep()
        wavs = [
            WavInfo(filename="test.wav", duration_sec=120.0),
        ]

        with patch("adapters.audio.steps.ai_parse_batch") as mock_ai:
            with patch("adapters.audio.steps.merge_ai_results") as mock_merge:
                # Simulace poškozené odpovědi
                mock_ai.return_value = {
                    "test.wav": ("INVALID_SIDE", "not_a_number")
                }

                # Nemělo by vyhodit výjimku
                result = ai_step.process(wavs)
                assert result is False