from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_super_admin, require_roles
from app.core.permissions import UserRole
from app.api.deps import get_db, get_current_user
from app.core.response import success_response
from app.repositories.role_permission import RolePermissionRepository
from app.schemas.role import RoleRead

router = APIRouter()

@router.get("")
def list_roles(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all available roles in the system.
    """
    roles = RolePermissionRepository.get_all_roles(db)
    roles_data = [RoleRead.model_validate(r).model_dump() for r in roles]
    return success_response(
        data=roles_data,
        message="Roles retrieved successfully."
    )
