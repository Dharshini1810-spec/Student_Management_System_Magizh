import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReferralLinkCreate(BaseModel):
    description: Optional[str] = None
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None

class ReferralLinkUpdate(BaseModel):
    is_active: Optional[bool] = None

class ReferralLinkRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    code: str
    description: Optional[str] = None
    is_active: bool
    max_uses: Optional[int] = None
    current_uses: int
    expires_at: Optional[datetime] = None
    created_at: datetime
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReferralClaim(BaseModel):
    code: str
