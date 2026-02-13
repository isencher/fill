"""
Fill Application - Template Model

Defines the Template model for managing document templates with placeholders.
Templates contain file references and metadata for auto-filling.
"""

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Template(BaseModel):
    """
    Template model for document auto-filling.

    A template represents a document structure with placeholders that can be
    filled with data from uploaded files. Placeholders use the syntax: {{field_name}}

    Attributes:
        id: Unique identifier for the template
        name: Human-readable name for the template
        description: Optional description of template purpose
        placeholders: List of placeholder names (extracted from template)
        file_path: Path to the template file (for future document generation)
        created_at: Timestamp when template was created
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    placeholders: list[str] = Field(default_factory=list)
    file_path: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate template name.

        Names must:
        - Not be empty (handled by min_length)
        - Not exceed 200 characters (handled by max_length)
        - Not contain only whitespace
        - Trim leading/trailing whitespace

        Args:
            v: The name value to validate

        Returns:
            Trimmed name

        Raises:
            ValueError: If name is empty after trimming
        """
        if not v or not v.strip():
            raise ValueError("Template name cannot be empty or whitespace only")

        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        Validate template description.

        Args:
            v: The description value to validate

        Returns:
            Trimmed description or None
        """
        if v is None:
            return None

        # Trim whitespace, return None if empty after trimming
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("placeholders")
    @classmethod
    def validate_placeholders(cls, v: list[str]) -> list[str]:
        """
        Validate placeholder list.

        Placeholders must:
        - Be unique (no duplicates)
        - Follow placeholder syntax: {{field_name}}
        - Not be empty strings
        - Contain only valid characters (alphanumeric, underscore, hyphen)

        Args:
            v: List of placeholder names

        Returns:
            Validated list of unique placeholders

        Raises:
            ValueError: If placeholders are invalid
        """
        validated = []

        for placeholder in v:
            if not placeholder or not placeholder.strip():
                raise ValueError("Placeholder cannot be empty or whitespace only")

            # Trim whitespace
            placeholder_clean = placeholder.strip()

            # Check for duplicates (case-insensitive)
            if placeholder_clean.lower() in [p.lower() for p in validated]:
                raise ValueError(f"Duplicate placeholder: {placeholder_clean}")

            # Validate placeholder contains only valid characters
            # Valid: alphanumeric, underscore, hyphen
            if not all(c.isalnum() or c in ("_", "-") for c in placeholder_clean):
                raise ValueError(
                    f"Invalid placeholder '{placeholder_clean}'. "
                    "Placeholders must contain only letters, numbers, underscores, and hyphens."
                )

            validated.append(placeholder_clean)

        return validated

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """
        Validate template file path.

        Args:
            v: The file path to validate

        Returns:
            Normalized file path

        Raises:
            ValueError: If file path is empty
        """
        if not v or not v.strip():
            raise ValueError("Template file path cannot be empty")

        # Normalize path separators
        path = Path(v.strip())

        # For now, just return the string representation
        # In future, could validate file exists, extension, etc.
        return str(path)

    def model_dump_json(self, **kwargs: Any) -> dict[str, Any]:
        """
        Export model to dictionary for JSON serialization.

        Args:
            **kwargs: Additional arguments for pydantic's model_dump

        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(**kwargs)

    @classmethod
    def model_validate_json(cls, data: dict[str, Any]) -> "Template":
        """
        Create Template instance from dictionary.

        Args:
            data: Dictionary containing template data

        Returns:
            Template instance

        Raises:
            ValueError: If data is invalid
        """
        return cls(**data)

    class Config:
        """Pydantic model configuration."""

        # Use enum values (not strings) in JSON
        use_enum_values = True

        # Validate assignment on instance creation
        validate_assignment = True

        # JSON schema examples
        json_schema_extra = {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Invoice Template",
                    "description": "Standard invoice template with customer info",
                    "placeholders": ["customer_name", "invoice_date", "total_amount"],
                    "file_path": "/templates/invoice.docx",
                    "created_at": "2026-02-13T12:00:00",
                }
            ]
        }

