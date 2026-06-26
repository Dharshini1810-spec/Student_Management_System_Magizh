import uuid
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict
from typing import Optional

class AttendanceSettingsCreate(BaseModel):
    check_in_deadline: str
    check_out_deadline: str

class AttendanceSettingsRead(BaseModel):
    id: int
    check_in_deadline: str
    check_out_deadline: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CheckInRequest(BaseModel):
    reason: Optional[str] = None

class CheckOutRequest(BaseModel):
    reason: Optional[str] = None

class AttendanceRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: Optional[str] = None
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: str
    is_late_check_in: bool
    is_late_check_out: bool

    model_config = ConfigDict(from_attributes=True)

class AttendanceRequestRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    student_name: Optional[str] = None
    request_type: str
    requested_time: datetime
    reason: Optional[str] = None
    status: str
    reviewed_by: Optional[uuid.UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
