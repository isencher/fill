"""
Unit tests for Parser Factory.

Tests cover file type detection, parser selection, and error handling.
"""

import pytest

from src.services.csv_parser import CSVParser
from src.services.excel_parser import ExcelParser
from src.services.parser_factory import get_parser, is_supported_file_type


class TestGetParser:
    """Test get_parser function for correct parser selection."""

    def test_get_parser_returns_csv_parser_for_csv(self):
        """Test that .csv files return CSVParser."""
        parser = get_parser("data.csv")
        assert parser == CSVParser

    def test_get_parser_returns_csv_parser_for_tsv(self):
        """Test that .tsv files return CSVParser."""
        parser = get_parser("data.tsv")
        assert parser == CSVParser

    def test_get_parser_returns_csv_parser_for_txt(self):
        """Test that .txt files return CSVParser."""
        parser = get_parser("data.txt")
        assert parser == CSVParser

    def test_get_parser_returns_excel_parser_for_xlsx(self):
        """Test that .xlsx files return ExcelParser."""
        parser = get_parser("data.xlsx")
        assert parser == ExcelParser

    def test_get_parser_returns_excel_parser_for_xlsm(self):
        """Test that .xlsm files return ExcelParser."""
        parser = get_parser("data.xlsm")
        assert parser == ExcelParser

    def test_get_parser_case_insensitive_extension(self):
        """Test that file extension detection is case-insensitive."""
        # Uppercase extensions
        assert get_parser("data.CSV") == CSVParser
        assert get_parser("data.XLSX") == ExcelParser

        # Mixed case extensions
        assert get_parser("data.Csv") == CSVParser
        assert get_parser("data.XlSX") == ExcelParser

    def test_get_parser_with_path_object(self):
        """Test that get_parser works with pathlib.Path objects."""
        from pathlib import Path

        # CSV with Path object
        parser = get_parser(Path("data.csv"))
        assert parser == CSVParser

        # Excel with Path object
        parser = get_parser(Path("data.xlsx"))
        assert parser == ExcelParser

    def test_get_parser_with_directory_in_path(self):
        """Test that get_parser works with directory paths."""
        # CSV with directory
        parser = get_parser("uploads/data.csv")
        assert parser == CSVParser

        # Excel with directory
        parser = get_parser("files/exports/data.xlsx")
        assert parser == ExcelParser

        # Nested directories
        parser = get_parser("a/b/c/data.csv")
        assert parser == CSVParser

    def test_get_parser_unsupported_extension_raises_error(self):
        """Test that unsupported file extensions raise ValueError."""
        unsupported_types = [
            "data.json",
            "data.xml",
            "data.yaml",
            "data.yml",
            "data.pdf",
            "data.docx",
            "data.png",
            "data.jpg",
            "data.zip",
            "data.tar.gz",
            "data.md",
            "data.py",
            "data.txt",  # This is actually supported, should pass
        ]

        for file_path in unsupported_types:
            if file_path.endswith(".txt"):
                # .txt is supported for CSV (tab/semicolon/pipe delimited)
                continue

            with pytest.raises(ValueError, match="Unsupported file type"):
                get_parser(file_path)

    def test_get_parser_error_message_includes_extension(self):
        """Test that error message includes the unsupported extension."""
        with pytest.raises(ValueError) as exc_info:
            get_parser("data.json")

        error_msg = str(exc_info.value)
        assert ".json" in error_msg
        assert "Supported types" in error_msg

    def test_get_parser_error_message_lists_supported_types(self):
        """Test that error message lists all supported types."""
        with pytest.raises(ValueError) as exc_info:
            get_parser("data.unknown")

        error_msg = str(exc_info.value)
        assert ".csv" in error_msg
        assert ".tsv" in error_msg
        assert ".txt" in error_msg
        assert ".xlsx" in error_msg
        assert ".xlsm" in error_msg


