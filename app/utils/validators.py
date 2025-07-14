from typing import List, Any, Dict


def validate_passenger_id(passenger_id: int) -> None:
    """Validate passenger ID is positive integer."""
    if passenger_id <= 0:
        raise ValueError("Passenger ID must be positive")


def validate_percentiles(percentiles: int) -> None:
    """Validate percentiles parameter."""
    if percentiles < 5 or percentiles > 100:
        raise ValueError("Percentiles must be between 5 and 100")


def validate_attributes(attributes: List[str], available_columns: List[str]) -> None:
    """Validate that requested attributes exist in the dataset."""
    if not attributes:
        raise ValueError("At least one attribute must be specified")
    
    invalid_attributes = [attr for attr in attributes if attr not in available_columns]
    if invalid_attributes:
        raise ValueError(f"Invalid attributes: {', '.join(invalid_attributes)}")


def validate_data_not_empty(data: List[Dict[str, Any]]) -> None:
    """Validate that data is not empty."""
    if not data:
        raise ValueError("No data available")


def validate_fare_data_exists(data: List[Dict[str, Any]]) -> None:
    """Validate fare data exists for histogram analysis."""
    fare_values = [row.get("Fare") for row in data if row.get("Fare") is not None]
    
    if not fare_values:
        raise ValueError("No valid fare data available for analysis")


def clean_passenger_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean passenger data by handling None values."""
    # For MVP, just return as-is since we're not dealing with pandas NaN
    return data