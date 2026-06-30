import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DailyContentCreate(BaseModel):
    title: str
    content: Optional[str] = None
    content_date: Optional[date] = None

class DailyContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class DailyContentRead(BaseModel):
    id: uuid.UUID
    title: str
    content: Optional[str] = None
    content_date: date
    created_by: uuid.UUID
    created_by_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
