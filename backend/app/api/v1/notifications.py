import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.response import success_response
from app.models.user import User
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationRead

router = APIRouter()

@router.get("", response_model=dict)
def list_notifications(
    is_read: Optional[bool] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifications, total = NotificationRepository.list_by_user(
        db=db, user_id=current_user.id,
        is_read=is_read, limit=limit, offset=offset
    )
    notif_data = [NotificationRead.model_validate(n).model_dump() for n in notifications]
    return success_response(
        data={"notifications": notif_data, "total": total, "limit": limit, "offset": offset},
        message="Notifications retrieved successfully."
    )

@router.get("/unread-count", response_model=dict)
def unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = NotificationRepository.unread_count(db=db, user_id=current_user.id)
    return success_response(
        data={"unread_count": count},
        message="Unread count retrieved successfully."
    )

@router.patch("/read-all", response_model=dict)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = NotificationRepository.mark_all_read(db=db, user_id=current_user.id)
    return success_response(
        data={"marked_read": count},
        message="All notifications marked as read."
    )

@router.patch("/{notification_id}/read", response_model=dict)
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = NotificationRepository.get_by_id(db=db, notification_id=notification_id)
    if not notification or notification.user_id != current_user.id:
        return success_response(
            data=None,
            message="Notification not found."
        )
    NotificationRepository.mark_as_read(db=db, notification=notification)
    return success_response(
        data=NotificationRead.model_validate(notification).model_dump(),
        message="Notification marked as read."
    )
