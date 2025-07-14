import os
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.endpoints import passengers
from app.api.dependencies import get_data_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Titanic API application...")
    
    try:
        # Validate configuration
        validate_configuration()
        
        # Initialize data service (validation happens in dependency)
        get_data_service()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down Titanic API application...")


def validate_configuration() -> None:
    """Validate configuration from environment variables."""
    data_source = os.getenv("DATA_SOURCE", "csv")
    percentiles = int(os.getenv("DEFAULT_HISTOGRAM_PERCENTILES", "10"))
    
    if percentiles < 1 or percentiles > 100:
        raise ValueError("DEFAULT_HISTOGRAM_PERCENTILES must be between 1 and 100")
    
    if data_source not in ["csv", "sqlite"]:
        raise ValueError(f"Unsupported DATA_SOURCE: {data_source}")
    
    logger.info(f"Configuration validated: data_source={data_source}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Titanic Passenger Data API",
        description="API for analyzing Titanic passenger data",
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.include_router(
        passengers.router,
        prefix="/passengers",
        tags=["passengers"]
    )
    
    return app

app = create_app()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Titanic Passenger Data API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)