"""
    Analytics service class
"""

import logging
import numpy as np
from abc import ABC, abstractmethod

from app.schemas.responses import HistogramData, HistogramResponse
from app.services.data_service import DataService


logger = logging.getLogger(__name__)

class AnalyticsCalculator(ABC):
    """
        Abstract base class for analytics calculations
    """
    
    @abstractmethod
    def calculate(self, data: list[float], **kwargs) -> any:
        """
            Perform calculation on data
        """


class FareHistogramCalculator(AnalyticsCalculator):
    """
        Calculator for fare histogram
    """
    
    def calculate(self, data: list, percentiles: int = 10) -> HistogramResponse:
        """
            Calculate fare histogram by percentiles
        """

        if not data:
            logger.error("No fare data available for histogram")
            raise ValueError("No fare data available for histogram")
        
        fare_array = np.array(data)

        boundaries = np.percentile(np.array(data), np.linspace(0, 100, percentiles + 1))
        
        histogram_data = []

        for i in range(percentiles):
            lower_bound, upper_bound = boundaries[i], boundaries[i + 1]
            inclusive = i == percentiles - 1
            mask = (
                    (fare_array >= lower_bound) &
                    (fare_array <= upper_bound if inclusive else fare_array < upper_bound)
            )

            count = int(np.sum(mask))

            histogram_data.append(HistogramData(
                percentile=(i + 1) * (100 / percentiles),
                count=count,
                fare_range=f"{lower_bound:.2f} - {upper_bound:.2f}"
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


class AnalyticsService:
    """
        Main analytics service
    """
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def get_fare_histogram(self, percentiles: int) -> HistogramResponse:
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
            raise ValueError from exc