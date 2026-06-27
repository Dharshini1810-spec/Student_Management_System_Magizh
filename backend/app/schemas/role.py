import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional

class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CreateUserRequest(BaseModel):
    email: str
    role: str
    name: Optional[str] = None
    admin_id: Optional[uuid.UUID] = None
    mentor_id: Optional[uuid.UUID] = None

class UserPermissionsResponse(BaseModel):
    user_id: uuid.UUID
    role: str
    role_permissions: list[str]
    direct_permissions: list[str]
    all_permissions: list[str]
