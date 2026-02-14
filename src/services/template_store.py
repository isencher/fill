"""
Fill Application - Template Storage Service

In-memory storage for Template objects.
Provides CRUD operations for template management.
"""

from threading import Lock
from typing import Any
from uuid import UUID

from src.models.template import Template


class TemplateStore:
    """
    In-memory storage for Template objects.

    Thread-safe storage using locks for concurrent access.
    Templates are stored in a dictionary keyed by template ID.

    This is a simple in-memory implementation for development.
    Production version should use a proper database.
    """

    def __init__(self) -> None:
        """
        Initialize the template store.

        Creates empty storage and lock for thread safety.
        """
        self._storage: dict[str, Template] = {}
        self._lock = Lock()

    def save_template(self, template: Template) -> Template:
        """
        Save a template to storage.

        If template with same ID exists, it will be updated.
        Otherwise, new template is created.

        Args:
            template: Template object to save

        Returns:
            The saved template (same as input)

        Raises:
            ValueError: If template validation fails
        """
        # Validate template (pydantic validation happens on creation)
        if not isinstance(template, Template):
            raise ValueError(f"Expected Template object, got {type(template)}")

        # Thread-safe write
        with self._lock:
            self._storage[template.id] = template

        return template

    def get_template(self, template_id: str | UUID) -> Template | None:
        """
        Retrieve a template by ID.

        Args:
            template_id: UUID of template to retrieve

        Returns:
            Template object if found, None otherwise
        """
        # Convert UUID to string if needed
        if isinstance(template_id, UUID):
            template_id = str(template_id)

        # Thread-safe read
        with self._lock:
            return self._storage.get(template_id)

    def get_template_by_name(self, name: str) -> Template | None:
        """
        Retrieve a template by name (exact match).

        Args:
            name: Template name to search for

        Returns:
            First template matching the name, or None if not found
        """
        # Thread-safe read
        with self._lock:
            for template in self._storage.values():
                if template.name == name:
                    return template
        return None

    def list_templates(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> list[Template]:
        """
        List all templates with pagination and sorting.

        Args:
            limit: Maximum number of templates to return (default: 100, max: 1000)
            offset: Number of templates to skip (default: 0)
            sort_by: Field to sort by (default: "created_at", options: name, created_at)
            order: Sort order (default: "desc", options: asc, desc)

        Returns:
            List of Template objects

        Raises:
            ValueError: If limit or offset are invalid, or sort parameters are invalid
        """
        # Validate limit
        if limit < 1:
            raise ValueError("Limit must be at least 1")
        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")

        # Validate offset
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        # Validate sort_by
        valid_sort_fields = {"name", "created_at"}
        if sort_by not in valid_sort_fields:
            raise ValueError(
                f"Invalid sort field: {sort_by}. "
                f"Valid options: {', '.join(sorted(valid_sort_fields))}"
            )

        # Validate order
        valid_orders = {"asc", "desc"}
        if order not in valid_orders:
            raise ValueError(
                f"Invalid sort order: {order}. "
                f"Valid options: {', '.join(sorted(valid_orders))}"
            )

        # Thread-safe read
        with self._lock:
            # Get all templates
            templates = list(self._storage.values())

            # Sort templates
            reverse = order == "desc"
            templates.sort(
                key=lambda t: getattr(t, sort_by),
                reverse=reverse
            )

            # Apply pagination
            total = len(templates)
            end = offset + limit
            paginated = templates[offset:end]

            return paginated

    def count_templates(self) -> int:
        """
        Count total number of templates in storage.

        Returns:
            Total count of templates
        """
        # Thread-safe read
        with self._lock:
            return len(self._storage)

    def delete_template(self, template_id: str | UUID) -> bool:
        """
        Delete a template by ID.

        Args:
            template_id: UUID of template to delete

        Returns:
            True if template was deleted, False if not found
        """
        # Convert UUID to string if needed
        if isinstance(template_id, UUID):
            template_id = str(template_id)

        # Thread-safe write
        with self._lock:
            if template_id in self._storage:
                del self._storage[template_id]
                return True
            return False

    def update_template(
        self,
        template_id: str | UUID,
        **updates: Any
    ) -> Template | None:
        """
        Update specific fields of a template.

        Args:
            template_id: UUID of template to update
            **updates: Field values to update (name, description, placeholders, file_path)

        Returns:
            Updated template if found, None otherwise

        Raises:
            ValueError: If updates contain invalid field names or values
        """
        # Convert UUID to string if needed
        if isinstance(template_id, UUID):
            template_id = str(template_id)

        # Valid fields that can be updated
        valid_fields = {"name", "description", "placeholders", "file_path"}
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            raise ValueError(
                f"Invalid field(s) for update: {', '.join(invalid_fields)}. "
                f"Valid fields: {', '.join(sorted(valid_fields))}"
            )

        # Thread-safe read-modify-write
        with self._lock:
            template = self._storage.get(template_id)
            if template is None:
                return None

            # Apply updates
            for field, value in updates.items():
                setattr(template, field, value)

            # Re-validate after update (pydantic will validate on assignment)
            # Store updated object
            self._storage[template_id] = template
            return template

    def clear(self) -> None:
        """
        Clear all templates from storage.

        Useful for testing and resetting state.
        """
        # Thread-safe write
        with self._lock:
            self._storage.clear()


# Global singleton instance
_default_store: TemplateStore | None = None
_store_lock = Lock()


def get_template_store() -> TemplateStore:
    """
    Get the global template store singleton.

    Returns:
        The global TemplateStore instance (created if needed)
    """
    global _default_store

    if _default_store is None:
        with _store_lock:
            # Double-check after acquiring lock
            if _default_store is None:
                _default_store = TemplateStore()

    return _default_store
