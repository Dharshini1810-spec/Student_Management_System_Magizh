import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

fallback_to_sqlite = False
engine = None

# Build connect args — enable SSL for remote (Aiven) connections
connect_args = {}
if settings.DATABASE_URL and ("aivencloud.com" in settings.DATABASE_URL or "sslmode=require" in settings.DATABASE_URL):
    connect_args["sslmode"] = "require"

try:
    if settings.DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        from app.database.base import Base
        from app.models import (
            User, Role, Permission, RolePermission, UserPermission,
            Student, AdminStudent, MentorStudent,
            Attendance, AttendanceRequest, AttendanceSettings,
            Todo, DailyContent, Project, StudentNote, ActivityLog, Notification,
            ReferralLink
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully initialized SQLite database schemas.")
    else:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args=connect_args,
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
        from app.models import (
            User, Role, Permission, RolePermission, UserPermission,
            Student, AdminStudent, MentorStudent,
            Attendance, AttendanceRequest, AttendanceSettings,
            Todo, DailyContent, Project, StudentNote, ActivityLog, Notification,
            ReferralLink
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully initialized SQLite fallback database schemas.")
    except Exception as create_err:
        logger.error(f"Failed to initialize SQLite fallback database: {create_err}")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
