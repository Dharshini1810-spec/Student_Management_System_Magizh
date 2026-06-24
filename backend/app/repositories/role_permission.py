import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_permission import UserPermission

class RolePermissionRepository:
    @staticmethod
    def get_all_roles(db: Session) -> List[Role]:
        return db.query(Role).order_by(Role.id).all()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_all_permissions(db: Session) -> List[Permission]:
        return db.query(Permission).order_by(Permission.id).all()

    @staticmethod
    def get_permission_by_id(db: Session, perm_id: int) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.id == perm_id).first()

    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.name == name).first()

    @staticmethod
    def get_role_permissions(db: Session, role_name: str) -> List[Permission]:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return []
        return role.permissions

    @staticmethod
    def get_custom_permissions(db: Session, user_id: uuid.UUID) -> List[UserPermission]:
        return db.query(UserPermission).filter(UserPermission.user_id == user_id).all()

    @staticmethod
    def get_user_permission(db: Session, user_id: uuid.UUID, permission_id: int) -> Optional[UserPermission]:
        return db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id
        ).first()

    @staticmethod
    def grant_custom_permission(
        db: Session,
        user_id: uuid.UUID,
        permission_id: int,
        granted_by: Optional[uuid.UUID] = None
    ) -> UserPermission:
        db_user_perm = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            granted_by=granted_by
        )
        db.add(db_user_perm)
        db.commit()
        db.refresh(db_user_perm)
        return db_user_perm

    @staticmethod
    def revoke_custom_permission(db: Session, user_id: uuid.UUID, permission_id: int) -> bool:
        db_user_perm = RolePermissionRepository.get_user_permission(db, user_id, permission_id)
        if not db_user_perm:
            return False
        db.delete(db_user_perm)
        db.commit()
        return True
