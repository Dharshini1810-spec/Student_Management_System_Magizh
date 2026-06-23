from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.response import success_response, error_response
from app.api.deps import get_db
from app.api.v1 import api_router

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register central global exception handlers
register_exception_handlers(app)

# Register base API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """
    Service health check endpoint.
    Verifies that the API service is up and can connect to the database.
    """
    health_status = {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": "offline"
        }
    }
    
    try:
        # Check db connection
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "online"
        return success_response(
            data=health_status,
            message="All services are operating normally."
        )
    except Exception as e:
        logger.error(f"Health check failed database verification: {e}")
        health_status["status"] = "degraded"
        return error_response(
            message="Database connection failed",
            code="DATABASE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=health_status
        )

@app.get("/")
def root():
    """
    Root endpoint redirecting/confirming the API version and status.
    """
    return success_response(
        data={"version": "1.0.0", "project": settings.PROJECT_NAME},
        message="Welcome to the Student Management System API."
    )
