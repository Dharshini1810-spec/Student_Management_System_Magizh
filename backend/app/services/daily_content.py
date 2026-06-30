import uuid
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from ..core.exceptions import AuthorizationException, NotFoundException
from ..core.permissions import UserRole
from ..models.user import User
from ..models.daily_content import DailyContent
from ..repositories.daily_content import DailyContentRepository
from ..repositories.user import UserRepository


class DailyContentService:

    @staticmethod
    def create(db: Session, requester: User, title: str, content: Optional[str], content_date: Optional[date]) -> DailyContent:
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value):
            raise AuthorizationException(
                message="Only Super Admins or Admins can create daily content.",
                code="DAILY_CONTENT_CREATE_FORBIDDEN",
            )
        if not content_date:
            content_date = datetime.now(timezone.utc).date()
        return DailyContentRepository.create(db=db, title=title, content=content, content_date=content_date, created_by=requester.id)

    @staticmethod
    def list_all(db: Session, requester: User, content_date: Optional[date] = None, limit: int = 50, offset: int = 0):
        return DailyContentRepository.list_all(db=db, content_date=content_date, limit=limit, offset=offset)

    @staticmethod
    def get_today(db: Session, requester: User) -> Optional[DailyContent]:
        return DailyContentRepository.get_today(db=db, today=datetime.now(timezone.utc).date())

    @staticmethod
    def get_by_id(db: Session, requester: User, content_id: uuid.UUID) -> DailyContent:
        dc = DailyContentRepository.get_by_id(db=db, content_id=content_id)
        if not dc:
            raise NotFoundException(message=f"Daily content with id '{content_id}' not found")
        return dc

    @staticmethod
    def update(db: Session, requester: User, content_id: uuid.UUID, update_data: dict) -> DailyContent:
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value):
            raise AuthorizationException(
                message="Only Super Admins or Admins can update daily content.",
                code="DAILY_CONTENT_UPDATE_FORBIDDEN",
            )
        dc = DailyContentRepository.get_by_id(db=db, content_id=content_id)
        if not dc:
            raise NotFoundException(message=f"Daily content with id '{content_id}' not found")
        return DailyContentRepository.update(db=db, dc=dc, update_data=update_data)

    @staticmethod
    def delete(db: Session, requester: User, content_id: uuid.UUID) -> DailyContent:
        if requester.role != UserRole.SUPER_ADMIN.value:
            raise AuthorizationException(
                message="Only Super Admins can delete daily content.",
                code="DAILY_CONTENT_DELETE_FORBIDDEN",
            )
        dc = DailyContentRepository.get_by_id(db=db, content_id=content_id)
        if not dc:
            raise NotFoundException(message=f"Daily content with id '{content_id}' not found")
        return DailyContentRepository.soft_delete(db=db, dc=dc)
