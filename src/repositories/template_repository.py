"""
Fill Application - Template Repository

Database repository for Template model CRUD operations.
"""

import json
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from migrations import Template as TemplateModel


class TemplateRepository:
    """
    Repository for Template database operations.

    Provides CRUD operations for the Template model.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize TemplateRepository.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create_template(
        self,
        name: str,
        placeholders: List[str],
        file_path: str,
        description: str | None = None,
    ) -> TemplateModel:
        """
        Create a new template record.

        Args:
            name: Template name
            placeholders: List of placeholder strings
            file_path: Path to template file
            description: Optional description

        Returns:
            TemplateModel: Created template record
        """
        template_record = TemplateModel(
            name=name,
            description=description,
            placeholders=json.dumps(placeholders),
            file_path=file_path,
            created_at=datetime.utcnow(),
        )
        self.session.add(template_record)
        self.session.flush()
        self.session.refresh(template_record)
        return template_record

    def get_template_by_id(self, template_id: UUID | str) -> TemplateModel | None:
        """
        Get template by ID.

        Args:
            template_id: Template UUID

        Returns:
            TemplateModel if found, None otherwise
        """
        return (
            self.session.query(TemplateModel)
            .filter(TemplateModel.id == template_id)
            .first()
        )

    def get_template_by_name(self, name: str) -> TemplateModel | None:
        """
        Get template by name.

        Args:
            name: Template name

        Returns:
            TemplateModel if found, None otherwise
        """
        return (
            self.session.query(TemplateModel)
            .filter(TemplateModel.name == name)
            .first()
        )

    def list_templates(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[TemplateModel]:
        """
        List templates with pagination and sorting.

        Args:
            limit: Maximum number of templates to return
            offset: Number of templates to skip
            sort_by: Field to sort by (name, created_at)
            sort_order: Sort order (asc, desc)

        Returns:
            List of TemplateModel objects
        """
        query = self.session.query(TemplateModel)

        # Validate sort parameters
        valid_sort_fields = {"name", "created_at"}
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"

        # Apply sorting
        sort_column = getattr(TemplateModel, sort_by)
        if sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        return query.limit(limit).offset(offset).all()

    def count_templates(self) -> int:
        """
        Count total templates.

        Returns:
            Total number of templates
        """
        return self.session.query(TemplateModel).count()

    def update_template(
        self,
        template_id: UUID | str,
        name: str | None = None,
        description: str | None = None,
        placeholders: List[str] | None = None,
        file_path: str | None = None,
    ) -> TemplateModel | None:
        """
        Update template fields.

        Args:
            template_id: Template UUID
            name: New name (optional)
            description: New description (optional)
            placeholders: New placeholders (optional)
            file_path: New file path (optional)

        Returns:
            Updated TemplateModel if found, None otherwise
        """
        template_record = self.get_template_by_id(template_id)
        if template_record:
            if name is not None:
                template_record.name = name
            if description is not None:
                template_record.description = description
            if placeholders is not None:
                template_record.placeholders = json.dumps(placeholders)
            if file_path is not None:
                template_record.file_path = file_path
            self.session.flush()
            self.session.refresh(template_record)
        return template_record

    def delete_template(self, template_id: UUID | str) -> bool:
        """
        Delete template by ID.

        Args:
            template_id: Template UUID

        Returns:
            True if deleted, False if not found
        """
        template_record = self.get_template_by_id(template_id)
        if template_record:
            self.session.delete(template_record)
            self.session.flush()
            return True
        return False
