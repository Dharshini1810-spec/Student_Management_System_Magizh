import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.referral_link import ReferralLink

class ReferralLinkRepository:
    @staticmethod
    def create(db: Session, user_id: uuid.UUID, description: Optional[str] = None, max_uses: Optional[int] = None, expires_at: Optional[datetime] = None) -> ReferralLink:
        link = ReferralLink(
            user_id=user_id,
            description=description,
            max_uses=max_uses,
            expires_at=expires_at
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def get_by_id(db: Session, link_id: uuid.UUID) -> Optional[ReferralLink]:
        return db.query(ReferralLink).filter(ReferralLink.id == link_id).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[ReferralLink]:
        return db.query(ReferralLink).filter(ReferralLink.code == code).first()

    @staticmethod
    def list_by_user(db: Session, user_id: uuid.UUID) -> List[ReferralLink]:
        return db.query(ReferralLink).filter(
            ReferralLink.user_id == user_id
        ).order_by(ReferralLink.created_at.desc()).all()

    @staticmethod
    def list_all(db: Session) -> List[ReferralLink]:
        return db.query(ReferralLink).order_by(ReferralLink.created_at.desc()).all()

    @staticmethod
    def update(db: Session, link: ReferralLink, update_data: dict) -> ReferralLink:
        for field, value in update_data.items():
            if hasattr(link, field):
                setattr(link, field, value)
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def increment_uses(db: Session, link: ReferralLink) -> ReferralLink:
        link.current_uses += 1
        if link.max_uses and link.current_uses >= link.max_uses:
            link.is_active = False
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def soft_delete(db: Session, link: ReferralLink) -> ReferralLink:
        link.is_active = False
        db.add(link)
        db.commit()
        db.refresh(link)
        return link
