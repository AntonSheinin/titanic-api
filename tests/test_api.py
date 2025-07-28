"""
    API tests module
"""

from fastapi import HTTPException


class TestAPIEndpoints:
    """
        Test API endpoints class
    """

    def test_root_endpoint_success(self, test_client):
        """
            Test root endpoint returns API information
        """

        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Titanic Passenger Data API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"

    def test_get_all_passengers_success(self, test_client):
        """
            Test get all passengers returns correct data
        """

        response = test_client.get("/passengers/")
        data = response.json()

        assert response.status_code == 200
        assert "passengers" in data
        assert "total_count" in data
        assert data["total_count"] == 3, "3 passengers returned from sample data fixture"
        assert len(data["passengers"]) == 3
        assert data["passengers"][0]["PassengerId"] == 1, "ID of first passenger should be 1"

    def test_get_passenger_by_id_success(self, test_client):
        """
            Test get passenger by ID returns correct passenger
        """

        response = test_client.get("/passengers/1")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["PassengerId"] == 1, "Should be 1 passenger"
        assert data["data"]["Name"] == "John Doe"

    def test_get_passenger_by_id_not_found(self, test_client, mock_data_service):
        """
            Test get non-existing passenger returns 404
        """

        mock_data_service.get_passenger_by_id.return_value = None

        response = test_client.get("/passengers/999")
        data = response.json()

        assert response.status_code == 404, "should return 404 Not Found"
        assert data["detail"] == "Passenger not found", "ID of non-existent passenger"

    def test_get_passenger_invalid_id_format(self, test_client):
        """
            Test get passenger with invalid ID format
        """

        response = test_client.get("/passengers/invalid")
        data = response.json()

        assert response.status_code == 422, "FastAPI should return 422 when passed invalid ID format"
        assert "detail" in data, "detail is a part of standard response of custom exception handler"

    def test_get_passenger_with_attributes_success(self, test_client):
        """
            Test get passenger with specific attributes
        """

        response = test_client.get("/passengers/1?attributes=Name&attributes=Age")
        data = response.json()

        assert response.status_code == 200
        assert "data" in data
        assert "Name" in data["data"]
        assert "Age" in data["data"]
        assert data["data"]["Name"] == "John Doe", "part of sample data"
        assert data["data"]["Age"] == 22.0

    def test_get_passenger_attributes_not_found(self, test_client, mock_data_service):
        """
            Test get attributes for non-existing passenger
        """

        mock_data_service.get_passenger_by_id.return_value = None

        response = test_client.get("/passengers/999?attributes=Name")
        data = response.json()

        assert response.status_code == 404
        assert data["detail"] == "Passenger not found"

    def test_get_passenger_invalid_attributes(self, test_client, mock_data_service):
        """
            Test get passenger with invalid attributes
        """

        from app.schemas.validators import validate_attributes

        def side_effect(attributes):
            try:
                validate_attributes(attributes, ["PassengerId", "Name", "Age"])
                return {"Name": "Test"}

            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))

        mock_data_service.get_passenger_attributes.side_effect = side_effect

        response = test_client.get("/passengers/1?attributes=InvalidColumn")

        assert response.status_code == 400, "should return 400 when passed invalid attributes"


class TestAnalyticsEndpoints:
    """
        Test analytics endpoints
    """

    def test_fare_histogram_success(self, test_client):
        """
            Test fare histogram endpoint returns correct data
        """

        response = test_client.get("/passengers/analytics/fare-histogram")
        data = response.json()

        assert response.status_code == 200
        assert "data" in data
        assert "total_passengers" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 10, "analytic service mock returns default histogram for 10 percentiles"

        # Check histogram data structure
        for item in data["data"]:
            assert "percentile" in item
            assert "count" in item
            assert "fare_range" in item

    def test_fare_histogram_custom_percentiles(self, test_client):
        """
            Test fare histogram with custom percentiles
        """

        response = test_client.get("/passengers/analytics/fare-histogram?percentiles=20")
        data = response.json()

        assert response.status_code == 200
        assert len(data["data"]) == 20, "should return 20 percentiles"

    def test_fare_histogram_invalid_percentiles_low(self, test_client):
        """
            Test fare histogram with percentiles too low
        """

        response = test_client.get("/passengers/analytics/fare-histogram?percentiles=3")
        data = response.json()

        assert response.status_code == 422, "FastAPI should return 422 when passed invalid percentiles"
        assert "detail" in data, "detail is a part of standard response of custom exception handler"

    def test_fare_histogram_invalid_percentiles_high(self, test_client):
        """
            Test fare histogram with percentiles too high
        """

        response = test_client.get("/passengers/analytics/fare-histogram?percentiles=150")
        data = response.json()

        assert response.status_code == 422, "FastAPI should return 422 when passed invalid percentiles"
        assert "detail" in data, "detail is a part of standard response of custom exception handler"

    def test_fare_histogram_no_data(self, test_client, mock_data_service):
        """
            Test fare histogram when no fare data available
        """

        mock_data_service.get_fare_data.return_value = []

        response = test_client.get("/passengers/analytics/fare-histogram")
        data = response.json()

        assert response.status_code == 400
        assert "No fare data available" in data["detail"]


class TestErrorHandling:
    """
        Test API error handling
    """

    def test_nonexistent_endpoint(self, test_client):
        """
            Test 404 error for non-existent endpoint
        """

        response = test_client.get("/nonexistent")

        assert response.status_code == 404, "should return 404 Not Found"

    def test_nonexistent_passenger_endpoint(self, test_client):
        """
            Test 404 for non-existent passenger sub-endpoint
        """

        response = test_client.get("/passengers/4")

        assert response.status_code == 404, "should return 404 Not Found because in sample data 3 passengers only"

    def test_nonexistent_analytics_endpoint(self, test_client):
        """
            Test 404 for non-existent analytics sub-endpoint
        """

        response = test_client.get("/analytics/invalid-endpoint")

        assert response.status_code == 404, "should return 404 Not Found"

    def test_method_not_allowed(self, test_client):
        """
            Test 405 for unsupported HTTP methods
        """

        response = test_client.post("/passengers/")

        assert response.status_code == 405, "POST method should return 405 Method Not Allowed"


class TestEdgeCases:
    """
        Test edge cases and boundary conditions
    """

    def test_empty_attributes_parameter(self, test_client):
        """
            Test behavior with empty attributes parameter
        """

        response = test_client.get("/passengers/1?attributes=")

        assert response.status_code == 200, "should return passenger data only and ignore empty attributes"

    def test_multiple_query_parameters(self, test_client):
        """
            Test endpoints with multiple query parameters
        """

        response = test_client.get("/passengers/1?attributes=Name&extra=ignored")

        assert response.status_code == 200, "should ignore the unsupported query parameter"
