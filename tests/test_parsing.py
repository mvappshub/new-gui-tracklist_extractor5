from __future__ import annotations

import pytest
from pathlib import Path

from core.domain.parsing import StrictFilenameParser, ParsedFileInfo


class TestStrictFilenameParser:
    """Unit testy pro StrictFilenameParser."""

    def setup_method(self) -> None:
        """Inicializace parseru pro každý test."""
        self.parser = StrictFilenameParser()

    @pytest.mark.parametrize(
        "filename,expected_side,expected_position",
        [
            # Základní parsing pozice (čísla na začátku) - pouze na konci stringu
            ("01.wav", None, 1),
            ("1.flac", None, 1),
            ("02.wav", None, 2),
            ("10.mp3", None, 10),
            ("99.wav", None, 99),

            # Parsing strany (Side patterns)
            ("Side_A_Track.wav", "A", None),
            ("Side_AA_Song.mp3", "AA", None),
            ("side_b_Track.flac", "B", None),
            ("SIDE_C_Song.wav", "C", None),
            ("Side-A-Track.mp3", "A", None),
            ("Side_AA_Track.wav", "AA", None),

            # Kombinované patterny (A1, B2, atd.)
            ("A1_Track.wav", "A", 1),
            ("B2_Song.mp3", "B", 2),
            ("AA02_Track.flac", "AA", 2),
            ("C3_Song.wav", "C", 3),
            ("D10_Track.mp3", "D", 10),
            ("A1_intro.wav", "A", 1),
            ("B2_song.mp3", "B", 2),

            # Side s pozicí
            ("Side_A_01.wav", "A", 1),
            ("SideA_02.mp3", "A", 2),
            ("Side_A01.flac", "A", 1),
            ("side_b_3.wav", "B", 3),
            ("SIDE_C_05.mp3", "C", 5),
            ("Side_AA_10.wav", "AA", 10),

            # Edge cases - bez pozice a strany
            ("Track_Without_Numbers.wav", None, None),
            ("Random_Filename.mp3", None, None),
            ("No_Pattern_Here.flac", None, None),
            ("", None, None),

            # Speciální formáty
            ("Side_A_01_Track_Name.wav", "A", 1),
            ("A1_Side_B_02.mp3", "B", 2),  # Side_B má prioritu před A1
            ("00_Prefixed_Track.wav", None, None),  # 00 není validní pozice
            ("0_Track.wav", None, None),  # 0 není validní pozice

            # Case insensitive testy
            ("side_a_01.wav", "A", 1),
            ("SIDE_B_02.mp3", "B", 2),
            ("a1_track.flac", "A", 1),
            ("b2_song.wav", "B", 2),

            # Složité názvy
            ("Side_A_01_Intro_To_Track.wav", "A", 1),
            ("A1_Featuring_Artist_Song.mp3", "A", 1),
            ("Side_AA_02_Remix.flac", "AA", 2),
        ]
    )
    def test_parse_filename_comprehensive(
        self, filename: str, expected_side: str | None, expected_position: int | None
    ) -> None:
        """Parametrizovaný test pro různé formáty filename parsing."""
        result = self.parser.parse(filename)

        assert result.side == expected_side
        assert result.position == expected_position

    @pytest.mark.parametrize(
        "filename,expected",
        [
            # Test s úplnými cestami
            ("/path/to/Side_A_01.wav", ParsedFileInfo(side="A", position=1)),
            ("C:\\Users\\Music\\B2_Song.mp3", ParsedFileInfo(side="B", position=2)),
            ("./tracks/A1_Track.flac", ParsedFileInfo(side="A", position=1)),
            ("../parent/dir/Side_AA_02.wav", ParsedFileInfo(side="AA", position=2)),

            # Test s různými příponami
            ("01.WAV", ParsedFileInfo(side=None, position=1)),
            ("Side_A_02.MP3", ParsedFileInfo(side="A", position=2)),
            ("A1_Song.FLAC", ParsedFileInfo(side="A", position=1)),
            ("B2_Track.aiff", ParsedFileInfo(side="B", position=2)),

            # Test bez přípon
            ("01", ParsedFileInfo(side=None, position=1)),
            ("Side_A_02", ParsedFileInfo(side="A", position=2)),
            ("A1_Song", ParsedFileInfo(side="A", position=1)),
        ]
    )
    def test_parse_with_paths_and_extensions(self, filename: str, expected: ParsedFileInfo) -> None:
        """Test parsing s různými typy cest a přípon souborů."""
        result = self.parser.parse(filename)
        assert result == expected

    def test_parse_empty_filename(self) -> None:
        """Test parsing prázdného názvu souboru."""
        result = self.parser.parse("")
        assert result == ParsedFileInfo(side=None, position=None)

    def test_parse_filename_with_only_numbers(self) -> None:
        """Test parsing názvu obsahujícího pouze čísla."""
        result = self.parser.parse("12345.wav")
        assert result == ParsedFileInfo(side=None, position=None)

    def test_parse_filename_starting_with_zero(self) -> None:
        """Test parsing názvu začínajícího nulou."""
        result = self.parser.parse("001.wav")
        assert result == ParsedFileInfo(side=None, position=1)

    def test_parse_complex_side_patterns(self) -> None:
        """Test parsing složitějších patternů pro strany."""
        test_cases = [
            ("Side-A-01.wav", "A", 1),
            ("Side_AA_02.mp3", "AA", 2),
            ("Side-ABC-03.flac", "ABC", 3),
            ("Side_A-B_01.wav", "A", 1),  # První match
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_parse_position_only_various_formats(self) -> None:
        """Test parsing pouze pozice v různých formátech."""
        test_cases = [
            ("01.wav", None, 1),
            ("02.wav", None, 2),
            ("10.flac", None, 10),
            ("99.wav", None, 99),
            ("1.wav", None, 1),
            ("001.mp3", None, 1),  # Leading zeros are stripped
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_parse_side_only_various_formats(self) -> None:
        """Test parsing pouze strany v různých formátech."""
        test_cases = [
            ("Side_A.wav", "A", None),
            ("Side_AA.mp3", "AA", None),
            ("side_b.flac", "B", None),
            ("SIDE_C.wav", "C", None),
            ("Side-ABC.mp3", "ABC", None),
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_case_insensitive_parsing(self) -> None:
        """Test case insensitive parsing."""
        test_cases = [
            ("side_a_01.wav", "A", 1),
            ("SIDE_B_02.mp3", "B", 2),
            ("Side_Cc_03.flac", "CC", 3),
            ("a1_track.wav", "A", 1),
            ("b2_song.mp3", "B", 2),
            ("Aa01_Track.flac", "AA", 1),
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_priority_of_patterns(self) -> None:
        """Test priority parsing patternů podle skutečné implementace."""
        test_cases = [
            # Side pattern má prioritu před A1 patternem - parsuje první písmeno a pozici
            ("Side_A1_Track.wav", "A", 1),  # Parsuje jako Side_A -> A s pozicí 1 z A1

            # Position na začátku má prioritu před jinými patterny (ale pouze na konci stringu)
            ("01Side_A_Track.wav", "A", None),  # Parsuje Side_A -> A, ignoruje pozici 01

            # A1 pattern má prioritu před pozicí v jiném místě
            ("A1_02_Track.wav", "A", 1),  # Parsuje A1 jako A s pozicí 1, ignoruje 02

            # Side pattern v prostředku má prioritu
            ("A1_Side_B_02.wav", "B", 2),  # Parsuje Side_B s pozicí 2
        ]

        for filename, expected_side, expected_position in test_cases:
            result = self.parser.parse(filename)
            assert result.side == expected_side
            assert result.position == expected_position

    def test_pathlib_path_objects(self) -> None:
        """Test parsing s Path objekty."""
        test_cases = [
            (Path("Side_A_01.wav"), "A", 1),
            (Path("/path/to/B2_Song.mp3"), "B", 2),
            (Path("A1_Track.flac"), "A", 1),
        ]

        for path, expected_side, expected_position in test_cases:
            result = self.parser.parse(str(path))
            assert result.side == expected_side
            assert result.position == expected_position

    def test_parsed_file_info_equality(self) -> None:
        """Test rovnosti ParsedFileInfo objektů."""
        info1 = ParsedFileInfo(side="A", position=1)
        info2 = ParsedFileInfo(side="A", position=1)
        info3 = ParsedFileInfo(side="B", position=1)
        info4 = ParsedFileInfo(side="A", position=2)

        assert info1 == info2
        assert info1 != info3
        assert info1 != info4
        assert info1 != ParsedFileInfo(side=None, position=None)

    def test_windows_path_parsing(self) -> None:
        """Test parsing Windows cest s backslash."""
        # Test specific Windows path cases
        test_cases = [
            ("C:\\Users\\Music\\B2_Song.mp3", "B", 2),
            ("D:\\Audio\\Side_A_01.wav", "A", 1),
            ("\\\\server\\share\\A1_Track.flac", "A", 1),
        ]

        for path, expected_side, expected_position in test_cases:
            result = self.parser.parse(path)
            assert result.side == expected_side
            assert result.position == expected_position