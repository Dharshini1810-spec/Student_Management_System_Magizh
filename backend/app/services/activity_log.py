import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.activity_log import ActivityLogRepository


class ActivityLogService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: uuid.UUID,
        action: str,
        description: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
    ) -> None:
        ActivityLogRepository.create_log(
            db=db,
            user_id=user_id,
            action=action,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
        )
