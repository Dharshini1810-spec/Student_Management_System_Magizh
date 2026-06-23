from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.
    """
    pass

# Import all models here to register them with metadata
from app.models.user import User  # noqa: F401
