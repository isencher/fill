"""
Unit tests for Template Model.

Tests cover Template model validation, field constraints, and edge cases.
"""

import pytest

from src.models.template import Template


class TestTemplateCreation:
    """Test basic Template creation and default values."""

    def test_create_template_with_required_fields_only(self):
        """Test creating template with only required fields."""
        template = Template(
            name="Invoice Template",
            file_path="/templates/invoice.docx",
        )

        assert template.name == "Invoice Template"
        assert template.file_path == "/templates/invoice.docx"
        assert template.description is None
        assert template.placeholders == []
        assert isinstance(template.id, str)
        assert len(template.id) > 0

    def test_create_template_with_all_fields(self):
        """Test creating template with all fields."""
        template = Template(
            name="Invoice Template",
            description="Standard invoice template",
            placeholders=["customer_name", "invoice_date", "total_amount"],
            file_path="/templates/invoice.docx",
        )

        assert template.name == "Invoice Template"
        assert template.description == "Standard invoice template"
        assert template.placeholders == ["customer_name", "invoice_date", "total_amount"]
        assert template.file_path == "/templates/invoice.docx"

    def test_template_id_is_unique(self):
        """Test that each template gets a unique ID."""
        template1 = Template(name="T1", file_path="/t1.docx")
        template2 = Template(name="T2", file_path="/t2.docx")

        assert template1.id != template2.id

    def test_template_created_at_is_set(self):
        """Test that created_at timestamp is set."""
        from datetime import datetime

        template = Template(name="Test", file_path="/test.docx")

        assert isinstance(template.created_at, datetime)
        assert template.created_at <= datetime.utcnow()


class TestTemplateNameValidation:
    """Test template name validation."""

    def test_name_cannot_be_empty(self):
        """Test that empty name raises ValidationError."""
        with pytest.raises(ValueError, match="name"):
            Template(name="", file_path="/test.docx")

    def test_name_cannot_be_whitespace_only(self):
        """Test that whitespace-only name raises ValidationError."""
        with pytest.raises(ValueError, match="name"):
            Template(name="   ", file_path="/test.docx")

    def test_name_trims_whitespace(self):
        """Test that leading/trailing whitespace is trimmed."""
        template = Template(name="  Invoice Template  ", file_path="/test.docx")

        assert template.name == "Invoice Template"
        # Note: Pydantic validation may preserve single internal spaces

    def test_name_max_length(self):
        """Test that name max length is 200 characters."""
        # 200 characters should work
        name_200 = "a" * 200
        template = Template(name=name_200, file_path="/test.docx")
        assert len(template.name) == 200

        # 201 characters should fail
        name_201 = "a" * 201
        with pytest.raises(ValueError):
            Template(name=name_201, file_path="/test.docx")

    def test_name_min_length(self):
        """Test that name min length is 1 character."""
        template = Template(name="A", file_path="/test.docx")
        assert template.name == "A"


class TestTemplateDescriptionValidation:
    """Test template description validation."""

    def test_description_is_optional(self):
        """Test that description can be omitted."""
        template = Template(name="Test", file_path="/test.docx")
        assert template.description is None

    def test_description_can_be_empty_string(self):
        """Test that empty string becomes None."""
        template = Template(name="Test", description="", file_path="/test.docx")
        assert template.description is None

    def test_description_trims_whitespace(self):
        """Test that whitespace-only description becomes None."""
        template = Template(name="Test", description="   ", file_path="/test.docx")
        assert template.description is None

    def test_description_trims_leading_trailing_whitespace(self):
        """Test that description trims leading/trailing whitespace."""
        template = Template(
            name="Test",
            description="  Standard invoice template  ",
            file_path="/test.docx",
        )

        assert template.description == "Standard invoice template"

    def test_description_max_length(self):
        """Test that description max length is 1000 characters."""
        # 1000 characters should work
        desc_1000 = "a" * 1000
        template = Template(name="Test", description=desc_1000, file_path="/test.docx")
        assert len(template.description) == 1000

        # 1001 characters should fail
        desc_1001 = "a" * 1001
        with pytest.raises(ValueError):
            Template(name="Test", description=desc_1001, file_path="/test.docx")


