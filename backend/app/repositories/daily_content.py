import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.daily_content import DailyContent

class DailyContentRepository:

    @staticmethod
    def create(
        db: Session,
        title: str,
        assigned_by: uuid.UUID,
        content_date: date,
        assigned_to: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        links: Optional[list[str]] = None,
    ) -> DailyContent:
        daily_content = DailyContent(
            title=title,
            description=description,
            links=links,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            content_date=content_date,
        )
        db.add(daily_content)
        db.commit()
        db.refresh(daily_content)
        return daily_content

    @staticmethod
    def get_by_id(db: Session, daily_content_id: uuid.UUID) -> Optional[DailyContent]:
        return db.query(DailyContent).filter(
            DailyContent.id == daily_content_id,
            DailyContent.is_deleted == False,
        ).first()

    @staticmethod
    def list_by_assigned_to(db: Session, user_id: uuid.UUID) -> List[DailyContent]:
        return db.query(DailyContent).filter(
            DailyContent.assigned_to == user_id,
            DailyContent.is_deleted == False,
        ).order_by(DailyContent.created_at.desc()).all()

    @staticmethod
    def list_created_by(db: Session, user_id: uuid.UUID) -> List[DailyContent]:
        return db.query(DailyContent).filter(
            DailyContent.assigned_by == user_id,
            DailyContent.is_deleted == False,
        ).order_by(DailyContent.created_at.desc()).all()

    @staticmethod
    def list_all(db: Session) -> List[DailyContent]:
        return db.query(DailyContent).filter(
            DailyContent.is_deleted == False,
        ).order_by(DailyContent.created_at.desc()).all()

    @staticmethod
    def update(db: Session, daily_content: DailyContent, update_data: dict) -> DailyContent:
        for field, value in update_data.items():
            if hasattr(daily_content, field):
                setattr(daily_content, field, value)
        db.add(daily_content)
        db.commit()
        db.refresh(daily_content)
        return daily_content

    @staticmethod
    def soft_delete(db: Session, daily_content: DailyContent) -> DailyContent:
        daily_content.is_deleted = True
        db.add(daily_content)
        db.commit()
        db.refresh(daily_content)
        return daily_content
