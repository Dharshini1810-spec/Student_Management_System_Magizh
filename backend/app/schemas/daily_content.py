import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DailyContentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    links: Optional[list[str]] = None
    assigned_to: Optional[uuid.UUID] = None
    content_date: date

class DailyContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    links: Optional[list[str]] = None
    assigned_to: Optional[uuid.UUID] = None
    content_date: Optional[date] = None

class DailyContentRead(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    links: Optional[list[str]] = None
    assigned_to: Optional[uuid.UUID] = None
    assigned_to_name: Optional[str] = None
    assigned_by: uuid.UUID
    assigned_by_name: Optional[str] = None
    content_date: date
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
