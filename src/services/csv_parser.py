"""
Fill Application - CSV Parser Service

Parses CSV files into structured data (list of dictionaries).
Handles different delimiters, encodings, and quote characters.
"""

from csv import DictReader, Error as CSVError, Sniffer
from pathlib import Path
from typing import Any


class CSVParser:
    """
    Parser for CSV files.

    Extracts data from CSV files and converts them to a list of dictionaries,
    where each dictionary represents a row with column headers as keys.

    Supports:
    - Different delimiters (comma, tab, semicolon, pipe)
    - Multiple encodings (utf-8, latin-1, ascii)
    - Quoted fields
    - Auto-detection of delimiter and encoding
    """

    DEFAULT_DELIMITER = ","
    DEFAULT_ENCODING = "utf-8"

    @staticmethod
    def parse_csv(
        file_path: str | Path,
        delimiter: str | None = None,
        encoding: str | None = None,
        skip_empty_rows: bool = True,
        has_headers: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Parse a CSV file and return structured data.

        Args:
            file_path: Path to the CSV file
            delimiter: Delimiter character (comma, tab, semicolon, pipe).
                       If None, auto-detects using csv.Sniffer.
            encoding: File encoding (utf-8, latin-1, ascii).
                      If None, auto-detects by trying common encodings.
            skip_empty_rows: If True, skips rows where all values are empty
            has_headers: If True, treats first row as headers. If False, generates column names.

        Returns:
            List of dictionaries, where each dictionary represents a row with
            column headers as keys and cell values as values.

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid CSV file, has no data, or encoding fails
            CSVError: If the CSV has malformed content

        Examples:
            >>> parser = CSVParser()
            >>> data = parser.parse_csv("data.csv")
            >>> # Returns: [{"Name": "John", "Age": "30"}, ...]

            >>> # Parse tab-separated file
            >>> data = parser.parse_csv("data.tsv", delimiter="\\t")

            >>> # Parse file with no headers
            >>> data = parser.parse_csv("data.csv", has_headers=False)
            >>> # Returns: [{"column1": "John", "column2": "30"}, ...]
        """
        file_path = Path(file_path)

        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file extension (allow .csv, .tsv, .txt for tab/semicolon/pipe delimited)
        valid_extensions = {".csv", ".tsv", ".txt"}
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"Invalid file type. Expected .csv, .tsv, or .txt, got: {file_path.suffix}")

        # Auto-detect encoding if not specified
        if encoding is None:
            encoding = CSVParser._detect_encoding(file_path)
        else:
            encoding = encoding.lower()

        # Parse CSV file
        try:
            # Read file to detect delimiter if needed
            with open(file_path, "r", encoding=encoding) as f:
                sample = f.read(1024)

                if not sample:
                    raise ValueError("CSV file is empty")

                # Auto-detect delimiter if not specified
                if delimiter is None:
                    try:
                        dialect = Sniffer().sniff(sample, delimiters=",;\t|")
                        delimiter = dialect.delimiter
                    except CSVError:
                        # Fallback to default delimiter if sniffing fails
                        delimiter = CSVParser.DEFAULT_DELIMITER

            # Parse the CSV file
            with open(file_path, "r", encoding=encoding, newline="") as f:
                # Create DictReader
                reader = DictReader(
                    f,
                    delimiter=delimiter,
                    skipinitialspace=True,
                )

                # If no headers, generate column names
                if not has_headers:
                    # Read first row to determine number of columns
                    f.seek(0)
                    first_line = f.readline().strip()
                    num_columns = len(first_line.split(delimiter))
                    f.seek(0)

                    # Generate column names
                    fieldnames = [f"column{i+1}" for i in range(num_columns)]
                    reader = DictReader(
                        f,
                        fieldnames=fieldnames,
                        delimiter=delimiter,
                        skipinitialspace=True,
                    )

                # Extract data
                data: list[dict[str, Any]] = []

                for row_dict in reader:
                    # Remove None keys (from trailing delimiters)
                    row_dict = {k: v for k, v in row_dict.items() if k is not None}

                    # Convert values: empty strings to empty string, preserve other types
                    row_data: dict[str, Any] = {}
                    for key, value in row_dict.items():
                        if value is None:
                            processed_value = ""
                        elif isinstance(value, str):
                            # Strip whitespace from string values
                            processed_value = value.strip()
                        else:
                            # Keep other types as-is (shouldn't happen with DictReader)
                            processed_value = value

                        row_data[key] = processed_value

                    # Skip empty rows if requested
                    if skip_empty_rows:
                        # Check if all values are empty strings
                        if all(v == "" for v in row_data.values()):
                            continue

                    # Add row to data
                    # When skip_empty_rows=False, always add the row (even if all empty)
                    # When skip_empty_rows=True, row was already skipped above if empty
                    data.append(row_data)

                # Validate we got some data
                if not data and has_headers:
                    # File has headers but no data rows
                    return []

                if not data and not has_headers:
                    raise ValueError("CSV file has no data rows")

                return data

        except (UnicodeDecodeError, LookupError) as e:
            # LookupError: unknown encoding
            # UnicodeDecodeError: encoding error
            raise ValueError(
                f"Failed to read file with encoding '{encoding}': {e}. "
                f"Try specifying a different encoding (utf-8, latin-1, ascii)."
            ) from e
        except CSVError as e:
            raise ValueError(f"Invalid CSV file format: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}") from e

    @staticmethod
    def _detect_encoding(file_path: Path) -> str:
        """
        Auto-detect file encoding by trying common encodings.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding name

        Raises:
            ValueError: If encoding detection fails
        """
        # Common encodings to try (in order of preference)
        encodings = ["utf-8", "utf-8-sig", "latin-1", "ascii", "cp1252"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    # Try to read a small sample
                    f.read(1024)
                    return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        # If all encodings fail, raise error
        raise ValueError(
            f"Failed to detect file encoding. Tried: {', '.join(encodings)}. "
            "Please specify encoding explicitly."
        )

    @staticmethod
    def detect_delimiter(file_path: str | Path, encoding: str = "utf-8") -> str:
        """
        Detect the delimiter used in a CSV file.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)

        Returns:
            Detected delimiter character

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If delimiter detection fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding=encoding) as f:
            sample = f.read(1024)

            if not sample:
                raise ValueError("CSV file is empty")

            try:
                dialect = Sniffer().sniff(sample, delimiters=",;\t|")
                return dialect.delimiter
            except CSVError:
                # Fallback to default if sniffing fails
                return CSVParser.DEFAULT_DELIMITER
