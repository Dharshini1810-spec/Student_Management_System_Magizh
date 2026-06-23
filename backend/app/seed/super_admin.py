import logging
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.core.security import get_password_hash
from app.core.permissions import UserRole

logger = logging.getLogger(__name__)

def seed_super_admin(db: Session) -> None:
    """
    Seeds a default super admin user if one doesn't exist.
    """
    logger.info("Checking if super admin user needs to be seeded...")
    
    # Default credentials. In production, these should be loaded from secure settings.
    admin_email = "admin@sms.com"
    admin_password = "SuperAdminSecurePassword123!"
    
    existing_admin = UserRepository.get_by_email(db, admin_email)
    if not existing_admin:
        logger.info(f"Super admin user not found. Creating new super admin with email: {admin_email}")
        hashed_pw = get_password_hash(admin_password)
        
        UserRepository.create(
            db=db,
            email=admin_email,
            hashed_password=hashed_pw,
            role=UserRole.SUPER_ADMIN.value,
            is_first_login=True  # Enforces password change on first access
        )
        logger.info("Super admin user successfully seeded.")
    else:
        logger.info("Super admin user already exists in the database. Seeding skipped.")
