"""
Fill Application - Parser Factory

Factory function to return the appropriate parser based on file extension.
Supports CSV and Excel file formats.
"""

from pathlib import Path
from typing import Protocol

from src.services.csv_parser import CSVParser
from src.services.excel_parser import ExcelParser


class ParserProtocol(Protocol):
    """
    Protocol defining the interface for file parsers.

    All parsers must implement these methods to be compatible
    with the parser factory.
    """

    def parse_csv(
        self,
        file_path: str | Path,
        delimiter: str | None = None,
        encoding: str | None = None,
        skip_empty_rows: bool = True,
        has_headers: bool = True,
    ) -> list[dict[str, object]]:
        """Parse a CSV file and return structured data."""
        ...

    def parse_excel(
        self,
        file_path: str | Path,
        sheet_name: str | int = 0,
        skip_empty_rows: bool = True,
    ) -> list[dict[str, object]]:
        """Parse an Excel file and return structured data."""
        ...


def get_parser(file_path: str | Path) -> type[CSVParser] | type[ExcelParser]:
    """
    Return the appropriate parser class based on file extension.

    This factory function determines which parser to use based on the file
    extension. It supports:
    - CSV files: .csv, .tsv, .txt
    - Excel files: .xlsx, .xlsm

    Args:
        file_path: Path to the file to parse

    Returns:
        Parser class (CSVParser or ExcelParser)

    Raises:
        ValueError: If file extension is not supported

    Examples:
        >>> parser = get_parser("data.csv")
        >>> parser == CSVParser
        True

        >>> parser = get_parser("data.xlsx")
        >>> parser == ExcelParser
        True

        >>> parser = get_parser("data.tsv")
        >>> parser == CSVParser
        True

        >>> parser = get_parser("data.txt")
        >>> parser == CSVParser
        True

        >>> parser = get_parser("data.json")
        ValueError: Unsupported file type: .json. Supported types: .csv, .tsv, .txt, .xlsx, .xlsm
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    # CSV file extensions (including tab-separated and text files)
    csv_extensions = {".csv", ".tsv", ".txt"}
    if extension in csv_extensions:
        return CSVParser

    # Excel file extensions
    excel_extensions = {".xlsx", ".xlsm"}
    if extension in excel_extensions:
        return ExcelParser

    # Unsupported file type
    supported_types = ", ".join(sorted(csv_extensions | excel_extensions))
    raise ValueError(
        f"Unsupported file type: {extension}. "
        f"Supported types: {supported_types}"
    )


def is_supported_file_type(file_path: str | Path) -> bool:
    """
    Check if a file type is supported by the parser factory.

    Args:
        file_path: Path to the file

    Returns:
        True if file type is supported, False otherwise

    Examples:
        >>> is_supported_file_type("data.csv")
        True

        >>> is_supported_file_type("data.json")
        False
    """
    try:
        get_parser(file_path)
        return True
    except ValueError:
        return False
