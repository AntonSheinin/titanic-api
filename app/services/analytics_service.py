"""
    Analytics service class
"""

import logging
from typing import List, Any
import numpy as np
from abc import ABC, abstractmethod

from app.models.responses import HistogramData, HistogramResponse
from app.services.data_service import DataService
from app.utils.validators import validate_percentiles


logger = logging.getLogger(__name__)

class AnalyticsCalculator(ABC):
    """
        Abstract base class for analytics calculations
    """
    
    @abstractmethod
    def calculate(self, data: List[float], **kwargs) -> Any:
        """
            Perform calculation on data
        """

        pass


class FareHistogramCalculator(AnalyticsCalculator):
    """
        Calculator for fare histogram
    """
    
    def calculate(self, data: list, percentiles: int = 10) -> HistogramResponse:
        """
            Calculate fare histogram by percentiles
        """

        validate_percentiles(percentiles)
        
        if not data:
            logger.error("No fare data available for histogram")
            raise ValueError("No fare data available for histogram")
        
        # Convert to numpy array for efficient operations
        fare_array = np.array(data)
        
        # Calculate percentile boundaries using numpy
        percentile_points = np.linspace(0, 100, percentiles + 1)
        boundaries = np.percentile(fare_array, percentile_points)
        
        # Create histogram buckets
        histogram_data = []
        for i in range(len(boundaries) - 1):
            lower_bound = boundaries[i]
            upper_bound = boundaries[i + 1]
            
            # Count values in range using numpy vectorized operations
            if i == len(boundaries) - 2:  # Last bucket includes upper bound
                count = np.sum((fare_array >= lower_bound) & (fare_array <= upper_bound))
            else:
                count = np.sum((fare_array >= lower_bound) & (fare_array < upper_bound))
            
            percentile_value = (i + 1) * (100 / percentiles)
            fare_range = f"{lower_bound:.2f} - {upper_bound:.2f}"
            
            histogram_data.append(HistogramData(
                percentile=percentile_value,
                count=int(count),  # Convert numpy int to Python int
                fare_range=fare_range
            ))
        
        return HistogramResponse(
            data=histogram_data,
            total_passengers=len(data)
        )


class AnalyticsCalculatorFactory:
    """
        Factory for creating analytics calculators
    """
    
    _calculators = {
        "fare_histogram": FareHistogramCalculator,
    }
    
    @classmethod
    def create_calculator(cls, calculator_type: str) -> AnalyticsCalculator:
        """
            Create appropriate analytics calculator
        """

        calculator_class = cls._calculators.get(calculator_type)

        if not calculator_class:
            logger.error(f"Unsupported calculator type: {calculator_type}")
            raise ValueError(f"Unsupported calculator type: {calculator_type}")
        
        return calculator_class()
    
    @classmethod
    def register_calculator(cls, calculator_type: str, calculator_class: type) -> None:
        """
            Register new calculator type
        """

        cls._calculators[calculator_type] = calculator_class


class AnalyticsService:
    """
        Main analytics service
    """
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def get_fare_histogram(self, percentiles: int = 10) -> HistogramResponse:
        """
            Get fare histogram by percentiles
        """
        
        try:
            fare_data = self.data_service.get_fare_data()
            
            fare_histogram_calculator = AnalyticsCalculatorFactory.create_calculator("fare_histogram")
            result = fare_histogram_calculator.calculate(fare_data, percentiles=percentiles)
            
            logger.info(f"Generated fare histogram with {percentiles} percentiles for {len(fare_data)} passengers")
            return result
            
        except Exception as exc:
            logger.error(f"Error generating fare histogram: {exc}")
            raise