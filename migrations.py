"""
Database Models for Fill Application

SQLAlchemy ORM models for persistent storage of files, templates, mappings, and jobs.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class File(Base):
    """Uploaded file metadata model."""
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    file_path = Column(String(1024), nullable=False)  # Path to stored file

    # Relationships
    jobs = relationship("Job", back_populates="file")
    mappings = relationship("Mapping", back_populates="file")


class Template(Base):
    """Template metadata model."""
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    placeholders = Column(Text, nullable=False)  # JSON string of list
    file_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    jobs = relationship("Job", back_populates="template")
    mappings = relationship("Mapping", back_populates="template")


class Mapping(Base):
    """Column mapping model."""
    __tablename__ = "mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    column_mappings = Column(Text, nullable=False)  # JSON string of dict
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    file = relationship("File", back_populates="mappings")
    template = relationship("Template", back_populates="mappings")
    jobs = relationship("Job", back_populates="mapping")


class Job(Base):
    """Batch processing job model."""
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    mapping_id = Column(UUID(as_uuid=True), ForeignKey("mappings.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    total_rows = Column(Integer, nullable=False, default=0)
    processed_rows = Column(Integer, nullable=False, default=0)
    failed_rows = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    file = relationship("File", back_populates="jobs")
    template = relationship("Template", back_populates="jobs")
    mapping = relationship("Mapping", back_populates="jobs")
    outputs = relationship("JobOutput", back_populates="job", cascade="all, delete-orphan")


class JobOutput(Base):
    """Generated output document model."""
    __tablename__ = "job_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    filename = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)  # Path to stored file
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="outputs")
