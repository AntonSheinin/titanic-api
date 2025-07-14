"""
    Pydantic response models
"""

ffrom pydantic import BaseModel
from typing import List, Dict, Any
from app.models.passenger import Passenger


class HistogramData(BaseModel):
    """
        Histogram data model
    """
    percentile: float
    count: int
    fare_range: str


class HistogramResponse(BaseModel):
    """
        Histogram response model
    """

    data: List[HistogramData]
    total_passengers: int


class PassengerResponse(BaseModel):
    """
        Passenger response model
    """

    data: Passenger


class PassengerAttributesResponse(BaseModel):
    """
        Passenger attributes response model
    """

    data: Dict[str, Any]


class PassengersListResponse(BaseModel):
    """
        Passengers list response model
    """

    passengers: List[Passenger]
    total_count: int


class APIInfoResponse(BaseModel):
    """
        API info response model
    """

    message: str
    version: str
    docs: str