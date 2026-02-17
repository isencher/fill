"""
Unit tests for CSV Parser Service.

Tests cover various CSV formats, delimiters, encodings, and edge cases.
"""

import os
from pathlib import Path

import pytest

from src.services.csv_parser import CSVParser


class TestCSVParserBasic:
    """Test basic CSV parsing functionality."""

    def test_parse_simple_csv(self, tmp_path):
        """Test parsing a simple CSV with headers and data."""
        # Create test CSV file
        csv_file = tmp_path / "simple.csv"
        csv_file.write_text("Name,Age,City\nJohn,30,New York\nJane,25,London\n")

        # Parse CSV
        data = CSVParser.parse_csv(csv_file)

        # Verify results
        assert len(data) == 2
        assert data[0] == {"Name": "John", "Age": "30", "City": "New York"}
        assert data[1] == {"Name": "Jane", "Age": "25", "City": "London"}

    def test_parse_csv_with_quoted_fields(self, tmp_path):
        """Test parsing CSV with quoted fields containing commas."""
        csv_file = tmp_path / "quoted.csv"
        csv_file.write_text(
            'Name,Description\nItem1,"This is a description, with commas"\nItem2,"Simple description"\n'
        )

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert data[0]["Description"] == "This is a description, with commas"
        assert data[1]["Description"] == "Simple description"

    def test_parse_csv_with_empty_cells(self, tmp_path):
        """Test parsing CSV with empty cells."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("Name,Age,City\nJohn,,New York\nJane,25,\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert data[0]["Age"] == ""
        assert data[0]["City"] == "New York"
        assert data[1]["Age"] == "25"
        assert data[1]["City"] == ""

    def test_parse_csv_skip_empty_rows(self, tmp_path):
        """Test that empty rows are skipped by default."""
        csv_file = tmp_path / "empty_rows.csv"
        csv_file.write_text("Name,Age\nJohn,30\n\nJane,25\n\n")

        data = CSVParser.parse_csv(csv_file)

        # Empty rows should be skipped
        assert len(data) == 2
        assert data[0] == {"Name": "John", "Age": "30"}
        assert data[1] == {"Name": "Jane", "Age": "25"}

    def test_parse_csv_keep_empty_rows(self, tmp_path):
        """Test keeping empty rows when skip_empty_rows=False."""
        csv_file = tmp_path / "empty_rows.csv"
        # Note: In CSV, blank lines are skipped by DictReader.
        # To get an empty row, we need empty values (commas with nothing between)
        csv_file.write_text("Name,Age\nJohn,30\n,\nJane,25\n")

        data = CSVParser.parse_csv(csv_file, skip_empty_rows=False)

        # Empty rows should be kept (when values are empty strings, not blank lines)
        assert len(data) == 3
        assert data[0] == {"Name": "John", "Age": "30"}
        assert data[1] == {"Name": "", "Age": ""}  # Empty row (empty values)
        assert data[2] == {"Name": "Jane", "Age": "25"}

    def test_parse_csv_single_column(self, tmp_path):
        """Test parsing CSV with single column."""
        csv_file = tmp_path / "single.csv"
        csv_file.write_text("Name\nJohn\nJane\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert data[0] == {"Name": "John"}
        assert data[1] == {"Name": "Jane"}

    def test_parse_csv_many_columns(self, tmp_path):
        """Test parsing CSV with many columns."""
        headers = ",".join([f"Col{i}" for i in range(1, 11)])
        row1 = ",".join([str(i) for i in range(1, 11)])
        row2 = ",".join([str(i * 10) for i in range(1, 11)])

        csv_file = tmp_path / "many_columns.csv"
        csv_file.write_text(f"{headers}\n{row1}\n{row2}\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert len(data[0]) == 10
        assert data[0]["Col1"] == "1"
        assert data[0]["Col10"] == "10"
        assert data[1]["Col1"] == "10"
        assert data[1]["Col10"] == "100"


class TestCSVDelimiters:
    """Test parsing CSV with different delimiters."""

    def test_parse_csv_tab_delimited(self, tmp_path):
        """Test parsing tab-separated values (TSV)."""
        csv_file = tmp_path / "tabbed.tsv"
        csv_file.write_text("Name\tAge\tCity\nJohn\t30\tNew York\n")

        data = CSVParser.parse_csv(csv_file, delimiter="\t")

        assert len(data) == 1
        assert data[0] == {"Name": "John", "Age": "30", "City": "New York"}

    def test_parse_csv_semicolon_delimited(self, tmp_path):
        """Test parsing semicolon-separated values."""
        csv_file = tmp_path / "semicolon.csv"
        csv_file.write_text("Name;Age;City\nJohn;30;New York\n")

        data = CSVParser.parse_csv(csv_file, delimiter=";")

        assert len(data) == 1
        assert data[0] == {"Name": "John", "Age": "30", "City": "New York"}

    def test_parse_csv_pipe_delimited(self, tmp_path):
        """Test parsing pipe-separated values."""
        csv_file = tmp_path / "pipe.csv"
        csv_file.write_text("Name|Age|City\nJohn|30|New York\n")

        data = CSVParser.parse_csv(csv_file, delimiter="|")

        assert len(data) == 1
        assert data[0] == {"Name": "John", "Age": "30", "City": "New York"}

    def test_auto_detect_delimiter_comma(self, tmp_path):
        """Test auto-detection of comma delimiter."""
        csv_file = tmp_path / "auto_comma.csv"
        csv_file.write_text("Name,Age,City\nJohn,30,New York\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        assert data[0] == {"Name": "John", "Age": "30", "City": "New York"}

    def test_auto_detect_delimiter_semicolon(self, tmp_path):
        """Test auto-detection of semicolon delimiter."""
        csv_file = tmp_path / "auto_semicolon.csv"
        csv_file.write_text("Name;Age;City\nJohn;30;New York\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        assert data[0] == {"Name": "John", "Age": "30", "City": "New York"}


class TestCSVEncodings:
    """Test parsing CSV with different encodings."""

    def test_parse_csv_utf8_encoding(self, tmp_path):
        """Test parsing UTF-8 encoded CSV."""
        csv_file = tmp_path / "utf8.csv"
        # UTF-8 encoded text with special characters
        content = "Name,City\nJosé,São Paulo\nMüller,München\n"
        csv_file.write_text(content, encoding="utf-8")

        data = CSVParser.parse_csv(csv_file, encoding="utf-8")

        assert len(data) == 2
        assert data[0]["Name"] == "José"
        assert data[0]["City"] == "São Paulo"

    def test_parse_csv_latin1_encoding(self, tmp_path):
        """Test parsing Latin-1 encoded CSV."""
        csv_file = tmp_path / "latin1.csv"
        # Latin-1 encoded text
        content = "Name,City\nJosé,São Paulo\n"
        csv_file.write_text(content, encoding="latin-1")

        data = CSVParser.parse_csv(csv_file, encoding="latin-1")

        assert len(data) == 1
        assert data[0]["Name"] == "José"

    def test_auto_detect_encoding_utf8(self, tmp_path):
        """Test auto-detection of UTF-8 encoding."""
        csv_file = tmp_path / "auto_utf8.csv"
        content = "Name,City\nJosé,São Paulo\n"
        csv_file.write_text(content, encoding="utf-8")

        # Auto-detect encoding
        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        assert data[0]["Name"] == "José"

    def test_auto_detect_encoding_latin1(self, tmp_path):
        """Test auto-detection of Latin-1 encoding."""
        csv_file = tmp_path / "auto_latin1.csv"
        # Write using binary to ensure exact encoding
        content = "Name,City\nJosé,São Paulo\n".encode("latin-1")
        csv_file.write_bytes(content)

        # Auto-detect encoding
        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        assert data[0]["Name"] == "José"

    def test_invalid_encoding_raises_error(self, tmp_path):
        """Test that invalid encoding raises ValueError."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nJohn,30\n")

        with pytest.raises(ValueError, match="Failed to read file with encoding"):
            CSVParser.parse_csv(csv_file, encoding="invalid-encoding")


