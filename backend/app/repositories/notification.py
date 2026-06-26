import uuid
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.notification import Notification

class NotificationRepository:
    @staticmethod
    def create(db: Session, user_id: uuid.UUID, title: str, message: str, entity_type: Optional[str] = None, entity_id: Optional[uuid.UUID] = None) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def list_by_user(db: Session, user_id: uuid.UUID, is_read: Optional[bool] = None, limit: int = 50, offset: int = 0) -> Tuple[List[Notification], int]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        total = query.count()
        notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
        return notifications, total

    @staticmethod
    def get_by_id(db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
        return db.query(Notification).filter(Notification.id == notification_id).first()

    @staticmethod
    def mark_as_read(db: Session, notification: Notification) -> Notification:
        notification.is_read = True
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_read(db: Session, user_id: uuid.UUID) -> int:
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count

    @staticmethod
    def unread_count(db: Session, user_id: uuid.UUID) -> int:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
