import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.permissions import require_permission, require_super_admin, require_roles, UserRole
from app.core.response import success_response
from app.models.user import User
from app.schemas.role import (
    CreateUserRequest,
    AssignPermissionRequest,
    RevokePermissionRequest,
    UpdateUserRequest,
)
from app.schemas.user import UserRead
from app.services.user import UserService

router = APIRouter()


# ─── User Management ──────────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED, tags=["User Management"])
def create_user(
    data: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin()),
):
    """
    **Super Admin only.**

    Creates a new user account (Admin, Mentor, or Student).
    Super Admin sets the email and a temporary password.
    The user must change their password on first login (`is_first_login=true`).
    """
    user = UserService.create_user(db, requester=current_user, data=data)
    user_read = UserRead.model_validate(user)
    return success_response(
        data=user_read.model_dump(),
        message=f"User '{user.email}' created successfully with role '{user.role}'."
    )


@router.get("/", tags=["User Management"])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.ADMIN])),
):
    """
    **Super Admin / Admin.**

    Lists all users.
    - Super Admin sees everyone.
    - Admin sees all non-super-admin users.
    """
    users = UserService.list_users(db, requester=current_user)
    data = [UserRead.model_validate(u).model_dump() for u in users]
    return success_response(data=data, message=f"Retrieved {len(data)} users")


@router.get("/{user_id}", tags=["User Management"])
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Authenticated.**

    Returns details for a specific user.
    - Super Admin: can view anyone
    - Admin: can view non-super-admin users
    - Others: can only view themselves
    """
    user = UserService.get_user(db, requester=current_user, user_id=user_id)
    user_read = UserRead.model_validate(user)
    return success_response(data=user_read.model_dump(), message="User retrieved successfully")


@router.patch("/{user_id}", tags=["User Management"])
def update_user(
    user_id: uuid.UUID,
    data: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update")),
):
    """
    **Requires: `users:update` permission.**

    Updates user fields (currently: `is_active`).
    Admin cannot modify Super Admin accounts.
    """
    update_dict = data.model_dump(exclude_none=True)
    user = UserService.update_user(db, requester=current_user, user_id=user_id, update_data=update_dict)
    user_read = UserRead.model_validate(user)
    return success_response(data=user_read.model_dump(), message="User updated successfully")


@router.delete("/{user_id}", tags=["User Management"])
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:delete")),
):
    """
    **Requires: `users:delete` permission.**

    Soft-deletes (deactivates) a user account. Cannot target Super Admin or yourself.
    """
    user = UserService.deactivate_user(db, requester=current_user, user_id=user_id)
    return success_response(
        data={"user_id": str(user.id), "is_active": user.is_active},
        message=f"User '{user.email}' has been deactivated"
    )


# ─── Permission Management ────────────────────────────────────────────────────

@router.get("/{user_id}/permissions", tags=["Permissions"])
def get_user_permissions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Super Admin or self.**

    Returns the complete permissions profile for a user:
    - `role_permissions`: inherited from the user's role
    - `direct_permissions`: directly assigned by Super Admin
    - `all_permissions`: combined set (deduped)
    """
    result = UserService.get_user_permissions(db, requester=current_user, user_id=user_id)
    return success_response(data=result.model_dump(), message="User permissions retrieved successfully")


@router.post("/{user_id}/permissions", tags=["Permissions"])
def assign_permission(
    user_id: uuid.UUID,
    data: AssignPermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin()),
):
    """
    **Super Admin only.**

    Grants an additional (direct) permission to a specific user.
    This is additive on top of their role permissions. Idempotent.
    """
    result = UserService.assign_permission(
        db, requester=current_user, user_id=user_id, permission_name=data.permission.value
    )
    return success_response(data=result, message=f"Permission '{data.permission.value}' granted successfully")


@router.delete("/{user_id}/permissions", tags=["Permissions"])
def revoke_permission(
    user_id: uuid.UUID,
    data: RevokePermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin()),
):
    """
    **Super Admin only.**

    Revokes a directly assigned permission from a specific user.
    Role-based permissions are not affected.
    """
    result = UserService.revoke_permission(
        db, requester=current_user, user_id=user_id, permission_name=data.permission.value
    )
    return success_response(data=result, message=f"Permission '{data.permission.value}' revoked successfully")


# ─── Password Reset (Super Admin) ─────────────────────────────────────────────

@router.post("/{user_id}/reset-password", tags=["User Management"])
def admin_reset_user_password(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin()),
):
    """
    **Super Admin only.**

    Forces a password reset for another user.
    Returns a reset token that the user must use with `POST /auth/reset-password`.
    In development mode, the token is returned directly in the response.
    """
    result = UserService.admin_reset_password(db, requester=current_user, user_id=user_id)
    return success_response(data=result, message="Password reset token generated")
