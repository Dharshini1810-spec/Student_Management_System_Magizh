import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PermissionRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserPermissionGrant(BaseModel):
    permission_id: int

class UserPermissionRead(BaseModel):
    id: int
    user_id: uuid.UUID
    permission_id: int
    granted_by: uuid.UUID | None = None
    granted_at: datetime
    permission: PermissionRead

    model_config = ConfigDict(from_attributes=True)
