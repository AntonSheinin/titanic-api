"""
    Pydantic models   
"""

from pydantic import BaseModel


class Passenger(BaseModel):
    PassengerId: int
    Survived: int
    Pclass: int
    Name: str
    Sex: str
    Age: float | None = None
    SibSp: int
    Parch: int
    Ticket: str
    Fare: float | None = None
    Cabin: str | None = None
    Embarked: str | None = None