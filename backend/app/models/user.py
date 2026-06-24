from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_first_login: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
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

    # Self-referential relationships
    mentor: Mapped[Optional[User]] = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[mentor_id],
        back_populates="mentees"
    )
    mentees: Mapped[List[User]] = relationship(
        "User",
        foreign_keys=[mentor_id],
        back_populates="mentor"
    )
    admin: Mapped[Optional[User]] = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[admin_id],
        back_populates="assigned_users"
    )
    assigned_users: Mapped[List[User]] = relationship(
        "User",
        foreign_keys=[admin_id],
        back_populates="admin"
    )