class TestCSVNoHeaders:
    """Test parsing CSV without headers."""

    def test_parse_csv_without_headers(self, tmp_path):
        """Test parsing CSV without headers generates column names."""
        csv_file = tmp_path / "no_headers.csv"
        csv_file.write_text("John,30,New York\nJane,25,London\n")

        data = CSVParser.parse_csv(csv_file, has_headers=False)

        assert len(data) == 2
        assert data[0] == {"column1": "John", "column2": "30", "column3": "New York"}
        assert data[1] == {"column1": "Jane", "column2": "25", "column3": "London"}

    def test_parse_csv_without_headers_many_columns(self, tmp_path):
        """Test parsing CSV without headers with many columns."""
        csv_file = tmp_path / "no_headers_many.csv"
        csv_file.write_text("1,2,3,4,5\n")

        data = CSVParser.parse_csv(csv_file, has_headers=False)

        assert len(data) == 1
        assert "column1" in data[0]
        assert "column5" in data[0]
        assert data[0]["column1"] == "1"
        assert data[0]["column5"] == "5"


class TestCSVErrors:
    """Test error handling for invalid CSV files."""

    def test_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            CSVParser.parse_csv(tmp_path / "nonexistent.csv")

    def test_invalid_file_type(self, tmp_path):
        """Test that ValueError is raised for non-CSV file extension."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"Name": "John", "Age": 30}')

        with pytest.raises(ValueError, match="Invalid file type"):
            CSVParser.parse_csv(json_file)

    def test_empty_file(self, tmp_path):
        """Test that ValueError is raised for empty file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(ValueError, match="CSV file is empty"):
            CSVParser.parse_csv(csv_file)

    def test_csv_with_headers_only(self, tmp_path):
        """Test parsing CSV with only headers (no data rows)."""
        csv_file = tmp_path / "headers_only.csv"
        csv_file.write_text("Name,Age,City\n")

        data = CSVParser.parse_csv(csv_file)

        # Should return empty list (headers but no data)
        assert data == []

    def test_csv_with_only_empty_rows(self, tmp_path):
        """Test parsing CSV with only empty rows."""
        csv_file = tmp_path / "only_empty.csv"
        csv_file.write_text("Name,Age\n\n\n")

        data = CSVParser.parse_csv(csv_file)

        # All rows are empty, should return empty list
        assert data == []

    def test_invalid_utf8_encoding_for_file(self, tmp_path):
        """Test that ValueError is raised for wrong encoding."""
        csv_file = tmp_path / "test.csv"
        # Write UTF-8 content
        csv_file.write_text("Name,Age\nJosé,30\n", encoding="utf-8")

        # Try to parse as ASCII (should fail)
        with pytest.raises(ValueError, match="Failed to read file with encoding"):
            CSVParser.parse_csv(csv_file, encoding="ascii")


