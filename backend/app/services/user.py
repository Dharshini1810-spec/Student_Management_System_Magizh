import uuid
from sqlalchemy.orm import Session

from app.core.exceptions import APIException, AuthorizationException, NotFoundException
from app.core.permissions import UserRole, PermissionName, _get_all_user_permissions
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.schemas.role import CreateUserRequest, UserPermissionsResponse


class UserService:

    @staticmethod
    def create_user(db: Session, requester: User, data: CreateUserRequest) -> User:
        """
        Creates a new user account.
        Only Super Admin may call this endpoint.
        The provided email + temporary password are set; is_first_login=True forces
        password change on next login.
        """
        if requester.role != UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="Only Super Admin can create user accounts",
                code="SUPER_ADMIN_REQUIRED"
            )

        # Ensure email is unique
        existing = UserRepository.get_by_email(db, data.email)
        if existing:
            raise APIException(
                message=f"A user with email '{data.email}' already exists",
                code="EMAIL_ALREADY_EXISTS",
                status_code=409
            )

        hashed_pw = get_password_hash(data.password)
        user = UserRepository.create(
            db=db,
            email=data.email,
            hashed_password=hashed_pw,
            role=data.role.value,
            is_first_login=True,  # Forces password change on first sign-in
        )
        return user

    @staticmethod
    def list_users(db: Session, requester: User) -> list[User]:
        """
        Returns a list of users.
        - Super Admin sees everyone.
        - Admin sees all non-super-admin users (further filtering in future phases).
        - Others cannot call this endpoint (enforced at route level).
        """
        if requester.role == UserRole.SUPER_ADMIN:
            return db.query(User).order_by(User.created_at.desc()).all()

        if requester.role == UserRole.ADMIN:
            # Admin sees all non-super-admin users
            return (
                db.query(User)
                .filter(User.role != UserRole.SUPER_ADMIN)
                .order_by(User.created_at.desc())
                .all()
            )

        raise AuthorizationException(
            message="You do not have permission to list users",
            code="INSUFFICIENT_PERMISSIONS"
        )

    @staticmethod
    def get_user(db: Session, requester: User, user_id: uuid.UUID) -> User:
        """
        Returns a specific user.
        Super Admin can fetch anyone; Admin can fetch non-super-admin users;
        others can only fetch themselves.
        """
        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        if requester.role == UserRole.SUPER_ADMIN:
            return target

        if requester.role == UserRole.ADMIN and target.role != UserRole.SUPER_ADMIN:
            return target

        # Allow users to fetch themselves
        if requester.id == user_id:
            return target

        raise AuthorizationException(
            message="You do not have permission to view this user",
            code="INSUFFICIENT_PERMISSIONS"
        )

    @staticmethod
    def update_user(db: Session, requester: User, user_id: uuid.UUID, update_data: dict) -> User:
        """
        Updates a user's fields.
        Requires 'users:update' permission (enforced at route level).
        Admin cannot update Super Admin accounts.
        """
        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        if requester.role != UserRole.SUPER_ADMIN and target.role == UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="Cannot modify a Super Admin account",
                code="INSUFFICIENT_PERMISSIONS"
            )

        return UserRepository.update(db, target, update_data)

    @staticmethod
    def deactivate_user(db: Session, requester: User, user_id: uuid.UUID) -> User:
        """
        Deactivates (soft-deletes) a user account.
        Only Super Admin or users with users:delete permission can call this.
        Cannot deactivate the Super Admin.
        """
        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        if target.role == UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="The Super Admin account cannot be deactivated",
                code="FORBIDDEN"
            )

        if requester.id == user_id:
            raise APIException(
                message="You cannot deactivate your own account",
                code="SELF_DEACTIVATION_FORBIDDEN",
                status_code=400
            )

        return UserRepository.update(db, target, {"is_active": False})

    @staticmethod
    def get_user_permissions(db: Session, requester: User, user_id: uuid.UUID) -> UserPermissionsResponse:
        """
        Returns the full permissions profile for a user:
        - Role-based permissions
        - Direct user_permission overrides
        - Combined set
        Super Admin can view anyone's permissions; others can only view their own.
        """
        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        # Authorization: Super Admin or self
        if requester.role != UserRole.SUPER_ADMIN and requester.id != user_id:
            raise AuthorizationException(
                message="You can only view your own permissions",
                code="INSUFFICIENT_PERMISSIONS"
            )

        # Role-based permissions
        role = RoleRepository.get_by_name(db, target.role)
        role_perms: list[str] = []
        if role:
            role_perms = [p.name for p in RoleRepository.get_permissions_for_role(db, role.id)]

        # Direct user_permissions
        direct_ups = PermissionRepository.get_user_permissions(db, user_id)
        direct_perms = [up.permission.name for up in direct_ups]

        all_perms = sorted(set(role_perms) | set(direct_perms))

        return UserPermissionsResponse(
            user_id=user_id,
            role=target.role,
            role_permissions=sorted(role_perms),
            direct_permissions=sorted(direct_perms),
            all_permissions=all_perms,
        )

    @staticmethod
    def assign_permission(
        db: Session,
        requester: User,
        user_id: uuid.UUID,
        permission_name: str,
    ) -> dict:
        """
        Grants a direct permission to a user (additive override).
        Only Super Admin can do this.
        """
        if requester.role != UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="Only Super Admin can assign permissions",
                code="SUPER_ADMIN_REQUIRED"
            )

        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        perm = PermissionRepository.get_by_name(db, permission_name)
        if not perm:
            raise APIException(
                message=f"Permission '{permission_name}' does not exist",
                code="PERMISSION_NOT_FOUND",
                status_code=404
            )

        up = PermissionRepository.assign_to_user(
            db=db,
            user_id=user_id,
            permission_id=perm.id,
            granted_by=requester.id,
        )
        return {
            "user_id": str(user_id),
            "permission": permission_name,
            "granted_at": up.granted_at.isoformat(),
        }

    @staticmethod
    def revoke_permission(
        db: Session,
        requester: User,
        user_id: uuid.UUID,
        permission_name: str,
    ) -> dict:
        """
        Revokes a direct user permission.
        Only Super Admin can do this.
        """
        if requester.role != UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="Only Super Admin can revoke permissions",
                code="SUPER_ADMIN_REQUIRED"
            )

        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        perm = PermissionRepository.get_by_name(db, permission_name)
        if not perm:
            raise APIException(
                message=f"Permission '{permission_name}' does not exist",
                code="PERMISSION_NOT_FOUND",
                status_code=404
            )

        removed = PermissionRepository.revoke_from_user(db, user_id, perm.id)
        if not removed:
            raise APIException(
                message=f"User does not have direct permission '{permission_name}'",
                code="PERMISSION_NOT_ASSIGNED",
                status_code=404
            )
        return {"user_id": str(user_id), "permission": permission_name, "revoked": True}

    @staticmethod
    def admin_reset_password(db: Session, requester: User, user_id: uuid.UUID) -> dict:
        """
        Super Admin forces a password reset for another user.
        Generates and returns a reset token (in development mode, returned directly).
        """
        if requester.role != UserRole.SUPER_ADMIN:
            raise AuthorizationException(
                message="Only Super Admin can force password resets",
                code="SUPER_ADMIN_REQUIRED"
            )

        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")

        if target.role == UserRole.SUPER_ADMIN:
            raise APIException(
                message="Cannot force-reset the Super Admin password via this endpoint",
                code="FORBIDDEN",
                status_code=403
            )

        # Delegate to auth service's forgot_password flow
        from app.services.auth import AuthService
        token = AuthService.forgot_password(db, email=target.email)
        return {
            "user_id": str(user_id),
            "email": target.email,
            "reset_token": token,
            "message": "Password reset token generated. Share with the user to reset their password.",
        }
