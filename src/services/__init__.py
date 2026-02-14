"""
Fill Application - Services Layer

This package contains business logic services for the fill application.
"""

from src.services.csv_parser import CSVParser
from src.services.excel_parser import ExcelParser
from src.services.mapping_validator import (
    MappingValidationError,
    MappingValidator,
    validate_mapping,
)
from src.services.output_storage import (
    OutputStorage,
    OutputStorageError,
    get_output_storage,
    save_output,
    get_output as get_output_file,
    get_job_outputs,
)
from src.services.parser_factory import get_parser, is_supported_file_type
from src.services.placeholder_parser import (
    PlaceholderParser,
    get_placeholder_parser,
)
from src.services.template_filler import (
    TemplateFiller,
    TemplateFillerError,
    fill_template,
)
from src.services.template_store import TemplateStore, get_template_store
from src.services.batch_processor import (
    BatchProcessor,
    BatchProcessorError,
    process_batch,
)

try:
    from src.services.docx_generator import (
        DocxGenerator,
        DocxGeneratorError,
        generate_docx_from_data,
        generate_docx_from_template,
    )

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

__all__ = [
    "CSVParser",
    "ExcelParser",
    "MappingValidationError",
    "MappingValidator",
    "validate_mapping",
    "OutputStorage",
    "OutputStorageError",
    "get_output_storage",
    "save_output",
    "get_output_file",
    "get_job_outputs",
    "get_parser",
    "is_supported_file_type",
    "PlaceholderParser",
    "get_placeholder_parser",
    "TemplateFiller",
    "TemplateFillerError",
    "fill_template",
    "TemplateStore",
    "get_template_store",
    "BatchProcessor",
    "BatchProcessorError",
    "process_batch",
    "DocxGenerator",
    "DocxGeneratorError",
    "generate_docx_from_data",
    "generate_docx_from_template",
]
