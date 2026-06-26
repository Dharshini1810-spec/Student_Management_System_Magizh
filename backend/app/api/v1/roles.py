from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_super_admin, require_roles
from app.core.permissions import UserRole
from app.core.response import success_response
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.schemas.role import RoleRead, PermissionRead

router = APIRouter()


@router.get("/roles", response_model=None, tags=["Roles & Permissions"])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin()),
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
    current_user: User = Depends(require_super_admin()),
):
    """
    Returns all system permissions.
    Accessible by all authenticated users.
    """
    perms = PermissionRepository.get_all(db)
    data = [{"id": p.id, "name": p.name, "description": p.description} for p in perms]
    return success_response(data=data, message="Permissions retrieved successfully")
