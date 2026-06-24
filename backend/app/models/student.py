from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User

class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dob: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_joined: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="student_profile", foreign_keys=[id])

    assigned_admins: Mapped[List[User]] = relationship(
        "User",
        secondary="admin_students",
        back_populates="assigned_students"
    )

    assigned_mentors: Mapped[List[User]] = relationship(
        "User",
        secondary="mentor_students",
        back_populates="assigned_mentees"
    )

class AdminStudent(Base):
    __tablename__ = "admin_students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)

class MentorStudent(Base):
    __tablename__ = "mentor_students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mentor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
