import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.core.permissions import UserRole, PermissionName

class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Additional Schemas used by UserService ---

class PermissionRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreateUserRequest(BaseModel):
    email: str
    password: str
    role: UserRole
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AssignPermissionRequest(BaseModel):
    permission: PermissionName


class RevokePermissionRequest(BaseModel):
    permission: PermissionName


class UserPermissionRead(BaseModel):
    permission: PermissionRead
    granted_by: Optional[uuid.UUID] = None
    granted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPermissionsResponse(BaseModel):
    user_id: uuid.UUID
    role: str
    role_permissions: list[str]
    direct_permissions: list[str]
    all_permissions: list[str]


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AdminResetPasswordResponse(BaseModel):
    user_id: uuid.UUID
    reset_token: str
    message: str


class UserListItem(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    is_first_login: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None

