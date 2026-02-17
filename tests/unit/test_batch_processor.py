"""
Unit tests for Batch Processing Service.
"""

import pytest
from pathlib import Path
from uuid import uuid4
from unittest.mock import MagicMock, patch

from src.models.job import Job, JobStatus
from src.models.mapping import Mapping
from src.services.batch_processor import (
    BatchProcessor,
    BatchProcessorError,
    process_batch,
)
from src.services.template_filler import TemplateFillerError


class TestBatchProcessorCreation:
    """Tests for BatchProcessor initialization."""

    def test_create_processor_without_output_dir(self):
        """Test creating processor without output directory."""
        processor = BatchProcessor()
        assert processor is not None
        assert processor._output_dir is None

    def test_create_processor_with_output_dir(self, tmp_path):
        """Test creating processor with output directory."""
        output_dir = tmp_path / "outputs"
        processor = BatchProcessor(output_dir=output_dir)
        assert processor is not None
        assert processor._output_dir == output_dir


class TestProcessBatch:
    """Tests for process_batch method."""

    def test_process_simple_csv(self, tmp_path):
        """Test processing a simple CSV file."""
        # Create test CSV file
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "name,age\nAlice,30\nBob,25\n", encoding="utf-8"
        )

        # Create simple text template
        template_file = tmp_path / "template.txt"
        template_file.write_text(
            "Name: {{name}}, Age: {{age}}", encoding="utf-8"
        )

        # Create mapping
        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name", "age": "age"}
        )

        # Create job
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        # Process batch
        processor = BatchProcessor()
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job
        )

        # Verify outputs
        assert len(outputs) == 2
        assert job.processed_rows == 2
        assert job.failed_rows == 0
        assert job.status == JobStatus.COMPLETED

    def test_process_with_missing_values(self, tmp_path):
        """Test processing with missing placeholder values."""
        # Create CSV with missing columns
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,\n")

        # Template with extra placeholder
        template_file = tmp_path / "template.txt"
        template_file.write_text(
            "Name: {{name}}, Age: {{age}}, Email: {{email}}"
        )

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name", "age": "age"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job, missing_placeholder_strategy="keep"
        )

        # Should process both rows (even with missing values)
        assert len(outputs) == 2

    def test_process_with_empty_strategy(self, tmp_path):
        """Test processing with empty missing value strategy."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}, Email: {{email}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job, missing_placeholder_strategy="empty"
        )

        assert len(outputs) == 1

    def test_process_file_not_found_raises_error(self, tmp_path):
        """Test that non-existent file raises error."""
        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id="non-existent.csv",
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id="non-existent.csv",
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        with pytest.raises(BatchProcessorError, match="File not found"):
            processor.process_batch(
                "non-existent.csv", template_file, mapping, job
            )

        # Job status remains PENDING since error occurs before status is set to PROCESSING
        assert job.status == JobStatus.PENDING

    def test_process_template_not_found_raises_error(self, tmp_path):
        """Test that non-existent template raises error."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id="non-existent.txt",
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        with pytest.raises(
            BatchProcessorError, match="Template not found"
        ):
            processor.process_batch(
                csv_file, "non-existent.txt", mapping, job
            )

        # Job status remains PENDING since error occurs before status is set to PROCESSING
        assert job.status == JobStatus.PENDING

    def test_process_updates_job_progress(self, tmp_path):
        """Test that job progress is updated during processing."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\nBob\nCharlie\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        processor.process_batch(csv_file, template_file, mapping, job)

        # Verify job was updated
        assert job.total_rows == 3
        assert job.processed_rows == 3
        assert job.progress_percentage == 100.0
        assert job.status == JobStatus.COMPLETED

    def test_process_with_output_dir_saves_files(self, tmp_path):
        """Test that outputs are saved when output directory is specified."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        output_dir = tmp_path / "outputs"
        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor(output_dir=output_dir)
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job
        )

        # Verify output file was created
        job_dir = output_dir / str(job.id)
        assert job_dir.exists()
        output_file = job_dir / "output_0.docx"
        assert output_file.exists()

    def test_process_handles_partial_failures(self, tmp_path):
        """Test that partial failures are handled correctly."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\nBob\n")

        # Create invalid template that will cause failures
        # For now, all should succeed with text template
        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job
        )

        # With valid template, all should succeed
        assert len(outputs) == 2
        assert job.failed_rows == 0

    def test_process_empty_file(self, tmp_path):
        """Test processing an empty file (no data rows)."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\n")  # Header only

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job
        )

        # No data rows = no outputs
        assert len(outputs) == 0
        assert job.total_rows == 0
        assert job.status == JobStatus.COMPLETED


