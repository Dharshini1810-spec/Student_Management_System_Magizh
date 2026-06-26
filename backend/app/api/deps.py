import uuid
from typing import Generator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import decode_token
from ..database.session import SessionLocal
from ..core.exceptions import AuthenticationException, AuthorizationException
from ..core.permissions import UserRole
from ..models.user import User
from ..repositories.user import UserRepository

# OAuth2PasswordBearer extracts the Bearer token from the Authorization header
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to provide a thread-safe database session.
    Closes the session after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Dependency to validate the access token and return the current user record.
    """
    payload = decode_token(token)
    if not payload:
        raise AuthenticationException(
            message="Could not validate credentials",
            code="INVALID_CREDENTIALS"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException(
            message="Token is missing subject claim",
            code="INVALID_TOKEN_CLAIMS"
        )
        
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationException(
            message="Invalid user identifier format",
            code="INVALID_USER_ID"
        )
        
    user = UserRepository.get_by_id(db, user_uuid)
    if not user:
        raise AuthenticationException(
            message="User not found",
            code="USER_NOT_FOUND"
        )
        
    if not user.is_active:
        raise AuthenticationException(
            message="User account is deactivated",
            code="INACTIVE_USER"
        )
        
    return user

class RoleRequired:
    """
    Dependency class to enforce role-based access control.
    """
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role
        if user_role not in [role.value for role in self.allowed_roles]:
            raise AuthorizationException(
                message="You do not have permission to access this resource",
                code="INSUFFICIENT_PERMISSIONS"
            )
        return current_user
