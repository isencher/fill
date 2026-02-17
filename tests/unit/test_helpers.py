"""
Unit tests for utility helpers module.

Tests common utility functions used across the application.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.utils import helpers


class TestFileHelpers:
    """Test file-related helper functions."""

    def test_ensure_directory_creates_directory(self):
        """Test that ensure_directory creates a directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "subdir" / "nested"
            assert not test_dir.exists()
            
            helpers.ensure_directory(str(test_dir))
            
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_ensure_directory_existing_directory(self):
        """Test that ensure_directory works with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_dir = Path(tmpdir)
            assert existing_dir.exists()
            
            # Should not raise error
            helpers.ensure_directory(str(existing_dir))
            
            assert existing_dir.exists()

    def test_get_file_extension(self):
        """Test extracting file extension."""
        assert helpers.get_file_extension("test.csv") == "csv"
        assert helpers.get_file_extension("test.xlsx") == "xlsx"
        assert helpers.get_file_extension("test.docx") == "docx"
        assert helpers.get_file_extension("TEST.CSV") == "csv"  # Case insensitive

    def test_get_file_extension_no_extension(self):
        """Test extracting extension from file without extension."""
        assert helpers.get_file_extension("README") == ""
        assert helpers.get_file_extension("Makefile") == ""

    def test_safe_filename(self):
        """Test making filenames safe."""
        assert helpers.safe_filename("test file.csv") == "test_file.csv"
        assert helpers.safe_filename("test/../file.csv") == "test_file.csv"
        assert helpers.safe_filename("test<file>.csv") == "test_file_.csv"


class TestStringHelpers:
    """Test string-related helper functions."""

    def test_truncate_string(self):
        """Test string truncation."""
        assert helpers.truncate_string("hello world", 5) == "he..."
        assert helpers.truncate_string("hello", 10) == "hello"
        assert helpers.truncate_string("", 5) == ""

    def test_slugify(self):
        """Test converting string to slug."""
        assert helpers.slugify("Hello World") == "hello-world"
        assert helpers.slugify("Test File Name") == "test-file-name"
        assert helpers.slugify("UPPER CASE") == "upper-case"

    def test_slugify_special_chars(self):
        """Test slugify with special characters."""
        assert helpers.slugify("Hello & World!") == "hello-world"
        assert helpers.slugify("Test--File") == "test-file"


class TestValidationHelpers:
    """Test validation helper functions."""

    def test_is_valid_email(self):
        """Test email validation."""
        assert helpers.is_valid_email("test@example.com") is True
        assert helpers.is_valid_email("user.name@domain.co.uk") is True
        assert helpers.is_valid_email("invalid") is False
        assert helpers.is_valid_email("@example.com") is False
        assert helpers.is_valid_email("") is False

    def test_is_valid_uuid(self):
        """Test UUID validation."""
        assert helpers.is_valid_uuid("550e8400-e29b-41d4-a716-446655440000") is True
        assert helpers.is_valid_uuid("not-a-uuid") is False
        assert helpers.is_valid_uuid("") is False


class TestDataHelpers:
    """Test data manipulation helpers."""

    def test_chunk_list(self):
        """Test splitting list into chunks."""
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        chunks = list(helpers.chunk_list(items, 3))
        
        assert len(chunks) == 4  # 3+3+3+1
        assert chunks[0] == [1, 2, 3]
        assert chunks[1] == [4, 5, 6]
        assert chunks[2] == [7, 8, 9]
        assert chunks[3] == [10]

    def test_chunk_list_empty(self):
        """Test chunking empty list."""
        chunks = list(helpers.chunk_list([], 3))
        assert chunks == []

    def test_merge_dicts(self):
        """Test merging dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = helpers.merge_dicts(dict1, dict2)
        
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_dicts_empty(self):
        """Test merging with empty dict."""
        dict1 = {"a": 1}
        result = helpers.merge_dicts(dict1, {})
        assert result == {"a": 1}


class TestPathHelpers:
    """Test path-related helper functions."""

    def test_join_paths(self):
        """Test joining paths safely."""
        result = helpers.join_paths("/base", "subdir", "file.txt")
        assert result == "/base/subdir/file.txt"

    def test_get_relative_path(self):
        """Test getting relative path."""
        result = helpers.get_relative_path("/base/subdir/file.txt", "/base")
        assert result == "subdir/file.txt"

    def test_normalize_path(self):
        """Test path normalization."""
        result = helpers.normalize_path("/base/../other/./file.txt")
        assert result == "/other/file.txt"
