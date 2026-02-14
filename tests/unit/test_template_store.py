"""
Unit tests for Template Store Service.

Tests cover CRUD operations, pagination, sorting, and thread safety.
"""

import pytest

from src.models.template import Template
from src.services.template_store import TemplateStore, get_template_store


class TestTemplateStoreCreation:
    """Test TemplateStore initialization."""

    def test_new_store_is_empty(self):
        """Test that new store has no templates."""
        store = TemplateStore()
        assert store.count_templates() == 0

    def test_new_store_has_empty_list(self):
        """Test that listing empty store returns empty list."""
        store = TemplateStore()
        templates = store.list_templates()
        assert templates == []

    def test_get_template_store_singleton(self):
        """Test that get_template_store returns singleton."""
        store1 = get_template_store()
        store2 = get_template_store()

        assert store1 is store2


class TestSaveTemplate:
    """Test save_template operation."""

    def test_save_single_template(self):
        """Test saving a single template."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")

        saved = store.save_template(template)

        assert saved is template
        assert store.count_templates() == 1
        assert store.get_template(saved.id) is template

    def test_save_multiple_templates(self):
        """Test saving multiple templates."""
        store = TemplateStore()
        t1 = Template(name="T1", file_path="/t1.docx")
        t2 = Template(name="T2", file_path="/t2.docx")
        t3 = Template(name="T3", file_path="/t3.docx")

        store.save_template(t1)
        store.save_template(t2)
        store.save_template(t3)

        assert store.count_templates() == 3

    def test_save_updates_existing_template(self):
        """Test that saving existing template updates it."""
        store = TemplateStore()
        template = Template(name="Original", file_path="/test.docx")
        store.save_template(template)

        # Update template
        template.name = "Updated"
        template.description = "New description"
        saved = store.save_template(template)

        assert saved.name == "Updated"
        assert saved.description == "New description"
        assert store.count_templates() == 1  # Still only 1

    def test_save_with_non_template_raises_error(self):
        """Test that saving non-Template raises ValueError."""
        store = TemplateStore()
        with pytest.raises(ValueError, match="Expected Template"):
            store.save_template("not a template")

    def test_save_preserves_id(self):
        """Test that saving preserves original ID."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        original_id = template.id
        template.name = "Updated"
        store.save_template(template)

        assert template.id == original_id

    def test_save_with_placeholders(self):
        """Test saving template with placeholders."""
        store = TemplateStore()
        template = Template(
            name="Invoice",
            placeholders=["customer", "amount"],
            file_path="/invoice.docx",
        )

        saved = store.save_template(template)

        assert saved.placeholders == ["customer", "amount"]


