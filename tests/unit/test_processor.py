"""
Unit tests for core Processor module.

Tests the main data processing logic.
"""

import pytest

from src.core.processor import Processor


class TestProcessor:
    """Test Processor class functionality."""

    def test_processor_initialization(self):
        """Test that Processor can be initialized."""
        processor = Processor()
        assert processor is not None

    def test_process_string_uppercase(self):
        """Test processing a string returns uppercase."""
        processor = Processor()
        result = processor.process("hello")
        assert result == "HELLO"

    def test_process_empty_string(self):
        """Test processing an empty string."""
        processor = Processor()
        result = processor.process("")
        assert result == ""

    def test_process_already_uppercase(self):
        """Test processing already uppercase string."""
        processor = Processor()
        result = processor.process("HELLO")
        assert result == "HELLO"

    def test_process_with_numbers(self):
        """Test processing string with numbers."""
        processor = Processor()
        result = processor.process("hello123")
        assert result == "HELLO123"

    def test_process_with_special_characters(self):
        """Test processing string with special characters."""
        processor = Processor()
        result = processor.process("hello_world!")
        assert result == "HELLO_WORLD!"

    def test_process_unicode(self):
        """Test processing unicode characters."""
        processor = Processor()
        result = processor.process("héllo")
        assert result == "HÉLLO"
