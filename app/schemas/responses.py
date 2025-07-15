"""
    Pydantic models
"""

from typing import Annotated, Literal, Any

from pydantic import BaseModel, Field


class Passenger(BaseModel):
    """
        Passenger model
    """

    PassengerId: Annotated[int, Field(gt=0, description="Unique passenger ID (> 0)")]
    Survived: Annotated[Literal[0, 1], Field(description="Survival flag: 0 = No, 1 = Yes")]
    Pclass: Annotated[int, Field(ge=1, le=3, description="Passenger class (1, 2, or 3)")]
    Name: Annotated[str, Field(description="Full name")]
    Sex: Annotated[Literal["male", "female"], Field(description="Sex: male or female")]
    Age: Annotated[float | None, Field(default=None, ge=0, description="Age in years")]
    SibSp: Annotated[int, Field(ge=0, description="# of siblings/spouses aboard")]
    Parch: Annotated[int, Field(ge=0, description="# of parents/children aboard")]
    Ticket: Annotated[str, Field(description="Ticket number")]
    Fare: Annotated[float | None, Field(default=None, ge=0, description="Fare paid")]
    Cabin: Annotated[str | None, Field(default=None, description="Cabin number")]
    Embarked: Annotated[str | None, Field(default=None, description="Port of embarkation")]


class HistogramData(BaseModel):
    """
        Histogram data model
    """
    percentile: Annotated[float, Field(description="Percentile")]
    count: Annotated[int, Field(ge=0, description="Number of passengers in this fare range")]
    fare_range: Annotated[str, Field(description="Fare range label, e.g., '$0–$50'")]


class HistogramResponse(BaseModel):
    """
        Histogram response model
    """

    data: list[HistogramData]
    total_passengers: Annotated[int, Field(ge=0, description="Total number of passengers available")]


class PassengerResponse(BaseModel):
    """
        Passenger response model
    """

    data: Annotated[Passenger, Field(description="Single passenger record")]


class PassengerAttributesResponse(BaseModel):
    """
        Passenger attributes response model
    """

    data: Annotated[dict[str, Any], Field(description="Dynamic passenger attributes dictionary")]


class PassengersListResponse(BaseModel):
    """
        Passengers list response model
    """

    passengers: list[Passenger] = Field(..., description="List of passenger records")
    total_count: int = Field(..., ge=0, description="Total number of passengers available")


class APIInfoResponse(BaseModel):
    """
        API info response model
    """

    message: str = Field(..., description="Response message")
    version: str = Field(..., description="API version")
    docs: str = Field(..., description="URL to documentation")