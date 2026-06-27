import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.core.response import success_response
from app.models.user import User
from app.repositories.activity_log import ActivityLogRepository
from app.schemas.activity_log import ActivityLogRead

router = APIRouter()

@router.get("", )
def list_all_logs(
    user_id: Optional[uuid.UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN.value:
        raise APIException(
            message="Only Super Admin can view all activity logs.",
            code="FORBIDDEN",
            status_code=403
        )

    logs, total = ActivityLogRepository.list_all(
        db=db, user_id=user_id, date_from=date_from,
        date_to=date_to, limit=limit, offset=offset
    )
    logs_data = [ActivityLogRead.model_validate(l).model_dump() for l in logs]
    return success_response(
        data={"logs": logs_data, "total": total, "limit": limit, "offset": offset},
        message="Activity logs retrieved successfully."
    )

@router.get("/me", )
def list_my_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grouped = ActivityLogRepository.list_by_user_grouped(db, current_user.id)
    return success_response(
        data={"logs": grouped},
        message="Your activity logs retrieved successfully."
    )
