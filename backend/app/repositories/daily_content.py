import uuid
from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.daily_content import DailyContent

class DailyContentRepository:

    @staticmethod
    def create(db: Session, title: str, content: Optional[str], content_date: date, created_by: uuid.UUID) -> DailyContent:
        dc = DailyContent(title=title, content=content, content_date=content_date, created_by=created_by)
        db.add(dc)
        db.commit()
        db.refresh(dc)
        return dc

    @staticmethod
    def get_by_id(db: Session, content_id: uuid.UUID) -> Optional[DailyContent]:
        return db.query(DailyContent).filter(DailyContent.id == content_id, DailyContent.is_active == True).first()

    @staticmethod
    def list_all(db: Session, content_date: Optional[date] = None, limit: int = 50, offset: int = 0) -> Tuple[List[DailyContent], int]:
        query = db.query(DailyContent).filter(DailyContent.is_active == True)
        if content_date:
            query = query.filter(DailyContent.content_date == content_date)
        total = query.count()
        items = query.order_by(DailyContent.content_date.desc(), DailyContent.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def get_today(db: Session, today: date) -> Optional[DailyContent]:
        return db.query(DailyContent).filter(
            DailyContent.content_date == today,
            DailyContent.is_active == True
        ).order_by(DailyContent.created_at.desc()).first()

    @staticmethod
    def update(db: Session, dc: DailyContent, update_data: dict) -> DailyContent:
        for field, value in update_data.items():
            if hasattr(dc, field):
                setattr(dc, field, value)
        db.add(dc)
        db.commit()
        db.refresh(dc)
        return dc

    @staticmethod
    def soft_delete(db: Session, dc: DailyContent) -> DailyContent:
        dc.is_active = False
        db.add(dc)
        db.commit()
        db.refresh(dc)
        return dc