class TestIsSupportedFileType:
    """Test is_supported_file_type function."""

    def test_supported_csv_returns_true(self):
        """Test that .csv files return True."""
        assert is_supported_file_type("data.csv") is True

    def test_supported_tsv_returns_true(self):
        """Test that .tsv files return True."""
        assert is_supported_file_type("data.tsv") is True

    def test_supported_txt_returns_true(self):
        """Test that .txt files return True."""
        assert is_supported_file_type("data.txt") is True

    def test_supported_xlsx_returns_true(self):
        """Test that .xlsx files return True."""
        assert is_supported_file_type("data.xlsx") is True

    def test_supported_xlsm_returns_true(self):
        """Test that .xlsm files return True."""
        assert is_supported_file_type("data.xlsm") is True

    def test_unsupported_json_returns_false(self):
        """Test that .json files return False."""
        assert is_supported_file_type("data.json") is False

    def test_unsupported_xml_returns_false(self):
        """Test that .xml files return False."""
        assert is_supported_file_type("data.xml") is False

    def test_unsupported_pdf_returns_false(self):
        """Test that .pdf files return False."""
        assert is_supported_file_type("data.pdf") is False

    def test_unsupported_image_returns_false(self):
        """Test that image files return False."""
        assert is_supported_file_type("data.png") is False
        assert is_supported_file_type("data.jpg") is False
        assert is_supported_file_type("data.gif") is False

    def test_unsupported_archive_returns_false(self):
        """Test that archive files return False."""
        assert is_supported_file_type("data.zip") is False
        assert is_supported_file_type("data.tar.gz") is False

    def test_case_insensitive(self):
        """Test that file type checking is case-insensitive."""
        assert is_supported_file_type("data.CSV") is True
        assert is_supported_file_type("data.XLSX") is True
        assert is_supported_file_type("data.JSON") is False

    def test_with_path_object(self):
        """Test that is_supported_file_type works with Path objects."""
        from pathlib import Path

        assert is_supported_file_type(Path("data.csv")) is True
        assert is_supported_file_type(Path("data.json")) is False

    def test_with_directory_in_path(self):
        """Test that directory paths work correctly."""
        assert is_supported_file_type("uploads/data.csv") is True
        assert is_supported_file_type("files/data.json") is False


class TestParserIntegration:
    """Test parser factory integration with actual parsers."""

    def test_factory_returns_parser_classes_not_instances(self):
        """Test that factory returns parser classes, not instances."""
        csv_parser = get_parser("data.csv")
        excel_parser = get_parser("data.xlsx")

        # Should be classes (type), not instances
        assert isinstance(csv_parser, type)
        assert isinstance(excel_parser, type)

        # Can instantiate them
        csv_instance = csv_parser()
        excel_instance = excel_parser()

        assert isinstance(csv_instance, CSVParser)
        assert isinstance(excel_instance, ExcelParser)

    def test_csv_parser_has_parse_method(self):
        """Test that CSVParser from factory has parse_csv method."""
        parser_class = get_parser("data.csv")
        assert hasattr(parser_class, "parse_csv")

    def test_excel_parser_has_parse_method(self):
        """Test that ExcelParser from factory has parse_excel method."""
        parser_class = get_parser("data.xlsx")
        assert hasattr(parser_class, "parse_excel")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_filename(self):
        """Test handling of filename without extension."""
        # No extension - should raise ValueError
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_parser("data")

    def test_hidden_file(self):
        """Test handling of hidden files (starting with dot)."""
        # Hidden file with extension - should work
        assert get_parser(".data.csv") == CSVParser
        assert get_parser(".hidden.xlsx") == ExcelParser

    def test_filename_with_multiple_dots(self):
        """Test handling of filenames with multiple dots."""
        # Should use last extension
        assert get_parser("data.backup.csv") == CSVParser
        assert get_parser("report.final.xlsx") == ExcelParser

    def test_filename_with_no_extension_only_dots(self):
        """Test handling of filename with only dots."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            get_parser("data...")

    def test_relative_path(self):
        """Test handling of relative paths."""
        assert get_parser("./data.csv") == CSVParser
        assert get_parser("../data.xlsx") == ExcelParser

    def test_absolute_path(self):
        """Test handling of absolute paths."""
        assert get_parser("/tmp/data.csv") == CSVParser
        assert get_parser("C:\\Users\\data.xlsx") == ExcelParser
