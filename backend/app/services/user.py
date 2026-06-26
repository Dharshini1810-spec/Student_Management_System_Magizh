import uuid
from sqlalchemy.orm import Session

from ..core.exceptions import APIException, AuthorizationException, NotFoundException
from ..core.permissions import UserRole, PermissionName
from ..core.security import get_password_hash
from ..models.user import User
from ..repositories.user import UserRepository
from ..repositories.role import RoleRepository
from ..repositories.permission import PermissionRepository
from ..schemas.role import CreateUserRequest, UserPermissionsResponse
from .auth import AuthService


class UserService:

    @staticmethod
    def create_user(db: Session, requester: User, data: CreateUserRequest) -> User:
        """
        Creates a new user account.
        Only Super Admin may call this endpoint.
        The provided email + temporary password are set; is_first_login=True forces
        password change on next login.
        """
        if requester.role == UserRole.SUPER_ADMIN:
            # Super Admin can create any role
            allowed_roles = {UserRole.ADMIN, UserRole.MENTOR, UserRole.STUDENT}
        elif requester.role == UserRole.ADMIN:
            # Admin can only create Mentor or Student
            allowed_roles = {UserRole.MENTOR, UserRole.STUDENT}
        else:
            raise AuthorizationException(
                message="Insufficient permissions to create a user",
                code="CREATE_USER_FORBIDDEN"
            )

        if data.role not in allowed_roles:
            raise AuthorizationException(
                message=f"{requester.role} cannot create a user with role {data.role}",
                code="ROLE_CREATION_FORBIDDEN"
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
    def list_users(
        db: Session,
        requester: User,
        *,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        role_filter: str | None = None,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> list[User]:
        """
        Returns a paginated list of users with optional search and filters.
        - Super Admin sees everyone.
        - Admin sees all non-super-admin users.
        - Filters are applied after role restrictions.
        """
        query = db.query(User)
        # Role restrictions
        if requester.role == UserRole.ADMIN:
            query = query.filter(User.role != UserRole.SUPER_ADMIN)

        # Apply soft-delete filter
        if not include_deleted:
            query = query.filter(User.is_deleted == False)  # noqa: E712

        # Apply search (email or name)
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                (User.email.ilike(search_term)) | (User.name.ilike(search_term))
            )

        # Role filter
        if role_filter:
            query = query.filter(User.role == role_filter)

        # Active filter
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Pagination
        offset = (page - 1) * page_size
        users = (
            query.order_by(User.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return users

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
    def activate_user(db: Session, requester: User, user_id: uuid.UUID) -> User:
        """
        Reactivates a previously deactivated user (set is_active=True).
        Only Super Admin or users with appropriate permission can call.
        """
        target = UserRepository.get_by_id(db, user_id)
        if not target:
            raise NotFoundException(message=f"User with id '{user_id}' not found")
        if target.role == UserRole.SUPER_ADMIN:
            raise AuthorizationException(message="Cannot activate a Super Admin account", code="FORBIDDEN")
        if target.is_active:
            raise APIException(message="User is already active", code="ALREADY_ACTIVE", status_code=400)
        return UserRepository.update(db, target, {"is_active": True})

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
        token = AuthService.forgot_password(db, email=target.email)
        return {
            "user_id": str(user_id),
            "email": target.email,
            "reset_token": token,
            "message": "Password reset token generated. Share with the user to reset their password.",
        }
