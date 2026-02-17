"""
Unit tests for Mapping Validation Service.

Tests cover mapping validation, placeholder checking,
column validation, and error handling.
"""

import pytest

from src.models.mapping import Mapping
from src.models.template import Template
from src.services.mapping_validator import (
    MappingValidationError,
    MappingValidator,
    validate_mapping,
)
from src.services.template_store import get_template_store


class TestMappingValidationError:
    """Test MappingValidationError custom exception."""

    def test_create_error_with_message_and_errors(self):
        """Test creating error with message and errors."""
        error = MappingValidationError(
            message="Validation failed",
            errors=["Error 1", "Error 2"]
        )

        assert str(error) == "Validation failed"
        assert error.message == "Validation failed"
        assert error.errors == ["Error 1", "Error 2"]

    def test_error_is_exception(self):
        """Test that error is an exception."""
        error = MappingValidationError(
            message="Test",
            errors=[]
        )

        assert isinstance(error, Exception)
        assert isinstance(error, BaseException)


class TestValidatePlaceholdersMapped:
    """Test _validate_placeholders_mapped method."""

    def setup_method(self):
        """Set up test template store before each test."""
        store = get_template_store()
        store.clear()

    def test_all_placeholders_mapped_passes(self):
        """Test validation passes when all placeholders are mapped."""
        # Create template with placeholders
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount", "date"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        # Create mapping with all placeholders mapped
        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Customer Name": "customer",
                "Total Amount": "amount",
                "Invoice Date": "date",
            },
        )

        validator = MappingValidator()
        errors = validator._validate_placeholders_mapped(template, mapping)

        assert errors == []

    def test_missing_placeholder_fails(self):
        """Test validation fails when placeholder is missing."""
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount", "date"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        # Create mapping missing "date" placeholder
        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Customer Name": "customer",
                "Total Amount": "amount",
                # Missing "date" mapping
            },
        )

        validator = MappingValidator()
        errors = validator._validate_placeholders_mapped(template, mapping)

        assert len(errors) == 1
        assert "date" in errors[0]

    def test_multiple_missing_placeholders_fails(self):
        """Test validation fails with multiple missing placeholders."""
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount", "date", "invoice_id"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        # Create mapping missing two placeholders
        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Customer Name": "customer",
                # Missing "amount", "date", "invoice_id"
            },
        )

        validator = MappingValidator()
        errors = validator._validate_placeholders_mapped(template, mapping)

        assert len(errors) == 3

    def test_extra_mapping_ignores(self):
        """Test extra mappings (not in template) don't cause errors."""
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        # Create mapping with extra placeholder
        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Customer Name": "customer",
                "Total Amount": "amount",
                "Extra Field": "extra_not_in_template",  # Not in template
            },
        )

        validator = MappingValidator()
        errors = validator._validate_placeholders_mapped(template, mapping)

        # Extra mappings don't cause errors in this validation
        # (only checks that required placeholders are mapped)
        assert errors == []

    def test_template_with_no_placeholders_passes(self):
        """Test validation passes when template has no placeholders."""
        template = Template(
            name="Simple",
            placeholders=[],  # No placeholders
            file_path="/simple.docx"
        )
        store = get_template_store()
        store.save_template(template)

        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={},
        )

        validator = MappingValidator()
        errors = validator._validate_placeholders_mapped(template, mapping)

        assert errors == []


class TestValidateColumnsExist:
    """Test _validate_columns_exist method."""

    def test_all_columns_exist_passes(self):
        """Test validation passes when all columns exist in data."""
        mapping = Mapping(
            file_id="file-1",
            template_id="template-1",
            column_mappings={
                "Column A": "placeholder_a",
                "Column B": "placeholder_b",
                "Column C": "placeholder_c",
            },
        )

        data_columns = ["Column A", "Column B", "Column C", "Column D"]

        validator = MappingValidator()
        errors = validator._validate_columns_exist(mapping, data_columns)

        assert errors == []

    def test_missing_column_fails(self):
        """Test validation fails when column doesn't exist in data."""
        mapping = Mapping(
            file_id="file-1",
            template_id="template-1",
            column_mappings={
                "Column A": "placeholder_a",
                "Column B": "placeholder_b",
                "Missing Column": "placeholder_c",
            },
        )

        data_columns = ["Column A", "Column B"]

        validator = MappingValidator()
        errors = validator._validate_columns_exist(mapping, data_columns)

        assert len(errors) == 1
        assert "Missing Column" in errors[0]

    def test_multiple_missing_columns_fails(self):
        """Test validation fails with multiple missing columns."""
        mapping = Mapping(
            file_id="file-1",
            template_id="template-1",
            column_mappings={
                "Missing A": "placeholder_a",
                "Column B": "placeholder_b",
                "Missing C": "placeholder_c",
            },
        )

        data_columns = ["Column B"]

        validator = MappingValidator()
        errors = validator._validate_columns_exist(mapping, data_columns)

        assert len(errors) == 2

    def test_case_sensitivity_in_columns(self):
        """Test that column names are case-sensitive."""
        mapping = Mapping(
            file_id="file-1",
            template_id="template-1",
            column_mappings={
                "Column A": "placeholder_a",
            },
        )

        data_columns = ["column a", "column b"]  # Lowercase

        validator = MappingValidator()
        errors = validator._validate_columns_exist(mapping, data_columns)

        # Case-sensitive: "Column A" != "column a"
        assert len(errors) == 1
        assert "Column A" in errors[0]

    def test_empty_mapping_with_data_passes(self):
        """Test validation passes with empty mapping."""
        mapping = Mapping(
            file_id="file-1",
            template_id="template-1",
            column_mappings={},
        )

        data_columns = ["Column A", "Column B"]

        validator = MappingValidator()
        errors = validator._validate_columns_exist(mapping, data_columns)

        assert errors == []


