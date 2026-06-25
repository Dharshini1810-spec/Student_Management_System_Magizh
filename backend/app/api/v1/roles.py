from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
<<<<<<< HEAD
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
=======
from app.core.permissions import require_roles, UserRole
from app.core.response import success_response
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.schemas.role import RoleRead, PermissionRead

router = APIRouter()


@router.get("/roles", response_model=None, tags=["Roles & Permissions"])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all system roles with their assigned permissions.
    Accessible by all authenticated users.
    """
    roles = RoleRepository.get_all(db)
    result = []
    for role in roles:
        perms = RoleRepository.get_permissions_for_role(db, role.id)
        result.append({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": [{"id": p.id, "name": p.name, "description": p.description} for p in perms],
        })
    return success_response(data=result, message="Roles retrieved successfully")


@router.get("/permissions", response_model=None, tags=["Roles & Permissions"])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all system permissions.
    Accessible by all authenticated users.
    """
    perms = PermissionRepository.get_all(db)
    data = [{"id": p.id, "name": p.name, "description": p.description} for p in perms]
    return success_response(data=data, message="Permissions retrieved successfully")
>>>>>>> fcf518897bf1e7d68bc46b20f3d81c9d5f561424
