"""
    Validators module for pydantic models    
"""

import logging


logger = logging.getLogger(__name__)

def validate_attributes(attributes: list, available_columns: list) -> None:
    """
        Validate that requested attributes exist in the dataset.
    """

    invalid_attributes = [attr for attr in attributes if attr not in available_columns]

    if invalid_attributes:
        logger.error(f"Invalid attributes requested: {invalid_attributes}")
        raise ValueError(f"Invalid attributes requested: {invalid_attributes}")

def validate_data_not_empty(data: list) -> None:
    """
        Validate that data is not empty.
    """
        
    if not data:
        logger.error("Empty data provided to validator")
        raise ValueError("No data available")