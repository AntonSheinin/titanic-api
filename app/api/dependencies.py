"""
    Dependencies for endpoints
"""

from functools import lru_cache

from app.services.data_service import DataService
from app.services.analytics_service import AnalyticsService


@lru_cache()
def get_data_service() -> DataService:
    """
        Get data service singleton
    """

    return DataService()


@lru_cache()
def get_analytics_service() -> AnalyticsService:
    """
        Get analytics service singleton
    """

    return AnalyticsService(get_data_service())