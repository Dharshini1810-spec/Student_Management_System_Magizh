from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.
    """
    pass

# Import all models here to register them with metadata
# Note: Models should be imported in alembic env.py or models/__init__.py to avoid circular imports.
