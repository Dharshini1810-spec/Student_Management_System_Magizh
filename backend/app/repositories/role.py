from typing import Optional
from sqlalchemy.orm import Session
from app.models.role import Role, RolePermission, Permission


class RoleRepository:

    @staticmethod
    def get_all(db: Session) -> list[Role]:
        """Returns all roles ordered by id."""
        return db.query(Role).order_by(Role.id).all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Role]:
        """Fetches a role by its exact name string."""
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_permissions_for_role(db: Session, role_id: int) -> list[Permission]:
        """Returns all Permission objects assigned to a specific role."""
        return (
            db.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id == role_id)
            .order_by(Permission.name)
            .all()
        )
