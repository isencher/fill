"""
Fill Application - Mapping Repository

Database repository for Mapping model CRUD operations.
"""

import json
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from migrations import Mapping as MappingModel


class MappingRepository:
    """
    Repository for Mapping database operations.

    Provides CRUD operations for the Mapping model.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize MappingRepository.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create_mapping(
        self,
        file_id: UUID | str,
        template_id: UUID | str,
        column_mappings: Dict[str, str],
    ) -> MappingModel:
        """
        Create a new mapping record.

        Args:
            file_id: File UUID
            template_id: Template UUID
            column_mappings: Dictionary mapping columns to placeholders

        Returns:
            MappingModel: Created mapping record
        """
        mapping_record = MappingModel(
            file_id=file_id,
            template_id=template_id,
            column_mappings=json.dumps(column_mappings),
            created_at=datetime.utcnow(),
        )
        self.session.add(mapping_record)
        self.session.flush()
        self.session.refresh(mapping_record)
        return mapping_record

    def get_mapping_by_id(self, mapping_id: UUID | str) -> MappingModel | None:
        """
        Get mapping by ID.

        Args:
            mapping_id: Mapping UUID

        Returns:
            MappingModel if found, None otherwise
        """
        return (
            self.session.query(MappingModel)
            .filter(MappingModel.id == mapping_id)
            .first()
        )

    def get_mappings_by_file(self, file_id: UUID | str) -> List[MappingModel]:
        """
        Get all mappings for a file.

        Args:
            file_id: File UUID

        Returns:
            List of MappingModel objects
        """
        return (
            self.session.query(MappingModel)
            .filter(MappingModel.file_id == file_id)
            .all()
        )

    def get_mappings_by_template(self, template_id: UUID | str) -> List[MappingModel]:
        """
        Get all mappings for a template.

        Args:
            template_id: Template UUID

        Returns:
            List of MappingModel objects
        """
        return (
            self.session.query(MappingModel)
            .filter(MappingModel.template_id == template_id)
            .all()
        )

    def get_mapping_for_file_template(
        self,
        file_id: UUID | str,
        template_id: UUID | str,
    ) -> MappingModel | None:
        """
        Get mapping for specific file and template combination.

        Args:
            file_id: File UUID
            template_id: Template UUID

        Returns:
            MappingModel if found, None otherwise
        """
        return (
            self.session.query(MappingModel)
            .filter(
                MappingModel.file_id == file_id,
                MappingModel.template_id == template_id,
            )
            .first()
        )

    def list_mappings(self, limit: int = 100, offset: int = 0) -> List[MappingModel]:
        """
        List all mappings with pagination.

        Args:
            limit: Maximum number of mappings to return
            offset: Number of mappings to skip

        Returns:
            List of MappingModel objects
        """
        return (
            self.session.query(MappingModel)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_mappings(self) -> int:
        """
        Count total mappings.

        Returns:
            Total number of mappings
        """
        return self.session.query(MappingModel).count()

    def update_mapping(
        self,
        mapping_id: UUID | str,
        column_mappings: Dict[str, str] | None = None,
    ) -> MappingModel | None:
        """
        Update mapping column mappings.

        Args:
            mapping_id: Mapping UUID
            column_mappings: New column mappings dictionary

        Returns:
            Updated MappingModel if found, None otherwise
        """
        mapping_record = self.get_mapping_by_id(mapping_id)
        if mapping_record:
            if column_mappings is not None:
                mapping_record.column_mappings = json.dumps(column_mappings)
            self.session.flush()
            self.session.refresh(mapping_record)
        return mapping_record

    def delete_mapping(self, mapping_id: UUID | str) -> bool:
        """
        Delete mapping by ID.

        Args:
            mapping_id: Mapping UUID

        Returns:
            True if deleted, False if not found
        """
        mapping_record = self.get_mapping_by_id(mapping_id)
        if mapping_record:
            self.session.delete(mapping_record)
            self.session.flush()
            return True
        return False
