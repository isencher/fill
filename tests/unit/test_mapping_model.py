"""
Unit tests for Mapping Model.

Tests cover field validation, constraints, edge cases,
and Pydantic configuration.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from src.models.mapping import Mapping


class TestMappingCreation:
    """Test Mapping initialization and basic creation."""

    def test_create_mapping_with_required_fields(self):
        """Test creating mapping with required fields only."""
        mapping = Mapping(
            file_id="file-123",
            template_id="template-456",
        )

        assert mapping.file_id == "file-123"
        assert mapping.template_id == "template-456"
        assert mapping.column_mappings == {}
        assert isinstance(mapping.id, str)
        assert isinstance(mapping.created_at, datetime)

    def test_create_mapping_with_column_mappings(self):
        """Test creating mapping with column mappings."""
        mapping = Mapping(
            file_id="file-123",
            template_id="template-456",
            column_mappings={
                "Customer Name": "customer_name",
                "Invoice Date": "invoice_date",
            },
        )

        assert len(mapping.column_mappings) == 2
        assert mapping.column_mappings["Customer Name"] == "customer_name"
        assert mapping.column_mappings["Invoice Date"] == "invoice_date"

    def test_create_mapping_with_empty_mappings(self):
        """Test creating mapping with empty mappings dict."""
        mapping = Mapping(
            file_id="file-123",
            template_id="template-456",
            column_mappings={},
        )

        assert mapping.column_mappings == {}

    def test_create_mapping_generates_unique_id(self):
        """Test that each mapping gets a unique ID."""
        mapping1 = Mapping(file_id="f1", template_id="t1")
        mapping2 = Mapping(file_id="f2", template_id="t2")

        assert mapping1.id != mapping2.id

    def test_create_mapping_generates_timestamp(self):
        """Test that mapping gets created_at timestamp."""
        before = datetime.now(timezone.utc)
        mapping = Mapping(file_id="f1", template_id="t1")
        after = datetime.now(timezone.utc)

        assert before <= mapping.created_at <= after


class TestFileIdValidation:
    """Test file_id field validation."""

    def test_file_id_with_leading_trailing_whitespace(self):
        """Test that file_id is trimmed."""
        mapping = Mapping(
            file_id="  file-123  ",
            template_id="template-456",
        )

        assert mapping.file_id == "file-123"

    def test_file_id_empty_raises_error(self):
        """Test that empty file_id raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(file_id="", template_id="t1")

    def test_file_id_whitespace_only_raises_error(self):
        """Test that whitespace-only file_id raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(file_id="   ", template_id="t1")

    def test_file_id_none_raises_error(self):
        """Test that None file_id raises validation error."""
        with pytest.raises(Exception):
            Mapping(file_id=None, template_id="t1")  # type: ignore


class TestTemplateIdValidation:
    """Test template_id field validation."""

    def test_template_id_with_leading_trailing_whitespace(self):
        """Test that template_id is trimmed."""
        mapping = Mapping(
            file_id="file-123",
            template_id="  template-456  ",
        )

        assert mapping.template_id == "template-456"

    def test_template_id_empty_raises_error(self):
        """Test that empty template_id raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(file_id="f1", template_id="")

    def test_template_id_whitespace_only_raises_error(self):
        """Test that whitespace-only template_id raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(file_id="f1", template_id="   ")

    def test_template_id_none_raises_error(self):
        """Test that None template_id raises validation error."""
        with pytest.raises(Exception):
            Mapping(file_id="f1", template_id=None)  # type: ignore


class TestColumnMappingsValidation:
    """Test column_mappings field validation."""

    def test_column_mappings_trims_whitespace(self):
        """Test that column and placeholder names are trimmed."""
        mapping = Mapping(
            file_id="f1",
            template_id="t1",
            column_mappings={
                "  Column Name  ": "  placeholder_name  ",
                "Another": "value",
            },
        )

        assert mapping.column_mappings == {
            "Column Name": "placeholder_name",
            "Another": "value",
        }

    def test_column_mappings_non_dict_raises_error(self):
        """Test that non-dict column_mappings raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings="not a dict",  # type: ignore
            )

    def test_column_mappings_empty_column_name_raises_error(self):
        """Test that empty column name raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings={"": "placeholder"},
            )

    def test_column_mappings_whitespace_only_column_name_raises_error(self):
        """Test that whitespace-only column name raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings={"   ": "placeholder"},
            )

    def test_column_mappings_non_string_column_name_raises_error(self):
        """Test that non-string column name raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings={123: "placeholder"},  # type: ignore
            )

    def test_column_mappings_empty_placeholder_name_raises_error(self):
        """Test that empty placeholder name raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings={"column": ""},
            )

    def test_column_mappings_whitespace_only_placeholder_name_raises_error(self):
        """Test that whitespace-only placeholder name raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings={"column": "   "},
            )

    def test_column_mappings_non_string_placeholder_name_raises_error(self):
        """Test that non-string placeholder name raises ValueError."""
        with pytest.raises(ValueError):
            Mapping(
                file_id="f1",
                template_id="t1",
                column_mappings={"column": 123},  # type: ignore
            )

    def test_column_mappings_multiple_entries(self):
        """Test column mappings with multiple entries."""
        mapping = Mapping(
            file_id="f1",
            template_id="t1",
            column_mappings={
                "col1": "placeholder1",
                "col2": "placeholder2",
                "col3": "placeholder3",
                "col4": "placeholder4",
                "col5": "placeholder5",
            },
        )

        assert len(mapping.column_mappings) == 5
        assert mapping.column_mappings["col1"] == "placeholder1"
        assert mapping.column_mappings["col5"] == "placeholder5"

    def test_column_mappings_with_special_characters(self):
        """Test column mappings with special characters in names."""
        mapping = Mapping(
            file_id="f1",
            template_id="t1",
            column_mappings={
                "Customer Name (Full)": "customer_name_full",
                "Invoice-Date": "invoice_date",
                "Total_Amount": "total_amount",
            },
        )

        assert len(mapping.column_mappings) == 3
        assert mapping.column_mappings["Customer Name (Full)"] == "customer_name_full"
        assert mapping.column_mappings["Invoice-Date"] == "invoice_date"
        assert mapping.column_mappings["Total_Amount"] == "total_amount"


class TestSerialization:
    """Test model serialization and deserialization."""

    def test_model_dump_json(self):
        """Test exporting model to dictionary."""
        mapping = Mapping(
            file_id="file-123",
            template_id="template-456",
            column_mappings={"Column": "placeholder"},
        )

        data = mapping.model_dump_json()

        assert data["file_id"] == "file-123"
        assert data["template_id"] == "template-456"
        assert data["column_mappings"] == {"Column": "placeholder"}
        assert "id" in data
        assert "created_at" in data

    def test_model_validate_json(self):
        """Test creating Mapping from dictionary."""
        data = {
            "file_id": "file-123",
            "template_id": "template-456",
            "column_mappings": {"Column": "placeholder"},
        }

        mapping = Mapping.model_validate_json(data)

        assert mapping.file_id == "file-123"
        assert mapping.template_id == "template-456"
        assert mapping.column_mappings == {"Column": "placeholder"}

    def test_model_validate_json_with_invalid_data(self):
        """Test that invalid dictionary raises ValueError."""
        data = {
            "file_id": "",  # Empty file_id
            "template_id": "template-456",
        }

        with pytest.raises(ValueError):
            Mapping.model_validate_json(data)


class TestPydanticConfig:
    """Test Pydantic model configuration."""

    def test_validate_assignment_enabled(self):
        """Test that assignment validation works."""
        mapping = Mapping(file_id="f1", template_id="t1")

        # Valid assignment should work
        mapping.file_id = "new-file-id"
        assert mapping.file_id == "new-file-id"

        # Invalid assignment should raise error
        with pytest.raises(ValueError):
            mapping.file_id = ""

    def test_use_enum_values(self):
        """Test that enum values configuration is set."""
        # In Pydantic v2, we use model_config instead of Config
        # Check that model_config exists and has use_enum_values
        assert hasattr(Mapping, "model_config")
        assert Mapping.model_config.get("use_enum_values") is True


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_mapping_with_very_long_names(self):
        """Test mapping with very long column and placeholder names."""
        long_name = "a" * 1000

        mapping = Mapping(
            file_id="f1",
            template_id="t1",
            column_mappings={long_name: long_name},
        )

        assert len(mapping.column_mappings) == 1
        assert long_name in mapping.column_mappings

    def test_mapping_with_unicode_characters(self):
        """Test mapping with Unicode characters."""
        mapping = Mapping(
            file_id="f1",
            template_id="t1",
            column_mappings={
                "客户名": "customer_name",
                "日期": "date",
                "金額": "amount",
            },
        )

        assert len(mapping.column_mappings) == 3
        assert mapping.column_mappings["客户名"] == "customer_name"
        assert mapping.column_mappings["日期"] == "date"
        assert mapping.column_mappings["金額"] == "amount"

    def test_mapping_preserves_insertion_order(self):
        """Test that mapping preserves column insertion order (Python 3.7+)."""
        mapping = Mapping(
            file_id="f1",
            template_id="t1",
            column_mappings={
                "z": "placeholder_z",
                "a": "placeholder_a",
                "m": "placeholder_m",
            },
        )

        # Python 3.7+ preserves dict insertion order
        keys = list(mapping.column_mappings.keys())
        assert keys == ["z", "a", "m"]
