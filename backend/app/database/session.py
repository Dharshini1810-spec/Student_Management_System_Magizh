import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

<<<<<<< HEAD
logger = logging.getLogger(__name__)

fallback_to_sqlite = False
engine = None

try:
    if settings.DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
        )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    logger.warning(f"Failed to connect to primary DATABASE_URL ({settings.DATABASE_URL}). Falling back to SQLite local database. Error: {e}")
    fallback_to_sqlite = True

if fallback_to_sqlite:
    sqlite_url = "sqlite:///./local_fallback.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )
    try:
        from app.database.base import Base
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.user_permission import UserPermission
        from app.models.student import Student, AdminStudent, MentorStudent
        from app.models.attendance import Attendance, AttendanceRequest, AttendanceSettings
        
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully initialized SQLite fallback database schemas.")
    except Exception as create_err:
        logger.error(f"Failed to initialize SQLite fallback database: {create_err}")
=======
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
>>>>>>> fcf518897bf1e7d68bc46b20f3d81c9d5f561424

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
