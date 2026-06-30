import uuid
from typing import Optional, List, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog

class ActivityLogRepository:
    @staticmethod
    def create_log(db: Session, user_id: uuid.UUID, action: str, description: str, entity_type: Optional[str] = None, entity_id: Optional[uuid.UUID] = None) -> ActivityLog:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def list_by_user(db: Session, user_id: uuid.UUID) -> List[ActivityLog]:
        return db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(ActivityLog.created_at.desc()).all()

    @staticmethod
    def list_all(
        db: Session,
        user_id: Optional[uuid.UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[ActivityLog], int]:
        query = db.query(ActivityLog)

        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if date_from:
            query = query.filter(ActivityLog.created_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.filter(ActivityLog.created_at <= datetime.combine(date_to, datetime.max.time()))

        total = query.count()
        logs = query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(limit).all()
        return logs, total

    @staticmethod
    def list_by_user_grouped(db: Session, user_id: uuid.UUID) -> dict:
        logs = db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(ActivityLog.created_at.desc()).all()

        grouped = {}
        for log in logs:
            key = log.created_at.strftime("%Y-%m-%d")
            if key not in grouped:
                grouped[key] = []
            grouped[key].append({
                "id": str(log.id),
                "action": log.action,
                "description": log.description,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_id) if log.entity_id else None,
                "created_at": log.created_at.isoformat()
            })
        return grouped
