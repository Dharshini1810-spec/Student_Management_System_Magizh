import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: str
    role: str
    name: Optional[str] = None
    is_active: bool = True
    is_first_login: bool = True
    is_approved: bool = True
    is_deleted: bool = False
    admin_id: Optional[uuid.UUID] = None
    mentor_id: Optional[uuid.UUID] = None

class UserCreate(BaseModel):
    email: str
    role: str
    name: Optional[str] = None
    admin_id: Optional[uuid.UUID] = None
    mentor_id: Optional[uuid.UUID] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    admin_id: Optional[uuid.UUID] = None
    mentor_id: Optional[uuid.UUID] = None
    role: Optional[str] = None

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
