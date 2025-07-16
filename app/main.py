"""
    Entry point of FastAPI app
"""

import os
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.routes import passengers_router
from app.schemas.responses import APIInfoResponse
from app.api.dependencies import get_data_service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Lifespan context manager for startup and shutdown events
    """

    logger.info("Starting Titanic API application...")
    
    try:
        validate_configuration()
        
        get_data_service()
        
        logger.info("Application startup completed successfully")
        
    except Exception as exc:
        logger.exception(f"Failed to start application: {exc}")
        raise
    
    yield
    
    logger.info("Shutting down Titanic API application...")


def validate_configuration() -> None:
    """
        Validate configuration from environment variables
    """

    data_source = os.getenv("DATA_SOURCE", "csv")
    
    if data_source not in ["csv", "sqlite"]:
        logger.error(f"Unsupported DATA_SOURCE: {data_source}")
        raise ValueError(f"Unsupported DATA_SOURCE: {data_source}")
    
    logger.info(f"Configuration validated: data_source={data_source}")


def create_app() -> FastAPI:
    """
        Create and configure FastAPI application
    """
    
    app = FastAPI(
        title="Titanic Passenger Data API",
        description="API for analyzing Titanic passenger data",
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.include_router(passengers_router)
    
    return app

app = create_app()

@app.get("/", response_model=APIInfoResponse)
def root() -> APIInfoResponse:
    """
        Root endpoint
    """

    return APIInfoResponse(
        message="Titanic Passenger Data API",
        version="1.0.0",
        docs="/docs"
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """
        Validation error handler
    """

    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """
        Value error handler
    """

    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)