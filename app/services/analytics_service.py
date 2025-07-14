import logging
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from app.models.responses import HistogramData, HistogramResponse
from app.services.data_service import DataService
from app.utils.validators import validate_percentiles

logger = logging.getLogger(__name__)


class AnalyticsCalculator(ABC):
    """Abstract base class for analytics calculations."""
    
    @abstractmethod
    def calculate(self, data: List[float], **kwargs) -> Any:
        """Perform calculation on data."""
        pass


class PercentileCalculator:
    """Helper class for percentile calculations."""
    
    @staticmethod
    def calculate_percentiles(data: List[float], num_percentiles: int) -> List[float]:
        """Calculate percentile boundaries."""
        if not data:
            return []
        
        sorted_data = sorted(data)
        boundaries = []
        
        for i in range(num_percentiles + 1):
            percentile = i * 100 / num_percentiles
            index = int(percentile / 100 * (len(sorted_data) - 1))
            boundaries.append(sorted_data[index])
        
        return boundaries


class FareHistogramCalculator(AnalyticsCalculator):
    """Calculator for fare histogram analysis."""
    
    def __init__(self):
        self.percentile_calculator = PercentileCalculator()
    
    def calculate(self, data: List[float], percentiles: int = 10) -> HistogramResponse:
        """Calculate fare histogram by percentiles."""
        validate_percentiles(percentiles)
        
        if not data:
            raise ValueError("No fare data available for histogram")
        
        boundaries = self.percentile_calculator.calculate_percentiles(data, percentiles)
        histogram_data = self._create_histogram_buckets(data, boundaries, percentiles)
        
        return HistogramResponse(
            data=histogram_data,
            total_passengers=len(data)
        )
    
    def _create_histogram_buckets(self, data: List[float], boundaries: List[float], percentiles: int) -> List[HistogramData]:
        """Create histogram buckets from boundaries."""
        histogram_data = []
        
        for i in range(len(boundaries) - 1):
            lower_bound = boundaries[i]
            upper_bound = boundaries[i + 1]
            
            count = self._count_values_in_range(data, lower_bound, upper_bound, is_last_bucket=(i == len(boundaries) - 2))
            percentile_value = (i + 1) * (100 / percentiles)
            fare_range = f"{lower_bound:.2f} - {upper_bound:.2f}"
            
            histogram_data.append(HistogramData(
                percentile=percentile_value,
                count=count,
                fare_range=fare_range
            ))
        
        return histogram_data
    
    def _count_values_in_range(self, data: List[float], lower: float, upper: float, is_last_bucket: bool = False) -> int:
        """Count values in specified range."""
        if is_last_bucket:
            # Include upper bound for last bucket
            return len([value for value in data if lower <= value <= upper])
        else:
            # Exclude upper bound for other buckets
            return len([value for value in data if lower <= value < upper])


class AnalyticsCalculatorFactory:
    """Factory for creating analytics calculators."""
    
    _calculators = {
        "fare_histogram": FareHistogramCalculator,
    }
    
    @classmethod
    def create_calculator(cls, calculator_type: str) -> AnalyticsCalculator:
        """Create appropriate analytics calculator."""
        calculator_class = cls._calculators.get(calculator_type)
        if not calculator_class:
            raise ValueError(f"Unsupported calculator type: {calculator_type}")
        return calculator_class()
    
    @classmethod
    def register_calculator(cls, calculator_type: str, calculator_class: type) -> None:
        """Register new calculator type."""
        cls._calculators[calculator_type] = calculator_class


class AnalyticsService:
    """Main analytics service using strategy pattern."""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def get_fare_histogram(self, percentiles: int = 10) -> HistogramResponse:
        """Get fare histogram by percentiles."""
        try:
            fare_data = self.data_service.get_fare_data()
            
            calculator = AnalyticsCalculatorFactory.create_calculator("fare_histogram")
            result = calculator.calculate(fare_data, percentiles=percentiles)
            
            logger.info(f"Generated fare histogram with {percentiles} percentiles for {len(fare_data)} passengers")
            return result
            
        except Exception as e:
            logger.error(f"Error generating fare histogram: {e}")
            raise