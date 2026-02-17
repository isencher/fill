"""
Utility helper functions for the Fill application.

Provides common utility functions used across the application.
"""

import os
import re
import uuid
from pathlib import Path
from typing import Any, Generator


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension without dot, lowercase
    """
    return Path(filename).suffix.lstrip(".").lower()


def safe_filename(filename: str) -> str:
    """
    Convert a filename to a safe version.

    Removes or replaces unsafe characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    # Remove path traversal attempts (do this first, before other replacements)
    safe = filename.replace("..", "")
    # Replace path separators and other unsafe chars with underscores
    safe = re.sub(r'[\\/:*?"<>|]', "_", safe)
    # Replace spaces with underscores
    safe = safe.replace(" ", "_")
    # Collapse multiple underscores into one
    safe = re.sub(r'_+', '_', safe)
    return safe


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: Input string
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    
    Args:
        text: Input string
        
    Returns:
        Slug string (lowercase, hyphen-separated)
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    return slug


def is_valid_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_uuid(value: str) -> bool:
    """
    Validate a UUID string.
    
    Args:
        value: String to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    if not value:
        return False
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


def chunk_list(items: list, chunk_size: int) -> Generator[list, None, None]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Yields:
        Chunks of the list
    """
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge (overrides dict1)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def join_paths(*paths: str) -> str:
    """
    Safely join multiple path components.
    
    Args:
        *paths: Path components
        
    Returns:
        Joined path
    """
    return os.path.join(*paths)


def get_relative_path(path: str, base: str) -> str:
    """
    Get the relative path from a base directory.
    
    Args:
        path: Full path
        base: Base directory
        
    Returns:
        Relative path
    """
    return os.path.relpath(path, base)


def normalize_path(path: str) -> str:
    """
    Normalize a path by resolving .. and . components.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path
    """
    return os.path.normpath(path)
