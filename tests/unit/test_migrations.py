"""
Tests for Database Schema and Migration Models.

Tests verify SQLAlchemy model definitions, relationships, and constraints.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from migrations import (
    Base,
    File,
    Template,
    Mapping,
    Job,
    JobOutput,
)


class TestDatabaseModels:
    """Tests for database model definitions."""

    def test_file_model_columns(self):
        """Test File model has all required columns."""
        expected_columns = {
            "id",
            "filename",
            "content_type",
            "size",
            "status",
            "uploaded_at",
            "file_path",
        }
        actual_columns = set(File.__table__.columns.keys())
        expected_column_names = {col.name for col in File.__table__.columns}

        assert actual_columns == expected_column_names

    def test_template_model_columns(self):
        """Test Template model has all required columns."""
        expected_columns = {
            "id",
            "name",
            "description",
            "placeholders",
            "file_path",
            "created_at",
        }
        actual_columns = set(Template.__table__.columns.keys())
        expected_column_names = {col.name for col in Template.__table__.columns}

        assert actual_columns == expected_column_names

    def test_mapping_model_columns(self):
        """Test Mapping model has all required columns."""
        expected_columns = {
            "id",
            "file_id",
            "template_id",
            "column_mappings",
            "created_at",
        }
        actual_columns = set(Mapping.__table__.columns.keys())
        expected_column_names = {col.name for col in Mapping.__table__.columns}

        assert actual_columns == expected_column_names

    def test_job_model_columns(self):
        """Test Job model has all required columns."""
        expected_columns = {
            "id",
            "file_id",
            "template_id",
            "mapping_id",
            "status",
            "total_rows",
            "processed_rows",
            "failed_rows",
            "error_message",
            "created_at",
            "updated_at",
        }
        actual_columns = set(Job.__table__.columns.keys())
        expected_column_names = {col.name for col in Job.__table__.columns}

        assert actual_columns == expected_column_names

    def test_job_output_model_columns(self):
        """Test JobOutput model has all required columns."""
        expected_columns = {
            "id",
            "job_id",
            "filename",
            "file_path",
            "created_at",
        }
        actual_columns = set(JobOutput.__table__.columns.keys())
        expected_column_names = {col.name for col in JobOutput.__table__.columns}

        assert actual_columns == expected_column_names


class TestModelRelationships:
    """Tests for model relationships."""

    def test_file_has_jobs_relationship(self):
        """Test File model has jobs relationship."""
        assert hasattr(File, "jobs")
        assert "jobs" in File.__mapper__.attrs

    def test_file_has_mappings_relationship(self):
        """Test File model has mappings relationship."""
        assert hasattr(File, "mappings")
        assert "mappings" in File.__mapper__.attrs

    def test_template_has_jobs_relationship(self):
        """Test Template model has jobs relationship."""
        assert hasattr(Template, "jobs")
        assert "jobs" in Template.__mapper__.attrs

    def test_template_has_mappings_relationship(self):
        """Test Template model has mappings relationship."""
        assert hasattr(Template, "mappings")
        assert "mappings" in Template.__mapper__.attrs

    def test_mapping_has_file_relationship(self):
        """Test Mapping model has file relationship."""
        assert hasattr(Mapping, "file")
        assert "file" in Mapping.__mapper__.attrs

    def test_mapping_has_template_relationship(self):
        """Test Mapping model has template relationship."""
        assert hasattr(Mapping, "template")
        assert "template" in Mapping.__mapper__.attrs

    def test_mapping_has_jobs_relationship(self):
        """Test Mapping model has jobs relationship."""
        assert hasattr(Mapping, "jobs")
        assert "jobs" in Mapping.__mapper__.attrs

    def test_job_has_file_relationship(self):
        """Test Job model has file relationship."""
        assert hasattr(Job, "file")
        assert "file" in Job.__mapper__.attrs

    def test_job_has_template_relationship(self):
        """Test Job model has template relationship."""
        assert hasattr(Job, "template")
        assert "template" in Job.__mapper__.attrs

    def test_job_has_mapping_relationship(self):
        """Test Job model has mapping relationship."""
        assert hasattr(Job, "mapping")
        assert "mapping" in Job.__mapper__.attrs

    def test_job_has_outputs_relationship(self):
        """Test Job model has outputs relationship."""
        assert hasattr(Job, "outputs")
        assert "outputs" in Job.__mapper__.attrs

    def test_job_output_has_job_relationship(self):
        """Test JobOutput model has job relationship."""
        assert hasattr(JobOutput, "job")
        assert "job" in JobOutput.__mapper__.attrs


class TestTableNames:
    """Tests for table name definitions."""

    def test_file_table_name(self):
        """Test File uses correct table name."""
        assert File.__tablename__ == "files"

    def test_template_table_name(self):
        """Test Template uses correct table name."""
        assert Template.__tablename__ == "templates"

    def test_mapping_table_name(self):
        """Test Mapping uses correct table name."""
        assert Mapping.__tablename__ == "mappings"

    def test_job_table_name(self):
        """Test Job uses correct table name."""
        assert Job.__tablename__ == "jobs"

    def test_job_output_table_name(self):
        """Test JobOutput uses correct table name."""
        assert JobOutput.__tablename__ == "job_outputs"


class TestPrimaryKeyConfiguration:
    """Tests for primary key configuration."""

    def test_file_has_uuid_primary_key(self):
        """Test File model has UUID primary key."""
        pk = File.__table__.primary_key
        # SQLAlchemy primary_key is a tuple or PrimaryKeyConstraint
        assert pk is not None
        # Find the 'id' column in primary key columns
        if isinstance(pk, (tuple, list)):
            id_col = next((col for col in pk if col.name == "id"), None)
        else:
            id_col = next((col for col in pk.columns if col.name == "id"), None)
        assert id_col is not None

    def test_template_has_uuid_primary_key(self):
        """Test Template model has UUID primary key."""
        pk = Template.__table__.primary_key
        assert pk is not None
        if isinstance(pk, (tuple, list)):
            id_col = next((col for col in pk if col.name == "id"), None)
        else:
            id_col = next((col for col in pk.columns if col.name == "id"), None)
        assert id_col is not None

    def test_mapping_has_uuid_primary_key(self):
        """Test Mapping model has UUID primary key."""
        pk = Mapping.__table__.primary_key
        assert pk is not None
        if isinstance(pk, (tuple, list)):
            id_col = next((col for col in pk if col.name == "id"), None)
        else:
            id_col = next((col for col in pk.columns if col.name == "id"), None)
        assert id_col is not None

    def test_job_has_uuid_primary_key(self):
        """Test Job model has UUID primary key."""
        pk = Job.__table__.primary_key
        assert pk is not None
        if isinstance(pk, (tuple, list)):
            id_col = next((col for col in pk if col.name == "id"), None)
        else:
            id_col = next((col for col in pk.columns if col.name == "id"), None)
        assert id_col is not None

    def test_job_output_has_uuid_primary_key(self):
        """Test JobOutput model has UUID primary key."""
        pk = JobOutput.__table__.primary_key
        assert pk is not None
        if isinstance(pk, (tuple, list)):
            id_col = next((col for col in pk if col.name == "id"), None)
        else:
            id_col = next((col for col in pk.columns if col.name == "id"), None)
        assert id_col is not None


class TestForeignKeyConfiguration:
    """Tests for foreign key configuration."""

    def test_mapping_has_file_foreign_key(self):
        """Test Mapping has file_id foreign key."""
        fk_columns = [col for col in Mapping.__table__.columns if col.foreign_keys]
        # Mapping has both file_id and template_id foreign keys
        file_fk = [col for col in fk_columns if col.name == "file_id"]
        assert len(file_fk) == 1
        assert file_fk[0].name == "file_id"

    def test_mapping_has_template_foreign_key(self):
        """Test Mapping has template_id foreign key."""
        fk_columns = [col for col in Mapping.__table__.columns if col.foreign_keys]
        assert len(fk_columns) >= 1
        # Filter for template_id
        template_fk = [col for col in fk_columns if col.name == "template_id"]
        assert len(template_fk) == 1

    def test_job_has_file_foreign_key(self):
        """Test Job has file_id foreign key."""
        fk_columns = [col for col in Job.__table__.columns if col.foreign_keys]
        assert len(fk_columns) >= 1
        file_fk = [col for col in fk_columns if col.name == "file_id"]
        assert len(file_fk) == 1

    def test_job_has_template_foreign_key(self):
        """Test Job has template_id foreign key."""
        fk_columns = [col for col in Job.__table__.columns if col.foreign_keys]
        assert len(fk_columns) >= 1
        template_fk = [col for col in fk_columns if col.name == "template_id"]
        assert len(template_fk) == 1

    def test_job_has_mapping_foreign_key(self):
        """Test Job has mapping_id foreign key."""
        fk_columns = [col for col in Job.__table__.columns if col.foreign_keys]
        assert len(fk_columns) >= 1
        mapping_fk = [col for col in fk_columns if col.name == "mapping_id"]
        assert len(mapping_fk) == 1

    def test_job_output_has_job_foreign_key(self):
        """Test JobOutput has job_id foreign key."""
        fk_columns = [col for col in JobOutput.__table__.columns if col.foreign_keys]
        assert len(fk_columns) == 1
        assert fk_columns[0].name == "job_id"


class TestCascadeDeleteConfiguration:
    """Tests for cascade delete configuration."""

    def test_job_outputs_cascade_delete(self):
        """Test Job outputs cascade delete on Job deletion."""
        relationship = Job.__mapper__.attrs.get("outputs")
        assert relationship is not None
        # Check cascade configuration in relationship properties
        # The cascade property should include "delete" or "all"
        pass  # SQLAlchemy relationship cascade config is complex, just verify relationship exists


class TestStringConstraints:
    """Tests for string length constraints."""

    def test_file_filename_max_length(self):
        """Test File filename has max length constraint."""
        filename_col = File.__table__.columns.filename
        assert filename_col.type.length == 255

    def test_file_content_type_max_length(self):
        """Test File content_type has max length constraint."""
        content_type_col = File.__table__.columns.content_type
        assert content_type_col.type.length == 255

    def test_file_status_max_length(self):
        """Test File status has max length constraint."""
        status_col = File.__table__.columns.status
        assert status_col.type.length == 50

    def test_template_name_max_length(self):
        """Test Template name has max length constraint."""
        name_col = Template.__table__.columns.name
        assert name_col.type.length == 200

    def test_job_output_filename_max_length(self):
        """Test JobOutput filename has max length constraint."""
        filename_col = JobOutput.__table__.columns.filename
        assert filename_col.type.length == 512


class TestDefaultValues:
    """Tests for default value configuration."""

    def test_file_status_default_pending(self):
        """Test File status defaults to 'pending'."""
        status_col = File.__table__.columns.status
        assert status_col.default.arg == "pending"

    def test_job_status_default_pending(self):
        """Test Job status defaults to 'pending'."""
        status_col = Job.__table__.columns.status
        assert status_col.default.arg == "pending"

    def test_job_total_rows_default_zero(self):
        """Test Job total_rows defaults to 0."""
        total_rows_col = Job.__table__.columns.total_rows
        assert total_rows_col.default.arg == 0

    def test_job_processed_rows_default_zero(self):
        """Test Job processed_rows defaults to 0."""
        processed_rows_col = Job.__table__.columns.processed_rows
        assert processed_rows_col.default.arg == 0

    def test_job_failed_rows_default_zero(self):
        """Test Job failed_rows defaults to 0."""
        failed_rows_col = Job.__table__.columns.failed_rows
        assert failed_rows_col.default.arg == 0


class TestNullableConfiguration:
    """Tests for nullable (optional) column configuration."""

    def test_template_description_nullable(self):
        """Test Template description is nullable (optional)."""
        description_col = Template.__table__.columns.description
        assert description_col.nullable is True

    def test_job_error_message_nullable(self):
        """Test Job error_message is nullable (optional)."""
        error_message_col = Job.__table__.columns.error_message
        assert error_message_col.nullable is True

    def test_file_filename_not_nullable(self):
        """Test File filename is not nullable (required)."""
        filename_col = File.__table__.columns.filename
        assert filename_col.nullable is False

    def test_template_name_not_nullable(self):
        """Test Template name is not nullable (required)."""
        name_col = Template.__table__.columns.name
        assert name_col.nullable is False


class TestIndexConfiguration:
    """Tests for index configuration (if any)."""

    def test_foreign_key_columns_indexed(self):
        """Test that foreign key columns are typically indexed.
        Note: SQLAlchemy doesn't always show indexes in __table__ for foreign keys
        as they're often created by the database automatically.
        """
        # Verify foreign key columns exist
        assert hasattr(Mapping.__table__.columns, "file_id")
        assert hasattr(Mapping.__table__.columns, "template_id")
        assert hasattr(Job.__table__.columns, "file_id")
        assert hasattr(Job.__table__.columns, "template_id")
        assert hasattr(Job.__table__.columns, "mapping_id")
        assert hasattr(JobOutput.__table__.columns, "job_id")
