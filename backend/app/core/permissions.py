from enum import Enum
from typing import Callable, List
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationException


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"


class PermissionName(str, Enum):
    """
    All fine-grained permissions supported by the system.
    Format: <resource>:<action>
    """
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    STUDENTS_VIEW = "students:view"
    STUDENTS_CREATE = "students:create"
    STUDENTS_UPDATE = "students:update"
    ATTENDANCE_MANAGE = "attendance:manage"
    PROJECTS_ASSIGN = "projects:assign"
    TODOS_ASSIGN = "todos:assign"
    DAILY_CONTENT_ASSIGN = "daily_content:assign"
    REPORTS_VIEW = "reports:view"


def require_permission(permission: str) -> Callable:
    """
    FastAPI dependency factory that checks whether the current user has the
    given permission (either via their role or a direct user_permission override).

    Super Admins bypass all permission checks.

    Usage:
        @router.get("/resource")
        def endpoint(user = Depends(require_permission("students:view"))):
            ...
    """
    def _checker(
        current_user=Depends(_get_current_user_lazy()),
        db: Session = Depends(_get_db_lazy()),
    ):
        # Super Admin bypasses everything
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        user_perms = _get_all_user_permissions(db, current_user)
        if permission not in user_perms:
            raise AuthorizationException(
                message=f"You do not have the required permission: '{permission}'",
                code="INSUFFICIENT_PERMISSIONS"
            )
        return current_user

    return _checker


def require_super_admin() -> Callable:
    """
    Dependency that allows only SUPER_ADMIN users through.
    """
    def _checker(current_user=Depends(_get_current_user_lazy())):
        if current_user.role != UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="Only Super Admin can perform this action",
                code="SUPER_ADMIN_REQUIRED"
            )
        return current_user

    return _checker


def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """
    Dependency that allows users with any of the specified roles through.
    Super Admin always passes.
    """
    def _checker(current_user=Depends(_get_current_user_lazy())):
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user
        if current_user.role not in [r.value for r in allowed_roles]:
            raise AuthorizationException(
                message="You do not have permission to access this resource",
                code="INSUFFICIENT_ROLE"
            )
        return current_user

    return _checker


def _get_all_user_permissions(db: Session, user) -> set[str]:
    """
    Returns the combined set of permission names for a user:
    role-based permissions + direct user_permission overrides.
    """
    from app.models.role import Role, RolePermission, UserPermission, Permission

    # Role-based permissions
    role = db.query(Role).filter(Role.name == user.role).first()
    role_perm_names: set[str] = set()
    if role:
        rps = (
            db.query(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id == role.id)
            .all()
        )
        role_perm_names = {row[0] for row in rps}

    # Direct user_permissions (additive)
    user_perm_names: set[str] = set()
    ups = (
        db.query(Permission.name)
        .join(UserPermission, UserPermission.permission_id == Permission.id)
        .filter(UserPermission.user_id == user.id)
        .all()
    )
    user_perm_names = {row[0] for row in ups}

    return role_perm_names | user_perm_names


# ─── Lazy dependency helpers (avoid circular imports) ─────────────────────────

def _get_current_user_lazy():
    """Returns the get_current_user dependency, imported lazily to avoid circular imports."""
    from app.api.deps import get_current_user
    return get_current_user


def _get_db_lazy():
    """Returns the get_db dependency, imported lazily to avoid circular imports."""
    from app.api.deps import get_db
    return get_db


# ─── Legacy compat (kept for backward compatibility) ──────────────────────────

class PermissionChecker:
    """
    Legacy dependency helper to check if the current user has the required roles.
    Prefer using require_permission() or require_roles() for new endpoints.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_role: str) -> bool:
        from fastapi import HTTPException, status
        if user_role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return True
