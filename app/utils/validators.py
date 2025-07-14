"""
    Validators module for pydantic models    
"""

import logging


logger = logging.getLogger(__name__)


def validate_passenger_id(passenger_id: int) -> None:
    """
        Validate passenger ID is positive integer.
    """
    
    if passenger_id <= 0:
        logger.error(f"Passenger ID must be positive, ID provided: {passenger_id}")
        raise ValueError(f"Passenger ID must be positive, ID provided: {passenger_id}")

def validate_percentiles(percentiles: int) -> None:
    """
        Validate percentiles parameter.
    """
   
    if percentiles not in range(5, 101):
        logger.error(f"Percentiles must be between 5 and 100, value provided: {percentiles}")
        raise ValueError(f"Percentiles must be between 5 and 100, value provided: {percentiles}")

def validate_attributes(attributes: list, available_columns: list) -> None:
    """
        Validate that requested attributes exist in the dataset.
    """
    
    if not attributes:
        logger.warning("At least one attribute must be specified, empty attributes list provided")
        raise ValueError("At least one attribute must be specified, empty attributes list provided")
    
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

def validate_fare_data_exists(data: list) -> None:
    """
        Validate fare data exists for histogram analysis.
    """
    
    fare_values = [row.get("Fare") for row in data if row.get("Fare") is not None]
    
    if not fare_values:
        logger.error("No valid fare data found in dataset")
        raise ValueError("No valid fare data found in dataset")