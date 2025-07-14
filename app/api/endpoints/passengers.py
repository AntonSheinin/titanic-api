from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any

from app.models.passenger import Passenger
from app.models.responses import HistogramResponse, PassengerAttributesResponse, PassengersListResponse
from app.services.data_service import DataService
from app.services.analytics_service import AnalyticsService
from app.api.dependencies import get_data_service, get_analytics_service

router = APIRouter()


@router.get("/", response_model=PassengersListResponse)
async def get_all_passengers(
    data_service: DataService = Depends(get_data_service)
) -> PassengersListResponse:
    """Return all passengers."""
    passengers = data_service.get_all_passengers()
    return PassengersListResponse(
        passengers=[p.model_dump() for p in passengers],
        total_count=len(passengers)
    )


@router.get("/{passenger_id}", response_model=Passenger)
async def get_passenger(
    passenger_id: int,
    data_service: DataService = Depends(get_data_service)
) -> Passenger:
    """Get passenger by ID."""
    passenger = data_service.get_passenger_by_id(passenger_id)
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")
    return passenger


@router.get("/{passenger_id}/attributes", response_model=PassengerAttributesResponse)
async def get_passenger_attributes(
    passenger_id: int,
    attributes: List[str] = Query(..., description="List of attributes to retrieve"),
    data_service: DataService = Depends(get_data_service)
) -> PassengerAttributesResponse:
    """Get specific attributes for a passenger."""
    result = data_service.get_passenger_attributes(passenger_id, attributes)
    if not result:
        raise HTTPException(status_code=404, detail="Passenger not found")
    return PassengerAttributesResponse(data=result)


@router.get("/analytics/fare-histogram", response_model=HistogramResponse)
async def get_fare_histogram(
    percentiles: int = Query(10, ge=5, le=100, description="Number of percentile divisions"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> HistogramResponse:
    """Get fare histogram by percentiles."""
    return analytics_service.get_fare_histogram(percentiles)