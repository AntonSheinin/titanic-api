from pydantic import BaseModel
from typing import List, Dict, Any


class HistogramData(BaseModel):
    percentile: float
    count: int
    fare_range: str


class HistogramResponse(BaseModel):
    data: List[HistogramData]
    total_passengers: int


class PassengerAttributesResponse(BaseModel):
    data: Dict[str, Any]


class PassengersListResponse(BaseModel):
    passengers: List[Dict[str, Any]]
    total_count: int