"""
Core Processor module for the Fill application.

Provides main data processing logic for transforming and processing data.
"""

from typing import Any


class Processor:
    """
    Main data processor for the Fill application.
    
    Handles data transformation and processing operations.
    """

    def __init__(self):
        """Initialize the processor."""
        pass

    def process(self, data: Any) -> Any:
        """
        Process input data.
        
        For string input, converts to uppercase.
        For other types, returns the data unchanged.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        if isinstance(data, str):
            return data.upper()
        return data
