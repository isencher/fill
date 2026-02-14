"""
Fill Application - File Repository

Database repository for File model CRUD operations.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from migrations import File as FileModel


class FileRepository:
    """
    Repository for File database operations.

    Provides CRUD operations for the File model.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize FileRepository.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create_file(
        self,
        filename: str,
        content_type: str,
        size: int,
        file_path: str,
        status: str = "pending",
    ) -> FileModel:
        """
        Create a new file record.

        Args:
            filename: Original filename
            content_type: MIME type
            size: File size in bytes
            file_path: Path to stored file
            status: Processing status

        Returns:
            FileModel: Created file record
        """
        file_record = FileModel(
            filename=filename,
            content_type=content_type,
            size=size,
            file_path=file_path,
            status=status,
            uploaded_at=datetime.utcnow(),
        )
        self.session.add(file_record)
        self.session.flush()
        self.session.refresh(file_record)
        return file_record

    def get_file_by_id(self, file_id: UUID | str) -> FileModel | None:
        """
        Get file by ID.

        Args:
            file_id: File UUID

        Returns:
            FileModel if found, None otherwise
        """
        return (
            self.session.query(FileModel)
            .filter(FileModel.id == file_id)
            .first()
        )

    def list_files(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
    ) -> List[FileModel]:
        """
        List files with pagination and filtering.

        Args:
            limit: Maximum number of files to return (1-1000)
            offset: Number of files to skip
            status: Optional status filter

        Returns:
            List of FileModel objects, sorted by uploaded_at descending
        """
        query = self.session.query(FileModel)

        if status:
            query = query.filter(FileModel.status == status)

        return (
            query.order_by(desc(FileModel.uploaded_at))
            .limit(min(limit, 1000))
            .offset(offset)
            .all()
        )

    def count_files(self, status: str | None = None) -> int:
        """
        Count total files.

        Args:
            status: Optional status filter

        Returns:
            Total number of files
        """
        query = self.session.query(FileModel)
        if status:
            query = query.filter(FileModel.status == status)
        return query.count()

    def update_file_status(
        self,
        file_id: UUID | str,
        status: str,
    ) -> FileModel | None:
        """
        Update file status.

        Args:
            file_id: File UUID
            status: New status value

        Returns:
            Updated FileModel if found, None otherwise
        """
        file_record = self.get_file_by_id(file_id)
        if file_record:
            file_record.status = status
            self.session.flush()
            self.session.refresh(file_record)
        return file_record

    def delete_file(self, file_id: UUID | str) -> bool:
        """
        Delete file by ID.

        Args:
            file_id: File UUID

        Returns:
            True if deleted, False if not found
        """
        file_record = self.get_file_by_id(file_id)
        if file_record:
            self.session.delete(file_record)
            self.session.flush()
            return True
        return False
