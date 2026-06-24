import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class StudentBase(BaseModel):
    nickname: Optional[str] = None
    dob: Optional[datetime] = None
    contact: Optional[str] = None
    position: Optional[str] = None
    avatar: Optional[str] = None

class StudentCreate(StudentBase):
    name: str
    email: str
    password: Optional[str] = None

class StudentUpdate(StudentBase):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class StudentRead(StudentBase):
    id: uuid.UUID
    name: str
    email: str
    role: str
    is_active: bool
    is_deleted: bool
    date_joined: datetime
    assigned_admin_id: Optional[uuid.UUID] = None
    assigned_mentor_id: Optional[uuid.UUID] = None
    assigned_admin_ids: List[uuid.UUID] = []
    assigned_mentor_ids: List[uuid.UUID] = []

    model_config = ConfigDict(from_attributes=True)

class AdminAssign(BaseModel):
    admin_id: uuid.UUID

class MentorAssign(BaseModel):
    mentor_id: uuid.UUID
