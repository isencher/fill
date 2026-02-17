"""
Fill Application - Batch Processing Service

Processes batch jobs to fill templates with data from uploaded files.
Iterates through file rows, fills templates, and generates outputs.
"""

from pathlib import Path
from typing import Any
from uuid import UUID

from src.models.job import Job, JobStatus
from src.models.mapping import Mapping
from src.models.template import Template
from src.services.parser_factory import get_parser
from src.services.template_filler import TemplateFiller, TemplateFillerError


class BatchProcessorError(Exception):
    """
    Custom exception for batch processing errors.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize batch processor error.

        Args:
            message: Error message describing what went wrong
        """
        self.message = message
        super().__init__(self.message)


class BatchProcessor:
    """
    Processes batch jobs for filling templates with data.

    Workflow:
    1. Parse uploaded file to extract data rows
    2. Iterate through each data row
    3. Fill template with row data using mapping
    4. Save generated output
    5. Update job progress and status

    Handles:
    - File parsing (CSV, Excel)
    - Template filling (text, DOCX)
    - Progress tracking
    - Error handling and recovery
    """

    def __init__(self, output_dir: str | Path | None = None) -> None:
        """
        Initialize the batch processor.

        Args:
            output_dir: Optional directory to save generated outputs.
                      If None, outputs are returned as bytes (not implemented yet).
        """
        self._output_dir = Path(output_dir) if output_dir else None

    def process_batch(
        self,
        file_path: str | Path,
        template_path: str | Path,
        mapping: Mapping,
        job: Job,
        missing_placeholder_strategy: str = "keep",
    ) -> dict[UUID, bytes]:
        """
        Process a batch job to fill template with file data.

        Args:
            file_path: Path to uploaded data file (CSV or Excel)
            template_path: Path to template file
            mapping: Column-to-placeholder mapping
            job: Job object to track progress
            missing_placeholder_strategy: Strategy for missing values
                - "keep": Keep placeholder (default)
                - "empty": Replace with empty string
                - "default": Replace with "N/A"

        Returns:
            Dictionary mapping row index to generated output bytes

        Raises:
            BatchProcessorError: If processing fails critically
            TemplateFillerError: If template filling fails
        """
        # Convert paths to Path objects
        file_path = Path(file_path)
        template_path = Path(template_path)

        # Validate inputs
        if not file_path.exists():
            raise BatchProcessorError(
                f"File not found: {file_path}"
            )

        if not template_path.exists():
            raise BatchProcessorError(
                f"Template not found: {template_path}"
            )

        # Update job status to processing
        job.set_status(JobStatus.PROCESSING)

        # Parse file to get data rows
        try:
            parser_class = get_parser(file_path)
            parser = parser_class()

            # Parse based on file type
            if file_path.suffix.lower() in {".csv", ".tsv", ".txt"}:
                data_rows = parser.parse_csv(file_path)
            elif file_path.suffix.lower() in {".xlsx", ".xls"}:
                data_rows = parser.parse_excel(file_path)
            else:
                raise BatchProcessorError(
                    f"Unsupported file type: {file_path.suffix}"
                )
        except Exception as e:
            job.set_error(f"Failed to parse file: {e}")
            raise BatchProcessorError(
                f"File parsing failed: {e}"
            )

        # Update job total rows
        job.total_rows = len(data_rows)

        # Initialize template filler
        try:
            filler = TemplateFiller(
                missing_placeholder_strategy=missing_placeholder_strategy
            )
        except Exception as e:
            job.set_error(f"Failed to initialize template filler: {e}")
            raise BatchProcessorError(
                f"Template filler initialization failed: {e}"
            )

        # Process each row
        outputs = {}
        for index, row_data in enumerate(data_rows):
            try:
                # Fill template with row data
                output_bytes = filler.fill_template(
                    template_path, row_data, mapping
                )

                # Store output
                outputs[index] = output_bytes

                # Save to file if output directory specified
                if self._output_dir:
                    self._save_output(
                        index, output_bytes, job.id
                    )

                # Update progress
                job.increment_processed()

            except Exception as e:
                # Log error but continue processing
                job.increment_failed()
                # Note: We could collect errors per row here
                # For now, just continue with next row
                continue

        # Update job status based on results
        if job.failed_rows > 0:
            # Job completed with some failures
            if job.processed_rows > 0:
                # Partial success
                job.set_status(JobStatus.COMPLETED)
            else:
                # Complete failure
                job.set_error(
                    f"All {job.total_rows} rows failed to process"
                )
        else:
            # Complete success
            job.set_status(JobStatus.COMPLETED)

        return outputs

    def process_batch_async(
        self,
        file_path: str | Path,
        template_path: str | Path,
        mapping: Mapping,
        job: Job,
        missing_placeholder_strategy: str = "keep",
    ) -> dict[UUID, bytes]:
        """
        Process batch job asynchronously (placeholder for future implementation).

        Currently processes synchronously. Future implementation will use
        background tasks or async processing.

        Args:
            file_path: Path to uploaded data file
            template_path: Path to template file
            mapping: Column-to-placeholder mapping
            job: Job object to track progress
            missing_placeholder_strategy: Strategy for missing values

        Returns:
            Dictionary mapping row index to generated output bytes
        """
        # For now, just call synchronous version
        return self.process_batch(
            file_path,
            template_path,
            mapping,
            job,
            missing_placeholder_strategy,
        )

    def _save_output(
        self,
        row_index: int,
        output_bytes: bytes,
        job_id: UUID,
    ) -> None:
        """
        Save generated output to file.

        Args:
            row_index: Index of the data row
            output_bytes: Generated document bytes
            job_id: ID of the job

        Raises:
            BatchProcessorError: If output directory is not set or save fails
        """
        if not self._output_dir:
            raise BatchProcessorError(
                "Output directory not specified"
            )

        try:
            # Create job directory
            job_dir = self._output_dir / str(job_id)
            job_dir.mkdir(parents=True, exist_ok=True)

            # Determine file extension
            # For now, assume .docx for all outputs
            # TODO: Detect based on template type
            output_path = job_dir / f"output_{row_index}.docx"

            # Write output file
            with open(output_path, "wb") as f:
                f.write(output_bytes)

        except Exception as e:
            raise BatchProcessorError(
                f"Failed to save output: {e}"
            )


def process_batch(
    file_path: str | Path,
    template_path: str | Path,
    mapping: Mapping,
    job: Job,
    missing_placeholder_strategy: str = "keep",
    output_dir: str | Path | None = None,
) -> dict[int, bytes]:
    """
    Convenience function to process a batch job.

    Args:
        file_path: Path to uploaded data file (CSV or Excel)
        template_path: Path to template file
        mapping: Column-to-placeholder mapping
        job: Job object to track progress
        missing_placeholder_strategy: Strategy for missing values
        output_dir: Optional directory to save outputs

    Returns:
        Dictionary mapping row index to generated output bytes

    Raises:
        BatchProcessorError: If processing fails critically
    """
    processor = BatchProcessor(output_dir=output_dir)
    return processor.process_batch(
        file_path,
        template_path,
        mapping,
        job,
        missing_placeholder_strategy,
    )
