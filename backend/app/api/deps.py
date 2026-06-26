import uuid
from typing import Generator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import decode_token, decode_access_token
from ..core.exceptions import AuthenticationException, AuthorizationException
from ..core.permissions import UserRole, has_permission
from ..database.session import SessionLocal
from ..models.user import User
from ..repositories.user import UserRepository

# OAuth2PasswordBearer extracts the Bearer token from the Authorization header
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
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
        raise AuthenticationException(detail="Could not validate credentials")
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException(detail="Token is missing subject claim")
        
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationException(detail="Invalid user identifier format")
        
    user = UserRepository.get_by_id(db, user_uuid)
    if not user:
        raise AuthenticationException(detail="User not found")
        
    if not user.is_active:
        raise AuthenticationException(detail="User account is deactivated")
        
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
            raise AuthorizationException(detail="You do not have permission to access this resource")
        return current_user


def require_super_admin():
    async def check_super_admin(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != UserRole.SUPER_ADMIN:
            raise AuthorizationException(detail="Only Super Admin can perform this action")
        return current_user
    return check_super_admin


def require_roles(allowed_roles: list[UserRole]):
    async def check_roles(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [role.value for role in allowed_roles]:
            raise AuthorizationException(detail="Insufficient permissions for this action")
        return current_user
    return check_roles


def require_permission(permission: str):
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise AuthorizationException(detail="Invalid user role")

        if not has_permission(user_role, permission):
            raise AuthorizationException(detail=f"Permission '{permission}' is required")
        return current_user
    return check_permission
