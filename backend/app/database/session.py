from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Build connect args — enable SSL for remote (Aiven) connections
connect_args = {}
if "aivencloud.com" in settings.DATABASE_URL or "sslmode=require" in settings.DATABASE_URL:
    connect_args["sslmode"] = "require"

# create_engine initiates the PostgreSQL connection pool configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # checks connection health before executing queries
    connect_args=connect_args,
)

# SessionLocal represents the database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
