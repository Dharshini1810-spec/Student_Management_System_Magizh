import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    deadline: Optional[datetime] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    deadline: Optional[datetime] = None

class TodoStatusUpdate(BaseModel):
    status: str

class TodoRead(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    created_by_name: Optional[str] = None
    assignee_name: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str
    is_personal: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
