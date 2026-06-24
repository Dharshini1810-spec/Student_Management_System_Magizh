from __future__ import annotations
import uuid
from datetime import datetime, date, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User

class AttendanceSettings(Base):
    __tablename__ = "attendance_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    check_in_deadline: Mapped[str] = mapped_column(String(10), default="09:00", nullable=False)
    check_out_deadline: Mapped[str] = mapped_column(String(10), default="17:00", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    check_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ABSENT", nullable=False)
    is_late_check_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_late_check_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship to student
    student: Mapped[Student] = relationship("Student", back_populates="attendance_records")

class AttendanceRequest(Base):
    __tablename__ = "attendance_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    request_type: Mapped[str] = mapped_column(String(20), nullable=False) # "CHECK_IN" or "CHECK_OUT"
    requested_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False) # "PENDING", "APPROVED", "REJECTED"
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="attendance_requests")
    reviewer: Mapped[Optional[User]] = relationship("User", foreign_keys=[reviewed_by])
