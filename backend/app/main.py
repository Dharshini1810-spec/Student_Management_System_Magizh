from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.response import success_response

from sqlalchemy import text
from app.database.session import SessionLocal
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


@app.get("/")
def root():
    """
    Root endpoint redirecting/confirming the API version and status.
    """
    return success_response(
        data={"version": "1.0.0", "project": settings.PROJECT_NAME},
        message="Welcome to the Student Management System API."
    )


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify API and Database status.
    """
    db_status = "healthy"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = "unhealthy"
        logger.error(f"Database health check failed: {e}")

    return success_response(
        data={
            "services": {
                "api": "healthy",
                "database": db_status
            }
        },
        message="System status retrieved successfully."
    )
