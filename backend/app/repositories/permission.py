import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.role import Permission, UserPermission


class PermissionRepository:

    @staticmethod
    def get_all(db: Session) -> list[Permission]:
        """Returns all permissions ordered alphabetically."""
        return db.query(Permission).order_by(Permission.name).all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Permission]:
        """Fetches a permission by its exact name string (e.g. 'users:create')."""
        return db.query(Permission).filter(Permission.name == name).first()

    @staticmethod
    def get_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        """Fetches a permission by id."""
        return db.query(Permission).filter(Permission.id == permission_id).first()

    @staticmethod
    def get_user_permissions(db: Session, user_id: uuid.UUID) -> list[UserPermission]:
        """Returns all direct UserPermission records for a given user (with Permission eager-loaded)."""
        return (
            db.query(UserPermission)
            .filter(UserPermission.user_id == user_id)
            .all()
        )

    @staticmethod
    def assign_to_user(
        db: Session,
        user_id: uuid.UUID,
        permission_id: int,
        granted_by: uuid.UUID,
    ) -> UserPermission:
        """
        Assigns a permission directly to a user (idempotent — no duplicate entries).
        Returns the existing or newly created UserPermission.
        """
        existing = db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id,
        ).first()

        if existing:
            return existing

        up = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            granted_by=granted_by,
        )
        db.add(up)
        db.commit()
        db.refresh(up)
        return up

    @staticmethod
    def revoke_from_user(
        db: Session,
        user_id: uuid.UUID,
        permission_id: int,
    ) -> bool:
        """
        Revokes a direct user permission. Returns True if it was removed, False if not found.
        """
        up = db.query(UserPermission).filter(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id,
        ).first()

        if not up:
            return False

        db.delete(up)
        db.commit()
        return True
