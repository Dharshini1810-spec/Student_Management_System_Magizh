import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class StudentNoteCreate(BaseModel):
    content: str

class StudentNoteRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    written_by: uuid.UUID
    content: str
    author_name: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