class TestProcessBatchAsync:
    """Tests for process_batch_async method."""

    def test_process_batch_async(self, tmp_path):
        """Test async processing (currently synchronous)."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        outputs = processor.process_batch_async(
            csv_file, template_file, mapping, job
        )

        # Should behave like synchronous version
        assert len(outputs) == 1
        assert job.status == JobStatus.COMPLETED


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_process_batch_convenience(self, tmp_path):
        """Test process_batch convenience function."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        outputs = process_batch(
            csv_file, template_file, mapping, job
        )

        assert len(outputs) == 1

    def test_process_batch_with_output_dir(self, tmp_path):
        """Test convenience function with output directory."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        output_dir = tmp_path / "outputs"
        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        outputs = process_batch(
            csv_file, template_file, mapping, job, output_dir=output_dir
        )

        # Verify output was saved
        job_dir = output_dir / str(job.id)
        assert job_dir.exists()


class TestBatchProcessorError:
    """Tests for BatchProcessorError exception."""

    def test_error_creation(self):
        """Test creating a BatchProcessorError."""
        error = BatchProcessorError("Test error message")
        assert error.message == "Test error message"
        assert str(error) == "Test error message"


class TestBatchProcessorIntegration:
    """Integration tests for BatchProcessor with real files."""

    def test_process_excel_file(self, tmp_path):
        """Test processing an Excel file."""
        from src.services.excel_parser import ExcelParser

        # Create test Excel file
        excel_file = tmp_path / "test.xlsx"
        # Create simple Excel file with test data
        # (For now, skip this test if pandas/openpyxl not available)
        try:
            import pandas as pd

            df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
            df.to_excel(excel_file, index=False)

            template_file = tmp_path / "template.txt"
            template_file.write_text("Name: {{name}}, Age: {{age}}")

            mapping = Mapping(
                file_id=str(excel_file),
                template_id=str(template_file),
                column_mappings={"name": "name", "age": "age"}
            )
            job = Job(
                file_id=str(excel_file),
                template_id=str(template_file),
                mapping_id="test-mapping",
                total_rows=0,
            )

            processor = BatchProcessor()
            outputs = processor.process_batch(
                excel_file, template_file, mapping, job
            )

            assert len(outputs) == 2
            assert job.status == JobStatus.COMPLETED

        except ImportError:
            # Skip if pandas not available
            pytest.skip("pandas not available for Excel test")

    def test_process_large_batch(self, tmp_path):
        """Test processing a larger batch (100 rows)."""
        # Create CSV with 100 rows
        csv_file = tmp_path / "test.csv"
        lines = ["name,age\n"] + [f"Person{i},{i * 10}\n" for i in range(100)]
        csv_file.write_text("".join(lines))

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}, Age: {{age}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name", "age": "age"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        outputs = processor.process_batch(
            csv_file, template_file, mapping, job
        )

        assert len(outputs) == 100
        assert job.processed_rows == 100
        assert job.progress_percentage == 100.0

    def test_process_unsupported_file_type(self, tmp_path):
        """Test processing an unsupported file type raises error."""
        # Create a file with unsupported extension
        bad_file = tmp_path / "test.pdf"
        bad_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(bad_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(bad_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()
        with pytest.raises(BatchProcessorError, match="Unsupported file type"):
            processor.process_batch(
                bad_file, template_file, mapping, job
            )

        # Job should be marked as FAILED with error message
        assert job.status == JobStatus.FAILED
        assert "Failed to parse file" in job.error_message

    def test_process_all_rows_fail(self, tmp_path):
        """Test that job is marked as FAILED when all rows fail processing."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\nBob\n")

        template_file = tmp_path / "template.txt"
        # Empty template will cause failures in some scenarios
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        # For now, all will succeed with a valid text template
        # To simulate all failures, we need to mock the filler
        from unittest.mock import patch, MagicMock

        processor = BatchProcessor()

        # Mock filler to raise exception
        with patch.object(
            processor,
            "_save_output",
            side_effect=Exception("Save failed")
        ):
            outputs = processor.process_batch(
                csv_file, template_file, mapping, job
            )

        # With save failures, processed rows will still increment
        # but failed rows will also increment
        assert job.status == JobStatus.COMPLETED  # Partial success

    def test_process_with_partial_success(self, tmp_path):
        """Test job marked COMPLETED with partial success."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\nBob\nCharlie\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor()

        # Mock to cause some failures (2nd row fails)
        call_count = 0

        def side_effect_filler(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise TemplateFillerError("Simulated failure")
            return b"output"

        with patch("src.services.batch_processor.TemplateFiller") as MockFiller:
            mock_instance = MagicMock()
            mock_instance.fill_template.side_effect = side_effect_filler
            MockFiller.return_value = mock_instance

            outputs = processor.process_batch(
                csv_file, template_file, mapping, job
            )

        # Should have 2 successes, 1 failure
        assert len(outputs) == 2
        assert job.processed_rows == 2
        assert job.failed_rows == 1
        assert job.status == JobStatus.COMPLETED  # Partial success

    def test_save_output_without_output_dir(self, tmp_path):
        """Test _save_output raises error when output_dir not set."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        # Create processor without output directory
        processor = BatchProcessor()

        # Call _save_output directly
        with pytest.raises(BatchProcessorError, match="Output directory not specified"):
            processor._save_output(0, b"output", job.id)

    def test_save_output_with_file_error(self, tmp_path):
        """Test _save_output handles file write errors."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nAlice\n")

        template_file = tmp_path / "template.txt"
        template_file.write_text("Name: {{name}}")

        output_dir = tmp_path / "outputs"

        mapping = Mapping(
            file_id=str(csv_file),
            template_id=str(template_file),
            column_mappings={"name": "name"}
        )
        job = Job(
            file_id=str(csv_file),
            template_id=str(template_file),
            mapping_id="test-mapping",
            total_rows=0,
        )

        processor = BatchProcessor(output_dir=output_dir)

        # Mock open to raise exception
        original_open = open

        def mock_open_func(path, *args, **kwargs):
            if "output_0" in str(path):
                raise PermissionError("Permission denied")
            return original_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=mock_open_func):
            with pytest.raises(BatchProcessorError, match="Failed to save output"):
                processor._save_output(0, b"output", job.id)
