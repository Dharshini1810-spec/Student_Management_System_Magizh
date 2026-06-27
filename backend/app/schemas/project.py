import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    assigned_to: uuid.UUID
    deadline: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    deadline: Optional[datetime] = None

class ProjectStatusUpdate(BaseModel):
    status: str

class ProjectApprovalUpdate(BaseModel):
    approval_status: str

class ProjectRead(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    assigned_by: uuid.UUID
    assignee_name: Optional[str] = None
    assigner_name: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str
    approval_status: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
