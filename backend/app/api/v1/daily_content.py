import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import APIException
from app.core.permissions import UserRole
from app.core.response import success_response
from app.models.user import User
from app.models.daily_content import DailyContent
from app.schemas.daily_content import DailyContentCreate, DailyContentUpdate, DailyContentRead
from app.services.daily_content import DailyContentService

router = APIRouter()


def map_daily_content_to_read(daily_content: DailyContent) -> DailyContentRead:
    return DailyContentRead(
        id=daily_content.id,
        title=daily_content.title,
        description=daily_content.description,
        links=daily_content.links,
        assigned_to=daily_content.assigned_to,
        assigned_to_name=daily_content.assignee.name if daily_content.assignee else None,
        assigned_by=daily_content.assigned_by,
        assigned_by_name=daily_content.assigner.name if daily_content.assigner else None,
        content_date=daily_content.content_date,
        is_deleted=daily_content.is_deleted,
        created_at=daily_content.created_at,
        updated_at=daily_content.updated_at,
    )


@router.post("", response_model=dict)
def create_daily_content(
    payload: DailyContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (UserRole.ADMIN.value, UserRole.MENTOR.value, UserRole.SUPER_ADMIN.value):
        raise APIException(
            message="Only Admins, Mentors, or Super Admins can create daily content.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    daily_content = DailyContentService.create_daily_content(
        db=db,
        requester=current_user,
        title=payload.title,
        description=payload.description,
        links=payload.links,
        assigned_to=payload.assigned_to,
        content_date=payload.content_date,
    )
    return success_response(
        data=map_daily_content_to_read(daily_content).model_dump(),
        message="Daily content created successfully.",
    )


@router.get("", response_model=dict)
def list_daily_contents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    daily_contents = DailyContentService.list_daily_contents(db=db, requester=current_user)
    daily_contents_data = [map_daily_content_to_read(item).model_dump() for item in daily_contents]
    return success_response(
        data={"daily_contents": daily_contents_data},
        message="Daily contents retrieved successfully.",
    )


@router.get("/{id}", response_model=dict)
def get_daily_content(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    daily_content = DailyContentService.get_daily_content(db=db, requester=current_user, daily_content_id=id)
    return success_response(
        data=map_daily_content_to_read(daily_content).model_dump(),
        message="Daily content retrieved successfully.",
    )


@router.put("/{id}", response_model=dict)
def update_daily_content(
    id: uuid.UUID,
    payload: DailyContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)
    daily_content = DailyContentService.update_daily_content(
        db=db,
        requester=current_user,
        daily_content_id=id,
        update_data=update_data,
    )
    return success_response(
        data=map_daily_content_to_read(daily_content).model_dump(),
        message="Daily content updated successfully.",
    )


@router.delete("/{id}", response_model=dict)
def delete_daily_content(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    daily_content = DailyContentService.delete_daily_content(db=db, requester=current_user, daily_content_id=id)
    return success_response(
        data=map_daily_content_to_read(daily_content).model_dump(),
        message="Daily content deleted successfully.",
    )
