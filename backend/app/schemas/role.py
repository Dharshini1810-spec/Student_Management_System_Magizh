<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict

class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
=======
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict

from ..core.permissions import UserRole, PermissionName


# ─── Role Schemas ─────────────────────────────────────────────────────────────

class PermissionRead(BaseModel):
    """Schema for a single permission object returned from the API."""
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleRead(BaseModel):
    """Schema for a role, optionally including its assigned permissions."""
    id: int
    name: str
    description: Optional[str] = None
    permissions: list[PermissionRead] = []

    model_config = ConfigDict(from_attributes=True)


# ─── User Creation (Super Admin only) ─────────────────────────────────────────

class CreateUserRequest(BaseModel):
    """
    Request body for Super Admin to create a new user account.
    Super Admin provides the email and temporary password; role must be one of
    ADMIN, MENTOR, or STUDENT (not SUPER_ADMIN).
    """
    email: str
    password: str
    role: UserRole
    full_name: Optional[str] = None

    @field_validator("role")
    @classmethod
    def role_must_not_be_super_admin(cls, v: UserRole) -> UserRole:
        if v == UserRole.SUPER_ADMIN:
            raise ValueError("Cannot create a SUPER_ADMIN user via this endpoint")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


# ─── User Permission Assignment ────────────────────────────────────────────────

class AssignPermissionRequest(BaseModel):
    """Request body to assign a direct permission to a user."""
    permission: PermissionName


class RevokePermissionRequest(BaseModel):
    """Request body to revoke a direct permission from a user."""
    permission: PermissionName


class UserPermissionRead(BaseModel):
    """Schema for a direct user permission record."""
    permission: PermissionRead
    granted_by: Optional[uuid.UUID] = None
    granted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPermissionsResponse(BaseModel):
    """Complete user permissions: role-based + direct overrides."""
    user_id: uuid.UUID
    role: str
    role_permissions: list[str]
    direct_permissions: list[str]
    all_permissions: list[str]


# ─── Change Password ───────────────────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    """Request body for changing password (first-login or voluntary)."""
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")
        return v


class AdminResetPasswordResponse(BaseModel):
    """Response after Super Admin triggers password reset for another user."""
    user_id: uuid.UUID
    reset_token: str
    message: str


# ─── User List / Detail ────────────────────────────────────────────────────────

class UserListItem(BaseModel):
    """Slim user representation for list views."""
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    is_first_login: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateUserRequest(BaseModel):
    """Fields that can be updated by Admin/Super Admin."""
    is_active: Optional[bool] = None
>>>>>>> fcf518897bf1e7d68bc46b20f3d81c9d5f561424
