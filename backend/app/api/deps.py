import uuid
from typing import Generator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.database.session import SessionLocal
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.permissions import UserRole
from app.models.user import User
from app.repositories.user import UserRepository

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

class PermissionRequired:
    """
    Dependency class to enforce permission-based access control, allowing custom user overrides.
    """
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # SUPER_ADMIN bypasses all checks
        if current_user.role == UserRole.SUPER_ADMIN.value:
            return current_user

        from app.repositories.role_permission import RolePermissionRepository
        
        # 1. Check role-based permissions
        role_perms = RolePermissionRepository.get_role_permissions(db, current_user.role)
        if any(p.name == self.required_permission for p in role_perms):
            return current_user

        # 2. Check custom user permissions
        custom_perms = RolePermissionRepository.get_custom_permissions(db, current_user.id)
        if any(cp.permission.name == self.required_permission for cp in custom_perms):
            return current_user

        raise AuthorizationException(
            message=f"You do not have permission to perform this action: {self.required_permission}",
            code="INSUFFICIENT_PERMISSIONS"
        )

def check_data_access(current_user: User, target_user: User) -> None:
    """
    Enforces data scoping rules:
    - Super Admin can access everything.
    - Admin access is limited to assigned mentors/students.
    - Mentor access is limited to assigned students.
    - Student access is limited to own data.
    """
    if current_user.role == UserRole.SUPER_ADMIN.value:
        return

    if current_user.role == UserRole.STUDENT.value:
        if target_user.id != current_user.id:
            raise AuthorizationException(
                message="Access denied: Students can only access their own data",
                code="ACCESS_DENIED"
            )
        return

    if current_user.role == UserRole.MENTOR.value:
        if target_user.role != UserRole.STUDENT.value or target_user.mentor_id != current_user.id:
            raise AuthorizationException(
                message="Access denied: Mentors can only access their assigned students",
                code="ACCESS_DENIED"
            )
        return

    if current_user.role == UserRole.ADMIN.value:
        if target_user.admin_id != current_user.id:
            raise AuthorizationException(
                message="Access denied: Admins can only access their assigned mentors and students",
                code="ACCESS_DENIED"
            )
        return
