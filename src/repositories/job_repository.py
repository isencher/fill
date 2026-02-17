"""
Fill Application - Job Repository

Database repository for Job and JobOutput model CRUD operations.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from migrations import Job as JobModel, JobOutput as JobOutputModel


class JobRepository:
    """
    Repository for Job database operations.

    Provides CRUD operations for the Job model.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize JobRepository.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create_job(
        self,
        file_id: UUID | str,
        template_id: UUID | str,
        mapping_id: UUID | str,
        total_rows: int = 0,
        status: str = "pending",
    ) -> JobModel:
        """
        Create a new job record.

        Args:
            file_id: File UUID
            template_id: Template UUID
            mapping_id: Mapping UUID
            total_rows: Total number of rows to process
            status: Initial job status

        Returns:
            JobModel: Created job record
        """
        job_record = JobModel(
            file_id=file_id,
            template_id=template_id,
            mapping_id=mapping_id,
            status=status,
            total_rows=total_rows,
            processed_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(job_record)
        self.session.flush()
        self.session.refresh(job_record)
        return job_record

    def get_job_by_id(self, job_id: UUID | str) -> JobModel | None:
        """
        Get job by ID.

        Args:
            job_id: Job UUID

        Returns:
            JobModel if found, None otherwise
        """
        return (
            self.session.query(JobModel)
            .filter(JobModel.id == job_id)
            .first()
        )

    def list_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        file_id: UUID | str | None = None,
    ) -> List[JobModel]:
        """
        List jobs with pagination and filtering.

        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            status: Optional status filter
            file_id: Optional file ID filter

        Returns:
            List of JobModel objects, sorted by created_at descending
        """
        query = self.session.query(JobModel)

        if status:
            query = query.filter(JobModel.status == status)
        if file_id:
            query = query.filter(JobModel.file_id == file_id)

        return (
            query.order_by(desc(JobModel.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_jobs(self, status: str | None = None) -> int:
        """
        Count total jobs.

        Args:
            status: Optional status filter

        Returns:
            Total number of jobs
        """
        query = self.session.query(JobModel)
        if status:
            query = query.filter(JobModel.status == status)
        return query.count()

    def update_job_status(
        self,
        job_id: UUID | str,
        status: str,
        error_message: str | None = None,
    ) -> JobModel | None:
        """
        Update job status.

        Args:
            job_id: Job UUID
            status: New status value
            error_message: Optional error message

        Returns:
            Updated JobModel if found, None otherwise
        """
        job_record = self.get_job_by_id(job_id)
        if job_record:
            job_record.status = status
            job_record.updated_at = datetime.utcnow()
            if error_message is not None:
                job_record.error_message = error_message
            self.session.flush()
            self.session.refresh(job_record)
        return job_record

    def increment_processed_rows(
        self,
        job_id: UUID | str,
        count: int = 1,
    ) -> JobModel | None:
        """
        Increment processed row count.

        Args:
            job_id: Job UUID
            count: Number of rows to increment by

        Returns:
            Updated JobModel if found, None otherwise
        """
        job_record = self.get_job_by_id(job_id)
        if job_record:
            job_record.processed_rows += count
            job_record.updated_at = datetime.utcnow()
            self.session.flush()
            self.session.refresh(job_record)
        return job_record

    def increment_failed_rows(
        self,
        job_id: UUID | str,
        count: int = 1,
    ) -> JobModel | None:
        """
        Increment failed row count.

        Args:
            job_id: Job UUID
            count: Number of rows to increment by

        Returns:
            Updated JobModel if found, None otherwise
        """
        job_record = self.get_job_by_id(job_id)
        if job_record:
            job_record.failed_rows += count
            job_record.updated_at = datetime.utcnow()
            self.session.flush()
            self.session.refresh(job_record)
        return job_record

    def delete_job(self, job_id: UUID | str) -> bool:
        """
        Delete job by ID.

        Args:
            job_id: Job UUID

        Returns:
            True if deleted, False if not found
        """
        job_record = self.get_job_by_id(job_id)
        if job_record:
            self.session.delete(job_record)
            self.session.flush()
            return True
        return False


class JobOutputRepository:
    """
    Repository for JobOutput database operations.

    Provides CRUD operations for the JobOutput model.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize JobOutputRepository.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create_output(
        self,
        job_id: UUID | str,
        filename: str,
        file_path: str,
    ) -> JobOutputModel:
        """
        Create a new job output record.

        Args:
            job_id: Job UUID
            filename: Output filename
            file_path: Path to stored output file

        Returns:
            JobOutputModel: Created job output record
        """
        output_record = JobOutputModel(
            job_id=job_id,
            filename=filename,
            file_path=file_path,
            created_at=datetime.utcnow(),
        )
        self.session.add(output_record)
        self.session.flush()
        self.session.refresh(output_record)
        return output_record

    def get_output_by_id(self, output_id: UUID | str) -> JobOutputModel | None:
        """
        Get job output by ID.

        Args:
            output_id: Output UUID

        Returns:
            JobOutputModel if found, None otherwise
        """
        return (
            self.session.query(JobOutputModel)
            .filter(JobOutputModel.id == output_id)
            .first()
        )

    def get_outputs_by_job(self, job_id: UUID | str) -> List[JobOutputModel]:
        """
        Get all outputs for a job.

        Args:
            job_id: Job UUID

        Returns:
            List of JobOutputModel objects
        """
        return (
            self.session.query(JobOutputModel)
            .filter(JobOutputModel.job_id == job_id)
            .all()
        )

    def get_output_by_job_and_filename(
        self,
        job_id: UUID | str,
        filename: str,
    ) -> JobOutputModel | None:
        """
        Get specific output file for a job.

        Args:
            job_id: Job UUID
            filename: Output filename

        Returns:
            JobOutputModel if found, None otherwise
        """
        return (
            self.session.query(JobOutputModel)
            .filter(
                JobOutputModel.job_id == job_id,
                JobOutputModel.filename == filename,
            )
            .first()
        )

    def list_output_files(self, job_id: UUID | str) -> List[str]:
        """
        List all output filenames for a job.

        Args:
            job_id: Job UUID

        Returns:
            List of filenames
        """
        outputs = self.get_outputs_by_job(job_id)
        return [output.filename for output in outputs]

    def count_outputs(self, job_id: UUID | str) -> int:
        """
        Count outputs for a job.

        Args:
            job_id: Job UUID

        Returns:
            Number of outputs
        """
        return (
            self.session.query(JobOutputModel)
            .filter(JobOutputModel.job_id == job_id)
            .count()
        )

    def delete_job_outputs(self, job_id: UUID | str) -> int:
        """
        Delete all outputs for a job.

        Args:
            job_id: Job UUID

        Returns:
            Number of outputs deleted
        """
        count = (
            self.session.query(JobOutputModel)
            .filter(JobOutputModel.job_id == job_id)
            .delete()
        )
        self.session.flush()
        return count

    def delete_output(self, output_id: UUID | str) -> bool:
        """
        Delete output by ID.

        Args:
            output_id: Output UUID

        Returns:
            True if deleted, False if not found
        """
        output_record = self.get_output_by_id(output_id)
        if output_record:
            self.session.delete(output_record)
            self.session.flush()
            return True
        return False
