# Titanic Passenger Data API

A FastAPI-based REST API for analyzing Titanic passenger data with support for multiple data sources (CSV and SQLite).

## API Endpoints

| Method | Endpoint                               | Description                       |
|--------|----------------------------------------|-----------------------------------|
| `GET`  | `/`                                    | API information                   |
| `GET`  | `/docs`                                | Swagger API documentation         |
| `GET`  | `/passengers/`                         | Get all passengers                |
| `GET`  | `/passengers/{id}`                     | Get passenger by ID               |
| `GET`  | `/passengers/{id}?attributes=Name,Age` | Get specific passenger attributes |
| `GET`  | `/passengers/analytics/fare-histogram` | Generate fare histogram           |
