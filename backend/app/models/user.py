from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_first_login: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Student-specific relationships
    student_profile: Mapped[Optional[Student]] = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        foreign_keys="Student.id",
        cascade="all, delete-orphan"
    )

    assigned_students: Mapped[List[Student]] = relationship(
        "Student",
        secondary="admin_students",
        back_populates="assigned_admins"
    )

    assigned_mentees: Mapped[List[Student]] = relationship(
        "Student",
        secondary="mentor_students",
        back_populates="assigned_mentors"
    )

    @property
    def admin_id(self) -> Optional[uuid.UUID]:
        if self.role == "STUDENT" and self.student_profile and self.student_profile.assigned_admins:
            return self.student_profile.assigned_admins[0].id
        return None

    @property
    def mentor_id(self) -> Optional[uuid.UUID]:
        if self.role == "STUDENT" and self.student_profile and self.student_profile.assigned_mentors:
            return self.student_profile.assigned_mentors[0].id
        return None



