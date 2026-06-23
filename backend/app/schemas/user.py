import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    email: str
    role: str
    is_active: bool = True
    is_first_login: bool = True

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
