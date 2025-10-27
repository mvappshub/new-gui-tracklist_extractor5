#!/usr/bin/env python3

"""
Pytest testy pro automatizovanou validaci auto-export funkcionality.

Testuje všechny čtyři scénáře ze spec:
1. Success - export.auto=true, JSON se vytvoří
2. Disabled - export.auto=false, žádný soubor se nevytvoří
3. Directory Creation - neexistující adresář se vytvoří
4. Write Failure - chyba při zápisu je propagována a zalogována
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from core.domain.analysis_status import AnalysisStatus

import pytest

# Import funkcionality pro testování
from core.models.analysis import SideResult, TrackInfo, WavInfo
from core.models.settings import ExportSettings
from services.export_service import export_results_to_json

pytestmark = pytest.mark.qt_no_exception_capture


class TestExportAuto:
    """Testovací třída pro auto-export funkcionalitu."""

    def create_mock_side_result(self, seq: int = 1) -> SideResult:
        """Vytvoří mock SideResult objekt pro testování."""
        return SideResult(
            seq=seq,
            pdf_path=Path(f"/test/pdf_{seq}.pdf"),
            zip_path=Path(f"/test/zip_{seq}.zip"),
            side="A",
            mode="side",
            status=AnalysisStatus.OK,
            pdf_tracks=[TrackInfo(title=f"Track {seq}", side="A", position=1, duration_sec=180)],
            wav_tracks=[WavInfo(filename=f"track_{seq}.wav", duration_sec=180.0, side="A", position=1)],
            total_pdf_sec=180,
            total_wav_sec=180.0,
            total_difference=0,
        )

    def test_export_success(self, tmp_path):
        """Test 2.1: Ověřit, že když export.auto=True, JSON soubor je vytvořen."""
        # Arrange
        export_dir = tmp_path / "exports"
        mock_results = [self.create_mock_side_result(1), self.create_mock_side_result(2)]

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is not None
        assert export_dir.exists()
        assert result_path.exists()

        # Ověřit název souboru
        expected_pattern = f"analysis_{datetime.now().strftime('%Y%m%d')}_"
        assert expected_pattern in result_path.name
        assert result_path.name.endswith(".json")

        # Ověřit obsah JSON
        with open(result_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "exported_at" in data
        assert "count" in data
        assert "results" in data
        assert data["count"] == 2
        assert len(data["results"]) == 2

        # Ověřit strukturu prvního výsledku
        result = data["results"][0]
        assert "seq" in result
        assert "pdf_path" in result
        assert "zip_path" in result
        assert "side" in result
        assert "mode" in result
        assert "status" in result
        assert "pdf_tracks" in result
        assert "wav_tracks" in result
        assert "total_pdf_sec" in result
        assert "total_wav_sec" in result
        assert "total_difference" in result

        # Ověřit, že cesty jsou stringy (JSON-safe)
        assert isinstance(result["pdf_path"], str)
        assert isinstance(result["zip_path"], str)
        assert isinstance(result["total_pdf_sec"], int)
        assert isinstance(result["total_wav_sec"], (int, float))

    def test_export_disabled(self, tmp_path):
        """Test 2.2: Ověřit, že když export.auto=False, žádný JSON soubor není vytvořen."""
        # Arrange
        export_dir = tmp_path / "exports"
        mock_results = [self.create_mock_side_result()]

        export_settings = ExportSettings(auto_export=False, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is None
        assert not export_dir.exists()

    def test_export_directory_creation(self, tmp_path):
        """Test 2.3: Ověřit, že když export.default_dir neexistuje, je automaticky vytvořen."""
        # Arrange
        export_dir = tmp_path / "new_exports_dir"
        mock_results = [self.create_mock_side_result()]

        # Zajistit, že adresář neexistuje
        assert not export_dir.exists()

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is not None
        assert export_dir.exists()  # Adresář byl vytvořen
        assert export_dir.is_dir()
        assert result_path.exists()
        assert result_path.parent == export_dir

    def test_export_write_failure(self, tmp_path, caplog):
        """Test 2.4: Ověřit, že když aplikace nemůže zapsat do export.default_dir, chyba je propagována."""
        # Arrange
        export_dir = tmp_path / "exports"
        export_dir.mkdir()
        mock_results = [self.create_mock_side_result()]

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Mock json.dump funkci, aby vyvolala PermissionError při zápisu
        with patch("json.dump") as mock_json_dump, caplog.at_level(logging.ERROR):
            mock_json_dump.side_effect = PermissionError("Access denied")

            with pytest.raises(PermissionError):
                export_results_to_json(mock_results, export_settings)

        assert len(caplog.records) > 0
        error_logged = any("Failed to export analysis results" in record.message for record in caplog.records)
        assert error_logged, "Expected error log not found in: {}".format([r.message for r in caplog.records])
        assert not any(export_dir.glob("*.json")), "Export file should not be created on failure"

    def test_export_empty_results(self, tmp_path):
        """Test: Ověřit, že s prázdnými výsledky se nevytváří žádný export."""
        # Arrange
        export_dir = tmp_path / "exports"
        empty_results = []

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(empty_results, export_settings)

        # Assert
        assert result_path is None
        assert not export_dir.exists()

    def test_export_json_structure_validation(self, tmp_path):
        """Test: Detailní ověření struktury exportovaného JSON."""
        # Arrange
        export_dir = tmp_path / "exports"
        mock_results = [
            SideResult(
                seq=1,
                pdf_path=Path("/test/path.pdf"),
                zip_path=Path("/test/path.zip"),
                side="A",
                mode="tracks",
                status=AnalysisStatus.OK,
                pdf_tracks=[TrackInfo(title="Test Track", side="A", position=1, duration_sec=245)],
                wav_tracks=[WavInfo(filename="test.wav", duration_sec=245.5, side="A", position=1)],
                total_pdf_sec=245,
                total_wav_sec=245.5,
                total_difference=0,
            )
        ]

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        # Act
        result_path = export_results_to_json(mock_results, export_settings)

        # Assert
        assert result_path is not None

        with open(result_path, encoding="utf-8") as f:
            data = json.load(f)

            # Ověřit základní strukturu
            assert "exported_at" in data
            assert "count" in data
            assert "results" in data
            assert data["count"] == 1

            result = data["results"][0]

            # Ověřit všechna požadovaná pole
            required_fields = [
                "seq",
                "pdf_path",
                "zip_path",
                "side",
                "mode",
                "status",
                "pdf_tracks",
                "wav_tracks",
                "total_pdf_sec",
                "total_wav_sec",
                "total_difference",
            ]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"

            # Ověřit typy dat
            assert isinstance(result["pdf_path"], str)
            assert isinstance(result["zip_path"], str)
            assert isinstance(result["total_pdf_sec"], int)
            assert isinstance(result["total_wav_sec"], int | float)

            # Ověřit strukturu tracks
            assert len(result["pdf_tracks"]) == 1
            pdf_track = result["pdf_tracks"][0]
            assert "title" in pdf_track
            assert "side" in pdf_track
            assert "position" in pdf_track
            assert "duration_sec" in pdf_track

            wav_track = result["wav_tracks"][0]
            assert "filename" in wav_track
            assert "duration_sec" in wav_track

    def test_export_open_failure(self, tmp_path, caplog):
        """Test: Ověřit, že když selže otevření souboru pro zápis, chyba je propagována."""
        # Arrange
        export_dir = tmp_path / "exports"
        export_dir.mkdir()

        export_settings = ExportSettings(auto_export=True, export_dir=export_dir)

        with patch("pathlib.Path.open", side_effect=PermissionError("Access denied")), caplog.at_level(logging.ERROR):
            with pytest.raises(PermissionError):
                export_results_to_json(
                    [self.create_mock_side_result(1)],
                    export_settings,
                )

        assert any("Failed to export analysis results" in record.message for record in caplog.records)
        assert not any(export_dir.glob("*.json"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
