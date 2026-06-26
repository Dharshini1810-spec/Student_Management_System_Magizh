import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session

from ..core.exceptions import APIException, AuthorizationException, NotFoundException
from ..core.permissions import UserRole
from ..models.user import User
from ..models.daily_content import DailyContent
from ..repositories.daily_content import DailyContentRepository
from ..repositories.user import UserRepository

class DailyContentService:

    @staticmethod
    def create_daily_content(
        db: Session,
        requester: User,
        title: str,
        content_date: date,
        assigned_to: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        links: Optional[list[str]] = None,
    ) -> DailyContent:
        if requester.role not in (
            UserRole.ADMIN.value,
            UserRole.MENTOR.value,
            UserRole.SUPER_ADMIN.value,
        ):
            raise AuthorizationException(
                message="Only Admins, Mentors, or Super Admins can create daily content.",
                code="DAILY_CONTENT_CREATE_FORBIDDEN",
            )

        if not assigned_to:
            raise APIException(
                message="Daily content must be assigned to a student.",
                code="ASSIGNED_TO_REQUIRED",
                status_code=400,
            )

        assigned_user = UserRepository.get_by_id(db, assigned_to)
        if not assigned_user or assigned_user.role != UserRole.STUDENT.value:
            raise APIException(
                message="Assigned user must be an existing student.",
                code="INVALID_ASSIGNED_TO",
                status_code=400,
            )

        return DailyContentRepository.create(
            db=db,
            title=title,
            assigned_by=requester.id,
            assigned_to=assigned_to,
            description=description,
            links=links,
            content_date=content_date,
        )

    @staticmethod
    def list_daily_contents(db: Session, requester: User) -> List[DailyContent]:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return DailyContentRepository.list_all(db)
        if requester.role in (UserRole.ADMIN.value, UserRole.MENTOR.value):
            return DailyContentRepository.list_created_by(db, requester.id)
        return DailyContentRepository.list_by_assigned_to(db, requester.id)

    @staticmethod
    def get_daily_content(db: Session, requester: User, daily_content_id: uuid.UUID) -> DailyContent:
        daily_content = DailyContentRepository.get_by_id(db, daily_content_id)
        if not daily_content:
            raise NotFoundException(message=f"Daily content with id '{daily_content_id}' not found")
        DailyContentService.check_access(requester, daily_content)
        return daily_content

    @staticmethod
    def check_access(requester: User, daily_content: DailyContent) -> None:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return

        if requester.role in (UserRole.ADMIN.value, UserRole.MENTOR.value):
            if daily_content.assigned_by == requester.id:
                return
            raise AuthorizationException(
                message="You do not have permission to access this daily content.",
                code="ACCESS_DENIED",
            )

        if requester.role == UserRole.STUDENT.value:
            if daily_content.assigned_to == requester.id:
                return
            raise AuthorizationException(
                message="You do not have permission to access this daily content.",
                code="ACCESS_DENIED",
            )

        raise AuthorizationException(
            message="You do not have permission to access this daily content.",
            code="ACCESS_DENIED",
        )

    @staticmethod
    def update_daily_content(
        db: Session,
        requester: User,
        daily_content_id: uuid.UUID,
        update_data: dict,
    ) -> DailyContent:
        if requester.role not in (
            UserRole.ADMIN.value,
            UserRole.MENTOR.value,
            UserRole.SUPER_ADMIN.value,
        ):
            raise AuthorizationException(
                message="Only Admins, Mentors, or Super Admins can update daily content.",
                code="DAILY_CONTENT_UPDATE_FORBIDDEN",
            )

        daily_content = DailyContentRepository.get_by_id(db, daily_content_id)
        if not daily_content:
            raise NotFoundException(message=f"Daily content with id '{daily_content_id}' not found")

        if requester.role != UserRole.SUPER_ADMIN.value and daily_content.assigned_by != requester.id:
            raise AuthorizationException(
                message="You can only update daily content you created.",
                code="ACCESS_DENIED",
            )

        if "assigned_to" in update_data and update_data["assigned_to"] is not None:
            assigned_user = UserRepository.get_by_id(db, update_data["assigned_to"])
            if not assigned_user or assigned_user.role != UserRole.STUDENT.value:
                raise APIException(
                    message="Assigned user must be an existing student.",
                    code="INVALID_ASSIGNED_TO",
                    status_code=400,
                )

        return DailyContentRepository.update(db, daily_content, update_data)

    @staticmethod
    def delete_daily_content(db: Session, requester: User, daily_content_id: uuid.UUID) -> DailyContent:
        if requester.role not in (
            UserRole.ADMIN.value,
            UserRole.MENTOR.value,
            UserRole.SUPER_ADMIN.value,
        ):
            raise AuthorizationException(
                message="Only Admins, Mentors, or Super Admins can delete daily content.",
                code="DAILY_CONTENT_DELETE_FORBIDDEN",
            )

        daily_content = DailyContentRepository.get_by_id(db, daily_content_id)
        if not daily_content:
            raise NotFoundException(message=f"Daily content with id '{daily_content_id}' not found")

        if requester.role != UserRole.SUPER_ADMIN.value and daily_content.assigned_by != requester.id:
            raise AuthorizationException(
                message="You can only delete daily content you created.",
                code="ACCESS_DENIED",
            )

        return DailyContentRepository.soft_delete(db, daily_content)