class TestTemplatePlaceholdersValidation:
    """Test template placeholder validation."""

    def test_placeholders_default_to_empty_list(self):
        """Test that placeholders default to empty list."""
        template = Template(name="Test", file_path="/test.docx")
        assert template.placeholders == []

    def test_placeholders_must_be_unique(self):
        """Test that duplicate placeholders raise ValidationError."""
        with pytest.raises(ValueError, match="Duplicate placeholder"):
            Template(
                name="Test",
                placeholders=["name", "name"],
                file_path="/test.docx",
            )

    def test_placeholders_case_insensitive_duplicate(self):
        """Test that case-insensitive duplicates raise ValidationError."""
        with pytest.raises(ValueError, match="Duplicate placeholder"):
            Template(
                name="Test",
                placeholders=["name", "Name", "NAME"],
                file_path="/test.docx",
            )

    def test_placeholders_cannot_be_empty(self):
        """Test that empty string placeholder raises ValidationError."""
        with pytest.raises(ValueError, match="Placeholder cannot be empty"):
            Template(
                name="Test",
                placeholders=["name", ""],
                file_path="/test.docx",
            )

    def test_placeholders_cannot_be_whitespace_only(self):
        """Test that whitespace-only placeholder raises ValidationError."""
        with pytest.raises(ValueError, match="Placeholder cannot be empty"):
            Template(
                name="Test",
                placeholders=["name", "  "],
                file_path="/test.docx",
            )

    def test_placeholders_trim_whitespace(self):
        """Test that placeholders trim whitespace."""
        template = Template(
            name="Test",
            placeholders=[" name ", " age "],
            file_path="/test.docx",
        )

        assert template.placeholders == ["name", "age"]

    def test_placeholders_valid_characters(self):
        """Test that valid characters work in placeholders."""
        # Alphanumeric, underscore, hyphen
        template = Template(
            name="Test",
            placeholders=[
                "name",
                "first_name",
                "last-name",
                "name123",
                "customer_name_2024",
            ],
            file_path="/test.docx",
        )

        assert len(template.placeholders) == 5

    def test_placeholders_invalid_characters(self):
        """Test that invalid characters raise ValidationError."""
        # Spaces are not allowed
        with pytest.raises(ValueError, match="Invalid placeholder"):
            Template(
                name="Test",
                placeholders=["customer name"],
                file_path="/test.docx",
            )

        # Special characters are not allowed
        with pytest.raises(ValueError, match="Invalid placeholder"):
            Template(
                name="Test",
                placeholders=["name@domain"],
                file_path="/test.docx",
            )

        # Dots are not allowed
        with pytest.raises(ValueError, match="Invalid placeholder"):
            Template(
                name="Test",
                placeholders=["first.name"],
                file_path="/test.docx",
            )

    def test_placeholders_many_valid(self):
        """Test template with many placeholders."""
        placeholders = [f"field_{i}" for i in range(100)]
        template = Template(
            name="Test",
            placeholders=placeholders,
            file_path="/test.docx",
        )

        assert len(template.placeholders) == 100
        assert template.placeholders[0] == "field_0"
        assert template.placeholders[99] == "field_99"


class TestTemplateFilePathValidation:
    """Test template file path validation."""

    def test_file_path_cannot_be_empty(self):
        """Test that empty file path raises ValidationError."""
        with pytest.raises(ValueError):  # Pydantic raises ValidationError
            Template(name="Test", file_path="")

    def test_file_path_cannot_be_whitespace_only(self):
        """Test that whitespace-only file path raises ValidationError."""
        with pytest.raises(ValueError, match="file path"):
            Template(name="Test", file_path="   ")

    def test_file_path_trims_whitespace(self):
        """Test that file path trims whitespace."""
        template = Template(name="Test", file_path="  /templates/test.docx  ")

        assert template.file_path == "/templates/test.docx"

    def test_file_path_with_directory(self):
        """Test that file path works with directories."""
        template = Template(
            name="Test",
            file_path="/templates/invoices/standard.docx",
        )

        assert "invoices" in template.file_path

    def test_file_path_relative_path(self):
        """Test that relative file paths work."""
        template = Template(name="Test", file_path="templates/test.docx")

        assert template.file_path == "templates/test.docx"