class TestMappingValidatorValidate:
    """Test validate method with full validation."""

    def setup_method(self):
        """Set up test template store before each test."""
        store = get_template_store()
        store.clear()

    def test_valid_mapping_passes(self):
        """Test that valid mapping passes validation."""
        # Create template
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        # Create valid mapping
        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Customer Name": "customer",
                "Total Amount": "amount",
            },
        )

        data_columns = ["Customer Name", "Total Amount", "Date"]

        validator = MappingValidator()
        # Should not raise
        validator.validate(mapping, data_columns)

    def test_missing_template_fails(self):
        """Test that nonexistent template fails validation."""
        mapping = Mapping(
            file_id="file-1",
            template_id="nonexistent-template-id",
            column_mappings={},
        )

        data_columns = ["Column A"]

        validator = MappingValidator()

        with pytest.raises(MappingValidationError) as exc_info:
            validator.validate(mapping, data_columns)

        # Check that there's at least one error about template not found
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("not found" in err.lower() or "not found" in err.lower() for err in errors)

    def test_missing_placeholder_fails(self):
        """Test that missing placeholder mapping fails validation."""
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount", "date"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        # Missing "date" mapping
        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Customer Name": "customer",
                "Total Amount": "amount",
            },
        )

        data_columns = ["Customer Name", "Total Amount"]

        validator = MappingValidator()

        with pytest.raises(MappingValidationError) as exc_info:
            validator.validate(mapping, data_columns)

        errors = exc_info.value.errors
        assert len(errors) == 1
        assert "date" in errors[0]

    def test_missing_column_fails(self):
        """Test that missing column fails validation."""
        template = Template(
            name="Invoice",
            placeholders=["customer"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Missing Column": "customer",
            },
        )

        data_columns = ["Other Column"]  # Missing "Missing Column"

        validator = MappingValidator()

        with pytest.raises(MappingValidationError) as exc_info:
            validator.validate(mapping, data_columns)

        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Missing Column" in e for e in errors)

    def test_multiple_errors_fails(self):
        """Test that multiple validation errors are reported."""
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount", "date"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={
                "Missing Col 1": "customer",
                "Missing Col 2": "amount",
                # Missing "date" mapping
            },
        )

        data_columns = ["Other Column"]  # None of the mapped columns exist

        validator = MappingValidator()

        with pytest.raises(MappingValidationError) as exc_info:
            validator.validate(mapping, data_columns)

        errors = exc_info.value.errors
        # Should have errors for:
        # - Missing "date" placeholder
        # - "Missing Col 1" not in data
        # - "Missing Col 2" not in data
        assert len(errors) == 3


class TestValidateMappingConvenienceFunction:
    """Test validate_mapping convenience function."""

    def setup_method(self):
        """Set up test template store before each test."""
        store = get_template_store()
        store.clear()

    def test_valid_mapping_passes(self):
        """Test that convenience function works for valid mapping."""
        template = Template(
            name="Invoice",
            placeholders=["customer"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={"Column": "customer"},
        )

        data_columns = ["Column"]

        # Should not raise
        validate_mapping(mapping, data_columns)

    def test_invalid_mapping_fails(self):
        """Test that convenience function raises on invalid mapping."""
        template = Template(
            name="Invoice",
            placeholders=["customer"],
            file_path="/invoice.docx"
        )
        store = get_template_store()
        store.save_template(template)

        mapping = Mapping(
            file_id="file-1",
            template_id=template.id,
            column_mappings={"Missing": "customer"},
        )

        data_columns = ["Column"]

        with pytest.raises(MappingValidationError):
            validate_mapping(mapping, data_columns)
