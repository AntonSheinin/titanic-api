"""
    Passengers API endpoints    
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.models.responses import HistogramResponse, PassengersListResponse
from app.services.data_service import DataService
from app.services.analytics_service import AnalyticsService
from app.api.dependencies import get_data_service, get_analytics_service


logger = logging.getLogger(__name__)

passengers_router = APIRouter(prefix="/passengers", tags=["passengers"])

@passengers_router.get("/", response_model=PassengersListResponse)
async def get_all_passengers(
    data_service: DataService = Depends(get_data_service)
) -> PassengersListResponse:
    """
        Return all passengers
    """

    passengers = data_service.get_all_passengers()

    logger.info(f"found {len(passengers)} passengers")
 
    return PassengersListResponse(
        passengers=[passenger.model_dump() for passenger in passengers],
        total_count=len(passengers)
    )


@passengers_router.get("/{passenger_id}")
async def get_passenger(
    passenger_id: int,
    attributes: list = Query([], description="Optional list of specific attributes to retrieve"),
    data_service: DataService = Depends(get_data_service)
) -> dict:
    """
        Get passenger by ID. Optionally specify attributes to get only those fields
    """
    
    passenger = data_service.get_passenger_by_id(passenger_id)

    if not passenger:
        logger.error(f"passenger with ID {passenger_id} not found")
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    if not attributes:
        return {"data": passenger.model_dump()}
    
    result = data_service.get_passenger_attributes(passenger_id, attributes)

    return {"data": result}


@passengers_router.get("/analytics/fare-histogram", response_model=HistogramResponse)
async def get_fare_histogram(
    percentiles: int = Query(10, ge=5, le=100, description="Number of percentile divisions"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> HistogramResponse:
    """
        Get fare histogram by percentiles
    """

    return analytics_service.get_fare_histogram(percentiles)