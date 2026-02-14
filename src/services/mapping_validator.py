"""
Fill Application - Mapping Validation Service

Validates data-to-template field mappings.
Checks that template placeholders have data column mappings.
"""

from typing import Any

from src.models.mapping import Mapping
from src.models.template import Template
from src.services.template_store import get_template_store


class MappingValidationError(Exception):
    """
    Custom exception for mapping validation errors.
    """

    def __init__(self, message: str, errors: list[str]) -> None:
        """
        Initialize validation error.

        Args:
            message: Overall error message
            errors: List of specific validation error messages
        """
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class MappingValidator:
    """
    Validates mapping objects for correctness.

    Checks:
    - All template placeholders are mapped to data columns
    - Mapped columns exist in source data
    - Mapping is consistent and complete
    """

    def __init__(self) -> None:
        """
        Initialize the mapping validator.

        Validator uses TemplateStore to retrieve template definitions.
        """
        self._template_store = get_template_store()

    def validate(self, mapping: Mapping, data_columns: list[str]) -> None:
        """
        Validate a mapping object.

        Args:
            mapping: Mapping object to validate
            data_columns: List of column names from source data

        Raises:
            MappingValidationError: If validation fails with detailed errors
        """
        errors: list[str] = []

        # Step 1: Check that template exists
        template = self._template_store.get_template(mapping.template_id)
        if template is None:
            errors.append(f"Template not found: {mapping.template_id}")

        # Step 2: Validate template placeholders are mapped
        if template is not None:
            placeholder_errors = self._validate_placeholders_mapped(
                template, mapping
            )
            errors.extend(placeholder_errors)

        # Step 3: Validate mapped columns exist in data
        column_errors = self._validate_columns_exist(
                mapping, data_columns
            )
        errors.extend(column_errors)

        # If any errors, raise exception
        if errors:
            raise MappingValidationError(
                message=f"Mapping validation failed with {len(errors)} error(s)",
                errors=errors
            )

    def _validate_placeholders_mapped(
        self, template: Template, mapping: Mapping
    ) -> list[str]:
        """
        Validate that all template placeholders are mapped.

        Args:
            template: Template object with required placeholders
            mapping: Mapping object with column mappings

        Returns:
            List of error messages for unmapped placeholders
        """
        errors: list[str] = []
        required_placeholders = set(template.placeholders)
        mapped_placeholders = set(mapping.column_mappings.values())

        # Find unmapped placeholders
        unmapped = required_placeholders - mapped_placeholders
        for placeholder in sorted(unmapped):
            errors.append(
                f"Template placeholder '{{{placeholder}}}' is not mapped to any data column"
            )

        return errors

    def _validate_columns_exist(
        self, mapping: Mapping, data_columns: list[str]
    ) -> list[str]:
        """
        Validate that mapped columns exist in source data.

        Args:
            mapping: Mapping object with column mappings
            data_columns: List of column names from source data

        Returns:
            List of error messages for missing columns
        """
        errors: list[str] = []
        data_column_set = set(data_columns)
        mapped_columns = set(mapping.column_mappings.keys())

        # Find columns that don't exist in data
        missing = mapped_columns - data_column_set
        for column in sorted(missing):
            errors.append(
                f"Mapped column '{column}' does not exist in source data"
            )

        return errors


def validate_mapping(
    mapping: Mapping,
    data_columns: list[str],
) -> None:
    """
    Convenience function to validate a mapping.

    Creates MappingValidator instance and validates the mapping.

    Args:
        mapping: Mapping object to validate
        data_columns: List of column names from source data

    Raises:
        MappingValidationError: If validation fails
    """
    validator = MappingValidator()
    validator.validate(mapping, data_columns)
