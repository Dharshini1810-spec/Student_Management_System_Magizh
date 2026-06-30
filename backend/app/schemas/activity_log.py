import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ActivityLogRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    action: str
    description: str
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
