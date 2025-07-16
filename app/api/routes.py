"""
    Passengers API endpoints    
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.services.data_service import DataService
from app.schemas.validators import validate_attributes
from app.services.analytics_service import AnalyticsService
from app.api.dependencies import get_data_service, get_analytics_service
from app.schemas.responses import (
    HistogramResponse,
    PassengersListResponse,
    PassengerResponse,
    PassengerAttributesResponse,
    Passenger
)

logger = logging.getLogger(__name__)

passengers_router = APIRouter(prefix="/passengers", tags=["passengers"])

@passengers_router.get("/", response_model=PassengersListResponse)
async def get_all_passengers(
    data_service: DataService = Depends(get_data_service)
) -> PassengersListResponse:
    """
        Return all passengers
    """

    passengers: list[Passenger] = data_service.get_all_passengers()

    logger.info(f"found {len(passengers)} passengers")
 
    return PassengersListResponse(
        passengers=passengers,
        total_count=len(passengers)
    )


@passengers_router.get("/{passenger_id}", response_model=PassengerResponse | PassengerAttributesResponse)
async def get_passenger(
    passenger_id: int,
    attributes: Annotated[list[str], Query(description="Optional list of specific attributes to retrieve")] = [],
    data_service: DataService = Depends(get_data_service)
) -> PassengerResponse | PassengerAttributesResponse:
    """
        Get passenger by ID. Optionally specify attributes to get only those fields
    """
    
    passenger: Passenger = data_service.get_passenger_by_id(passenger_id)

    if not passenger:
        logger.error(f"passenger with ID {passenger_id} not found")
        raise HTTPException(status_code=404, detail="Passenger not found")

    if not any(attr.strip() for attr in attributes):
        return PassengerResponse(data=passenger)

    try:
        validate_attributes(attributes, Passenger.model_fields.keys())

    except ValueError as exc:
        logger.error(f"Invalid attributes requested: {exc}")
        raise

    result = data_service.get_passenger_attributes(passenger_id, attributes)

    return PassengerAttributesResponse(data=result)


@passengers_router.get("/analytics/fare-histogram", response_model=HistogramResponse)
async def get_fare_histogram(
    percentiles: Annotated[int, Query(ge=5, le=100, description="Number of percentile divisions")] = 10,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> HistogramResponse:
    """
        Get fare histogram by percentiles
    """

    return analytics_service.get_fare_histogram(percentiles)