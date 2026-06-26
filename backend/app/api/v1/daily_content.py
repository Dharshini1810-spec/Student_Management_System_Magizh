import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionRequired
from app.core.response import success_response
from app.models.user import User
from app.models.daily_content import DailyContent
from app.services.daily_content import DailyContentService
from app.services.notification import NotificationService
from app.repositories.user import UserRepository
from app.schemas.daily_content import DailyContentCreate, DailyContentUpdate, DailyContentRead

router = APIRouter()

def map_to_read(dc: DailyContent) -> DailyContentRead:
    return DailyContentRead(
        id=dc.id,
        title=dc.title,
        content=dc.content,
        content_date=dc.content_date,
        created_by=dc.created_by,
        created_by_name=dc.creator.name if dc.creator else None,
        is_active=dc.is_active,
        created_at=dc.created_at,
        updated_at=dc.updated_at,
    )

@router.post("", response_model=dict)
def create_daily_content(
    payload: DailyContentCreate,
    current_user: User = Depends(PermissionRequired("daily_content:assign")),
    db: Session = Depends(get_db),
):
    dc = DailyContentService.create(
        db=db, requester=current_user,
        title=payload.title, content=payload.content,
        content_date=payload.content_date,
    )
    students = UserRepository.get_all_active_students(db)
    for student in students:
        NotificationService.send_notification(
            db=db, user_id=student.id,
            title="New Daily Content",
            message=f"New content posted: {dc.title}",
            entity_type="daily_content", entity_id=dc.id,
        )
    return success_response(
        data=map_to_read(dc).model_dump(),
        message="Daily content created successfully.",
    )

@router.get("", response_model=dict)
def list_daily_content(
    content_date: Optional[date] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = DailyContentService.list_all(
        db=db, requester=current_user,
        content_date=content_date, limit=limit, offset=offset,
    )
    data = [map_to_read(item).model_dump() for item in items]
    return success_response(
        data={"daily_contents": data, "total": total, "limit": limit, "offset": offset},
        message="Daily content retrieved successfully.",
    )

@router.get("/today", response_model=dict)
def get_today_content(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dc = DailyContentService.get_today(db=db, requester=current_user)
    return success_response(
        data=map_to_read(dc).model_dump() if dc else None,
        message="Today's content retrieved successfully.",
    )

@router.get("/{content_id}", response_model=dict)
def get_daily_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dc = DailyContentService.get_by_id(db=db, requester=current_user, content_id=content_id)
    return success_response(
        data=map_to_read(dc).model_dump(),
        message="Daily content retrieved successfully.",
    )

@router.patch("/{content_id}", response_model=dict)
def update_daily_content(
    content_id: uuid.UUID,
    payload: DailyContentUpdate,
    current_user: User = Depends(PermissionRequired("daily_content:assign")),
    db: Session = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)
    dc = DailyContentService.update(
        db=db, requester=current_user,
        content_id=content_id, update_data=update_data,
    )
    return success_response(
        data=map_to_read(dc).model_dump(),
        message="Daily content updated successfully.",
    )

@router.delete("/{content_id}", response_model=dict)
def delete_daily_content(
    content_id: uuid.UUID,
    current_user: User = Depends(PermissionRequired("daily_content:assign")),
    db: Session = Depends(get_db),
):
    dc = DailyContentService.delete(db=db, requester=current_user, content_id=content_id)
    return success_response(
        data=map_to_read(dc).model_dump(),
        message="Daily content deleted successfully.",
    )
