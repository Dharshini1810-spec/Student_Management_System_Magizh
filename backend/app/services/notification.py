import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.notification import NotificationRepository


class NotificationService:
    @staticmethod
    def send_notification(
        db: Session,
        user_id: uuid.UUID,
        title: str,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
    ) -> None:
        NotificationRepository.create(
            db=db,
            user_id=user_id,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