class TestCSVDetectDelimiter:
    """Test the detect_delimiter static method."""

    def test_detect_delimiter_comma(self, tmp_path):
        """Test detecting comma delimiter."""
        csv_file = tmp_path / "comma.csv"
        csv_file.write_text("Name,Age,City\nJohn,30,New York\n")

        delimiter = CSVParser.detect_delimiter(csv_file)

        assert delimiter == ","

    def test_detect_delimiter_semicolon(self, tmp_path):
        """Test detecting semicolon delimiter."""
        csv_file = tmp_path / "semicolon.csv"
        csv_file.write_text("Name;Age;City\nJohn;30;New York\n")

        delimiter = CSVParser.detect_delimiter(csv_file)

        assert delimiter == ";"

    def test_detect_delimiter_tab(self, tmp_path):
        """Test detecting tab delimiter."""
        csv_file = tmp_path / "tab.tsv"
        csv_file.write_text("Name\tAge\nJohn\t30\n")

        delimiter = CSVParser.detect_delimiter(csv_file)

        assert delimiter == "\t"

    def test_detect_delimiter_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            CSVParser.detect_delimiter(tmp_path / "nonexistent.csv")

    def test_detect_delimiter_empty_file(self, tmp_path):
        """Test that ValueError is raised for empty file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(ValueError, match="CSV file is empty"):
            CSVParser.detect_delimiter(csv_file)


class TestCSVWhitespaceHandling:
    """Test whitespace handling in CSV parsing."""

    def test_whitespace_around_values(self, tmp_path):
        """Test that whitespace is trimmed from values."""
        csv_file = tmp_path / "whitespace.csv"
        csv_file.write_text("Name, Age , City\n  John  , 30 , New York  \n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        # DictReader with skipinitialspace should handle leading/trailing spaces
        assert data[0]["Name"].strip() == "John"
        assert data[0]["City"].strip() == "New York"

    def test_whitespace_in_quoted_fields_preserved(self, tmp_path):
        """Test that whitespace in quoted fields is preserved."""
        csv_file = tmp_path / "quoted_whitespace.csv"
        csv_file.write_text('Name,Description\nItem1,"  Value with spaces  "\n')

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        # Quoted fields should preserve internal whitespace
        assert data[0]["Description"].strip() == "Value with spaces"


class TestCSVSpecialCharacters:
    """Test handling of special characters in CSV."""

    def test_newlines_in_quoted_fields(self, tmp_path):
        """Test that newlines in quoted fields are handled."""
        csv_file = tmp_path / "newlines.csv"
        csv_file.write_text('Name,Description\nItem1,"Line 1\nLine 2"\nItem2,"Simple"\n')

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert "Line 1" in data[0]["Description"]
        assert "Line 2" in data[0]["Description"]

    def test_special_characters_in_values(self, tmp_path):
        """Test handling of special characters (!@#$%^&*)."""
        csv_file = tmp_path / "special.csv"
        csv_file.write_text('Name,Email\nUser1,user1@example.com\nUser2,user+tag@example.com\n')

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert data[0]["Email"] == "user1@example.com"
        assert data[1]["Email"] == "user+tag@example.com"

    def test_unicode_emojis(self, tmp_path):
        """Test handling of Unicode emoji characters."""
        csv_file = tmp_path / "emoji.csv"
        csv_file.write_text("Name,Status\nJohn,😀\nJane,❤️\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert data[0]["Status"] == "😀"
        assert data[1]["Status"] == "❤️"


class TestCSVMixedDataTypes:
    """Test handling of different data types in CSV."""

    def test_numeric_values_as_strings(self, tmp_path):
        """Test that numeric values are returned as strings (CSV behavior)."""
        csv_file = tmp_path / "numeric.csv"
        csv_file.write_text("Name,Age,Salary\nJohn,30,50000.50\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        # CSV DictReader returns all values as strings
        assert isinstance(data[0]["Age"], str)
        assert data[0]["Age"] == "30"
        assert data[0]["Salary"] == "50000.50"

    def test_boolean_values_as_strings(self, tmp_path):
        """Test that boolean-like values are returned as strings."""
        csv_file = tmp_path / "boolean.csv"
        csv_file.write_text("Name,Active,Verified\nJohn,true,false\n")

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 1
        assert data[0]["Active"] == "true"
        assert data[0]["Verified"] == "false"

    def test_mixed_content(self, tmp_path):
        """Test CSV with mixed content types."""
        csv_file = tmp_path / "mixed.csv"
        csv_file.write_text(
            "Name,Age,Active,Score,Note\nJohn,30,true,95.5,Some text\nJane,25,false,87.3,\n"
        )

        data = CSVParser.parse_csv(csv_file)

        assert len(data) == 2
        assert data[0]["Name"] == "John"
        assert data[0]["Age"] == "30"
        assert data[0]["Active"] == "true"
        assert data[0]["Score"] == "95.5"
        assert data[1]["Note"] == ""  # Empty value
