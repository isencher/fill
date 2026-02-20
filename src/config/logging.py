"""
Structured logging configuration for the Fill application.

This module sets up logging with both file and console handlers,
and configures appropriate log levels for different components.
"""

import logging
import sys
from pathlib import Path


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Creates a logs directory and sets up logging to both file
    and console with appropriate formatting.
    """
    logs_dir = Path(".logs")
    logs_dir.mkdir(exist_ok=True)

    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=format_string,
        handlers=[
            logging.FileHandler(logs_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set specific log levels to reduce noise
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
