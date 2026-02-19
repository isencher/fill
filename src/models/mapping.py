"""
Fill Application - Mapping Model

Defines the Mapping model for linking data columns to template placeholders.
Maps table columns to template placeholder fields for auto-filling.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Mapping(BaseModel):
    """
    Mapping model for data-to-template field mapping.

    A mapping defines how columns from uploaded data files map to
    placeholder fields in templates. This enables the system to know
    which data values fill which template placeholders.

    Attributes:
        id: Unique identifier for the mapping
        file_id: ID of the uploaded data file (source of data)
        template_id: ID of the template to fill (destination for data)
        column_mappings: Dictionary mapping column names to placeholder names
                      Format: {"column_name": "placeholder_name"}
        created_at: Timestamp when mapping was created
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    file_id: str = Field(..., min_length=1, description="ID of uploaded data file")
    template_id: str = Field(..., min_length=1, description="ID of template to fill")
    column_mappings: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of data columns to template placeholders"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("file_id")
    @classmethod
    def validate_file_id(cls, v: str) -> str:
        """
        Validate file ID.

        Args:
            v: The file_id value to validate

        Returns:
            Trimmed file_id

        Raises:
            ValueError: If file_id is empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("File ID cannot be empty or whitespace only")

        return v.strip()

    @field_validator("template_id")
    @classmethod
    def validate_template_id(cls, v: str) -> str:
        """
        Validate template ID.

        Args:
            v: The template_id value to validate

        Returns:
            Trimmed template_id

        Raises:
            ValueError: If template_id is empty or whitespace only
        """
        if not v or not v.strip():
            raise ValueError("Template ID cannot be empty or whitespace only")

        return v.strip()

    @field_validator("column_mappings")
    @classmethod
    def validate_column_mappings(cls, v: dict[str, str]) -> dict[str, str]:
        """
        Validate column mappings dictionary.

        Mappings must:
        - Have non-empty column names (keys)
        - Have non-empty placeholder names (values)
        - Trim whitespace from both keys and values

        Args:
            v: Dictionary of column_name -> placeholder_name mappings

        Returns:
            Validated and cleaned mapping dictionary

        Raises:
            ValueError: If mappings are invalid
        """
        if not isinstance(v, dict):
            raise ValueError("Column mappings must be a dictionary")

        validated = {}

        for column_name, placeholder_name in v.items():
            # Validate column name (key)
            if not column_name or not isinstance(column_name, str):
                raise ValueError("Column name must be a non-empty string")

            column_clean = column_name.strip()
            if not column_clean:
                raise ValueError("Column name cannot be empty or whitespace only")

            # Validate placeholder name (value)
            if not placeholder_name or not isinstance(placeholder_name, str):
                raise ValueError("Placeholder name must be a non-empty string")

            placeholder_clean = placeholder_name.strip()
            if not placeholder_clean:
                raise ValueError("Placeholder name cannot be empty or whitespace only")

            # Store cleaned mapping
            validated[column_clean] = placeholder_clean

        return validated

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
    def model_validate_json(cls, data: dict[str, Any]) -> "Mapping":
        """
        Create Mapping instance from dictionary.

        Args:
            data: Dictionary containing mapping data

        Returns:
            Mapping instance

        Raises:
            ValueError: If data is invalid
        """
        return cls(**data)

    model_config = ConfigDict(
        # Use enum values (not strings) in JSON
        use_enum_values=True,
        # Validate assignment on instance creation
        validate_assignment=True,
        # JSON schema examples
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "file_id": "file-uuid-1234",
                    "template_id": "template-uuid-5678",
                    "column_mappings": {
                        "Customer Name": "customer_name",
                        "Invoice Date": "invoice_date",
                        "Total Amount": "total_amount",
                    },
                    "created_at": "2026-02-14T12:00:00",
                }
            ]
        },
    )
