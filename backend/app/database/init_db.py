from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.seed.super_admin import seed_super_admin

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    Validates connection and runs database seed routines.
    """
    try:
        # Simple query to verify database is online and reachable
        db.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
    except Exception as e:
        logger.error(f"Failed database connection verification: {e}")
        raise e

    # Invoke the Super Admin seed placeholder
    seed_super_admin(db)