class TestGetTemplate:
    """Test get_template operation."""

    def test_get_template_by_id(self):
        """Test retrieving template by ID."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        found = store.get_template(template.id)

        assert found is template
        assert found.name == "Test"

    def test_get_template_with_uuid_object(self):
        """Test retrieving template with UUID object."""
        from uuid import UUID

        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        found = store.get_template(UUID(template.id))

        assert found is template

    def test_get_nonexistent_template_returns_none(self):
        """Test that getting nonexistent template returns None."""
        store = TemplateStore()
        found = store.get_template("nonexistent-id")

        assert found is None

    def test_get_template_by_name(self):
        """Test retrieving template by name."""
        store = TemplateStore()
        template = Template(name="Unique Name", file_path="/test.docx")
        store.save_template(template)

        found = store.get_template_by_name("Unique Name")

        assert found is template
        assert found.name == "Unique Name"

    def test_get_template_by_name_not_found_returns_none(self):
        """Test that getting template by non-existent name returns None."""
        store = TemplateStore()
        found = store.get_template_by_name("Nonexistent")

        assert found is None

    def test_get_template_by_name_returns_first_match(self):
        """Test that get by name returns first matching template."""
        store = TemplateStore()
        t1 = Template(name="Same", file_path="/t1.docx")
        t2 = Template(name="Same", file_path="/t2.docx")
        store.save_template(t1)
        store.save_template(t2)

        found = store.get_template_by_name("Same")

        assert found is t1  # First one saved


class TestListTemplates:
    """Test list_templates operation."""

    def test_list_empty_store(self):
        """Test listing empty store."""
        store = TemplateStore()
        templates = store.list_templates()
        assert templates == []

    def test_list_returns_all_templates(self):
        """Test listing returns all templates."""
        store = TemplateStore()
        t1 = Template(name="A", file_path="/a.docx")
        t2 = Template(name="B", file_path="/b.docx")
        t3 = Template(name="C", file_path="/c.docx")
        store.save_template(t1)
        store.save_template(t2)
        store.save_template(t3)

        templates = store.list_templates()

        assert len(templates) == 3
        assert t1 in templates
        assert t2 in templates
        assert t3 in templates

    def test_list_default_sorting_by_created_at_desc(self):
        """Test default sorting is by created_at descending."""
        store = TemplateStore()
        import time

        t1 = Template(name="First", file_path="/t1.docx")
        store.save_template(t1)
        time.sleep(0.01)  # Ensure different timestamps

        t2 = Template(name="Second", file_path="/t2.docx")
        store.save_template(t2)
        time.sleep(0.01)

        t3 = Template(name="Third", file_path="/t3.docx")
        store.save_template(t3)

        templates = store.list_templates()

        assert templates[0].name == "Third"
        assert templates[1].name == "Second"
        assert templates[2].name == "First"

    def test_limit_parameter(self):
        """Test limit parameter works."""
        store = TemplateStore()
        for i in range(10):
            store.save_template(Template(name=f"T{i}", file_path=f"/t{i}.docx"))

        templates = store.list_templates(limit=5)

        assert len(templates) == 5

    def test_limit_max_value(self):
        """Test limit maximum is 1000."""
        store = TemplateStore()
        for i in range(100):
            store.save_template(Template(name=f"T{i}", file_path=f"/t{i}.docx"))

        # 100 templates, limit 1000 should return all
        templates = store.list_templates(limit=1000)

        assert len(templates) == 100

    def test_limit_too_large_raises_error(self):
        """Test limit > 1000 raises ValueError."""
        store = TemplateStore()
        with pytest.raises(ValueError, match="exceed"):
            store.list_templates(limit=1001)

    def test_limit_too_small_raises_error(self):
        """Test limit < 1 raises ValueError."""
        store = TemplateStore()
        with pytest.raises(ValueError, match="at least"):
            store.list_templates(limit=0)

    def test_offset_parameter(self):
        """Test offset parameter works."""
        store = TemplateStore()
        for i in range(5):
            store.save_template(Template(name=f"T{i}", file_path=f"/t{i}.docx"))

        templates = store.list_templates(offset=2)

        assert len(templates) == 3  # Skipped first 2

    def test_offset_negative_raises_error(self):
        """Test negative offset raises ValueError."""
        store = TemplateStore()
        with pytest.raises(ValueError, match="negative"):
            store.list_templates(offset=-1)

    def test_invalid_sort_by_field_raises_error(self):
        """Test invalid sort_by field raises ValueError."""
        store = TemplateStore()
        with pytest.raises(ValueError, match="Invalid sort field"):
            store.list_templates(sort_by="invalid_field")

    def test_invalid_sort_order_raises_error(self):
        """Test invalid sort order raises ValueError."""
        store = TemplateStore()
        with pytest.raises(ValueError, match="Invalid sort order"):
            store.list_templates(order="invalid")

    def test_sort_by_name_asc(self):
        """Test sorting by name ascending."""
        store = TemplateStore()
        t1 = Template(name="C", file_path="/c.docx")
        t2 = Template(name="A", file_path="/a.docx")
        t3 = Template(name="B", file_path="/b.docx")
        store.save_template(t1)
        store.save_template(t2)
        store.save_template(t3)

        templates = store.list_templates(sort_by="name", order="asc")

        assert templates[0].name == "A"
        assert templates[1].name == "B"
        assert templates[2].name == "C"


class TestDeleteTemplate:
    """Test delete_template operation."""

    def test_delete_existing_template(self):
        """Test deleting an existing template."""
        store = TemplateStore()
        template = Template(name="To Delete", file_path="/test.docx")
        store.save_template(template)

        result = store.delete_template(template.id)

        assert result is True
        assert store.get_template(template.id) is None
        assert store.count_templates() == 0

    def test_delete_nonexistent_template(self):
        """Test deleting a nonexistent template."""
        store = TemplateStore()
        result = store.delete_template("nonexistent-id")

        assert result is False

    def test_delete_with_uuid_object(self):
        """Test deleting template with UUID object."""
        from uuid import UUID

        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        result = store.delete_template(UUID(template.id))

        assert result is True
        assert store.count_templates() == 0


class TestUpdateTemplate:
    """Test update_template operation."""

    def test_update_template_name(self):
        """Test updating template name."""
        store = TemplateStore()
        template = Template(name="Original", file_path="/test.docx")
        store.save_template(template)

        updated = store.update_template(template.id, name="Updated")

        assert updated is not None
        assert updated.name == "Updated"
        assert store.get_template(template.id).name == "Updated"

    def test_update_template_description(self):
        """Test updating template description."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        updated = store.update_template(template.id, description="New description")

        assert updated is not None
        assert updated.description == "New description"

    def test_update_template_placeholders(self):
        """Test updating template placeholders."""
        store = TemplateStore()
        template = Template(name="Test", placeholders=["old"], file_path="/test.docx")
        store.save_template(template)

        updated = store.update_template(template.id, placeholders=["new1", "new2"])

        assert updated is not None
        assert updated.placeholders == ["new1", "new2"]

    def test_update_template_file_path(self):
        """Test updating template file path."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/old.docx")
        store.save_template(template)

        updated = store.update_template(template.id, file_path="/new.docx")

        assert updated is not None
        assert updated.file_path == "/new.docx"

    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        store = TemplateStore()
        template = Template(
            name="Original",
            description="Original desc",
            placeholders=["old"],
            file_path="/old.docx",
        )
        store.save_template(template)

        updated = store.update_template(
            template.id,
            name="Updated",
            description="Updated desc",
            placeholders=["new"],
            file_path="/new.docx",
        )

        assert updated is not None
        assert updated.name == "Updated"
        assert updated.description == "Updated desc"
        assert updated.placeholders == ["new"]
        assert updated.file_path == "/new.docx"

    def test_update_nonexistent_template(self):
        """Test updating a nonexistent template."""
        store = TemplateStore()
        updated = store.update_template("nonexistent-id", name="Test")

        assert updated is None

    def test_update_with_invalid_field_raises_error(self):
        """Test updating with invalid field raises ValueError."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        with pytest.raises(ValueError, match="Invalid field"):
            store.update_template(template.id, invalid_field="value")

    def test_update_with_multiple_invalid_fields_raises_error(self):
        """Test updating with multiple invalid fields raises ValueError."""
        store = TemplateStore()
        template = Template(name="Test", file_path="/test.docx")
        store.save_template(template)

        with pytest.raises(ValueError, match="Invalid field"):
            store.update_template(template.id, field1="v1", field2="v2")

    def test_update_with_uuid_object(self):
        """Test updating template with UUID object."""
        from uuid import UUID

        store = TemplateStore()
        template = Template(name="Original", file_path="/test.docx")
        store.save_template(template)

        updated = store.update_template(UUID(template.id), name="Updated")

        assert updated is not None
        assert updated.name == "Updated"

    def test_update_preserves_id_and_created_at(self):
        """Test that update preserves ID and created_at."""
        store = TemplateStore()
        template = Template(name="Original", file_path="/test.docx")
        store.save_template(template)

        original_id = template.id
        original_created_at = template.created_at

        updated = store.update_template(template.id, name="Updated")

        assert updated.id == original_id
        assert updated.created_at == original_created_at


class TestClearTemplates:
    """Test clear operation."""

    def test_clear_empty_store(self):
        """Test clearing empty store."""
        store = TemplateStore()
        store.clear()
        assert store.count_templates() == 0

    def test_clear_with_templates(self):
        """Test clearing store with templates."""
        store = TemplateStore()
        t1 = Template(name="T1", file_path="/t1.docx")
        t2 = Template(name="T2", file_path="/t2.docx")
        store.save_template(t1)
        store.save_template(t2)

        store.clear()

        assert store.count_templates() == 0
        assert store.list_templates() == []

    def test_clear_multiple_times(self):
        """Test clearing store multiple times."""
        store = TemplateStore()
        store.save_template(Template(name="T", file_path="/t.docx"))

        store.clear()
        assert store.count_templates() == 0

        store.clear()
        assert store.count_templates() == 0