class TestTemplateSerialization:
    """Test Template serialization and deserialization."""

    def test_model_dump_json(self):
        """Test exporting template to dictionary."""
        template = Template(
            id="test-id",
            name="Test Template",
            description="Test description",
            placeholders=["field1", "field2"],
            file_path="/test.docx",
        )

        data = template.model_dump_json()

        assert data["id"] == "test-id"
        assert data["name"] == "Test Template"
        assert data["description"] == "Test description"
        assert data["placeholders"] == ["field1", "field2"]
        assert data["file_path"] == "/test.docx"
        assert "created_at" in data

    def test_model_validate_json(self):
        """Test creating template from dictionary."""
        data = {
            "id": "test-id",
            "name": "Test Template",
            "description": "Test description",
            "placeholders": ["field1", "field2"],
            "file_path": "/test.docx",
        }

        template = Template.model_validate_json(data)

        assert template.id == "test-id"
        assert template.name == "Test Template"
        assert template.description == "Test description"
        assert template.placeholders == ["field1", "field2"]
        assert template.file_path == "/test.docx"

    def test_model_validate_json_with_missing_fields(self):
        """Test that missing required fields raise ValidationError."""
        # Missing name
        data = {"file_path": "/test.docx"}
        with pytest.raises(ValueError):
            Template.model_validate_json(data)

        # Missing file_path
        data = {"name": "Test"}
        with pytest.raises(ValueError):
            Template.model_validate_json(data)


class TestTemplateEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_template_with_many_placeholders(self):
        """Test template with large number of placeholders."""
        placeholders = [f"placeholder_{i}" for i in range(1000)]
        template = Template(
            name="Test",
            placeholders=placeholders,
            file_path="/test.docx",
        )

        assert len(template.placeholders) == 1000

    def test_template_name_with_special_valid_characters(self):
        """Test template name with various valid characters."""
        # Names can contain spaces, punctuation, etc.
        template = Template(
            name="Invoice Template (2024) - Standard",
            file_path="/test.docx",
        )

        assert "2024" in template.name
        assert "(" in template.name
        assert ")" in template.name

    def test_template_description_multiline(self):
        """Test that multiline descriptions work."""
        template = Template(
            name="Test",
            description="Line 1\nLine 2\nLine 3",
            file_path="/test.docx",
        )

        assert "\n" in template.description

    def test_template_file_path_windows_style(self):
        """Test that Windows-style file paths work."""
        template = Template(
            name="Test",
            file_path="C:\\Templates\\test.docx",
        )

        assert "C:" in template.file_path

    def test_template_placeholder_underscore_and_hyphen(self):
        """Test that underscores and hyphens work in placeholders."""
        template = Template(
            name="Test",
            placeholders=["first_name", "last-name", "middle_name-2"],
            file_path="/test.docx",
        )

        assert "first_name" in template.placeholders
        assert "last-name" in template.placeholders
        assert "middle_name-2" in template.placeholders


class TestTemplateConfig:
    """Test Pydantic configuration for Template model."""

    def test_json_encoders_datetime(self):
        """Test that datetime is serializable in model_dump."""
        import json

        template = Template(name="Test", file_path="/test.docx")

        # Convert to dict using model_dump(mode='json')
        data = template.model_dump(mode="json")

        # Verify datetime is present and serializable (as ISO string in JSON mode)
        assert "created_at" in data

        # Should be JSON serializable
        json_str = json.dumps(data)
        assert "created_at" in json_str

    def test_validate_assignment_enabled(self):
        """Test that field validation happens on assignment."""
        template = Template(name="Test", file_path="/test.docx")

        # Assigning invalid name should raise error
        with pytest.raises(ValueError):
            template.name = ""

    def test_model_dump_excludes_internal_config(self):
        """Test that model_dump doesn't include Pydantic internals."""
        template = Template(name="Test", file_path="/test.docx")

        data = template.model_dump()

        # Should only have model fields, not Pydantic internals
        expected_keys = {"id", "name", "description", "placeholders", "file_path", "created_at"}
        assert set(data.keys()) == expected_keys
