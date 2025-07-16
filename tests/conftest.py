"""
    Fixtures module for pytest
"""

import pytest
from pydantic import ValidationError
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from app.schemas.responses import Passenger
from app.services.data_service import DataService
from app.schemas.responses import APIInfoResponse
from app.services.analytics_service import AnalyticsService
from app.schemas.responses import HistogramResponse, HistogramData
from app.api.dependencies import get_data_service, get_analytics_service
from app.main import create_app, validation_exception_handler, value_error_handler, root


@pytest.fixture
def sample_data():
    """
        Sample passenger data for testing
    """

    return [
        {
            "PassengerId": 1,
            "Survived": 0,
            "Pclass": 3,
            "Name": "John Doe",
            "Sex": "male",
            "Age": 22.0,
            "SibSp": 1,
            "Parch": 0,
            "Ticket": "A123",
            "Fare": 7.25,
            "Cabin": None,
            "Embarked": "S"
        },
        {
            "PassengerId": 2,
            "Survived": 1,
            "Pclass": 1,
            "Name": "Jane Smith",
            "Sex": "female",
            "Age": 38.0,
            "SibSp": 1,
            "Parch": 0,
            "Ticket": "B456",
            "Fare": 71.28,
            "Cabin": "C85",
            "Embarked": "C"
        },
        {
            "PassengerId": 3,
            "Survived": 1,
            "Pclass": 3,
            "Name": "Bob Wilson",
            "Sex": "male",
            "Age": None,
            "SibSp": 0,
            "Parch": 0,
            "Ticket": "C789",
            "Fare": None,
            "Cabin": None,
            "Embarked": "S"
        }
    ]


@pytest.fixture
def mock_analytics_service(mock_data_service):
    """
        Mock analytics service that respects data service
    """

    mock = Mock(spec=AnalyticsService)

    def get_fare_histogram_side_effect(percentiles=10):
        """
            Generate histogram data or raise error based on data service
        """

        fare_data = mock_data_service.get_fare_data()

        if not fare_data:
            raise ValueError("No fare data available for analysis")

        # Generate histogram data based on percentiles
        data = []
        for i in range(percentiles):
            percentile_value = ((i + 1) * 100) / percentiles
            lower_bound = i * 10.0
            upper_bound = (i + 1) * 10.0

            data.append(HistogramData(
                percentile=percentile_value,
                count=1,
                fare_range=f"{lower_bound:.2f} - {upper_bound:.2f}"
            ))

        return HistogramResponse(
            data=data,
            total_passengers=len(fare_data)
        )

    mock.get_fare_histogram.side_effect = get_fare_histogram_side_effect

    return mock

@pytest.fixture
def mock_data_service(sample_data):
    """
        Mock data service with sample data
    """

    mock = Mock(spec=DataService)
    passengers = [Passenger(**data) for data in sample_data]

    def get_passenger_by_id_side_effect(passenger_id):
        """
            Return based on actual ID
        """
        for passenger in passengers:
            if passenger.PassengerId == passenger_id:
                return passenger
        return None

    mock.get_all_passengers.return_value = passengers
    mock.get_passenger_by_id.side_effect = get_passenger_by_id_side_effect  # Use side_effect
    mock.get_passenger_attributes.return_value = {"Name": "John Doe", "Age": 22.0}
    mock.get_fare_data.return_value = [7.25, 71.28]
    mock.get_columns.return_value = list(sample_data[0].keys())

    return mock


@pytest.fixture
def test_client(mock_data_service, mock_analytics_service):
    """
        Test client with mocked data and analytics service and all endpoints/handlers
    """

    with patch('app.main.validate_configuration'), \
            patch('app.api.dependencies.get_data_service', return_value=mock_data_service):
        app = create_app()

        app.add_exception_handler(ValidationError, validation_exception_handler)
        app.add_exception_handler(ValueError, value_error_handler)
        app.get("/", response_model=APIInfoResponse)(root)

        app.dependency_overrides[get_data_service] = lambda: mock_data_service
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service

        return TestClient(app)