import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, RoleRequired, check_data_access
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.core.response import success_response
from app.repositories.role_permission import RolePermissionRepository
from app.repositories.user import UserRepository
from app.schemas.permission import PermissionRead, UserPermissionGrant, UserPermissionRead

router = APIRouter()

@router.get("")
def list_permissions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all available permissions in the system.
    """
    permissions = RolePermissionRepository.get_all_permissions(db)
    perms_data = [PermissionRead.model_validate(p).model_dump() for p in permissions]
    return success_response(
        data=perms_data,
        message="Permissions retrieved successfully."
    )
