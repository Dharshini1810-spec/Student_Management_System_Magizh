import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, APIException
from app.core.permissions import UserRole
from app.models.user import User
from app.models.referral_link import ReferralLink
from app.repositories.referral_link import ReferralLinkRepository

class ReferralLinkService:
    @staticmethod
    def create_link(db: Session, requester: User, description: Optional[str] = None, max_uses: Optional[int] = None, expires_at: Optional[datetime] = None) -> ReferralLink:
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value, UserRole.MENTOR.value):
            raise APIException(message="Only Admins, Mentors, and Super Admins can create referral links", code="FORBIDDEN", status_code=403)
        return ReferralLinkRepository.create(db=db, user_id=requester.id, description=description, max_uses=max_uses, expires_at=expires_at)

    @staticmethod
    def get_link(db: Session, link_id: uuid.UUID) -> ReferralLink:
        link = ReferralLinkRepository.get_by_id(db, link_id)
        if not link:
            raise NotFoundException(message=f"Referral link with id '{link_id}' not found")
        return link

    @staticmethod
    def list_links(db: Session, requester: User) -> List[ReferralLink]:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return ReferralLinkRepository.list_all(db)
        return ReferralLinkRepository.list_by_user(db, requester.id)

    @staticmethod
    def deactivate_link(db: Session, requester: User, link_id: uuid.UUID) -> ReferralLink:
        link = ReferralLinkService.get_link(db, link_id)
        if link.user_id != requester.id and requester.role != UserRole.SUPER_ADMIN.value:
            raise APIException(message="You can only deactivate your own referral links", code="FORBIDDEN", status_code=403)
        return ReferralLinkRepository.soft_delete(db, link)

    @staticmethod
    def validate_code(db: Session, code: str) -> Optional[ReferralLink]:
        link = ReferralLinkRepository.get_by_code(db, code)
        if not link:
            return None
        if not link.is_active:
            return None
        if link.expires_at and link.expires_at < datetime.now(timezone.utc):
            return None
        if link.max_uses and link.current_uses >= link.max_uses:
            return None
        return link
