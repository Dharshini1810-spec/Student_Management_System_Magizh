from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# create_engine initiates the PostgreSQL connection pool configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # checks connection health before executing queries
)

# SessionLocal represents the database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
