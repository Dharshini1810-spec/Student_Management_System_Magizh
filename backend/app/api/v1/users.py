import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionRequired, RoleRequired, check_data_access
from app.core.permissions import UserRole
from app.core.security import get_password_hash
from app.core.exceptions import APIException
from app.core.response import success_response
from app.models.user import User
from app.repositories.user import UserRepository
from typing import Optional
from app.schemas.user import UserCreate, UserRead, UserUpdate

from app.repositories.role_permission import RolePermissionRepository
from app.schemas.permission import PermissionRead, UserPermissionGrant, UserPermissionRead

router = APIRouter()

DEFAULT_STANDARD_PASSWORD = "StandardPassword123!"

@router.get("", response_model=dict)
def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_deleted: bool = False,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of users, with support for pagination, search, role filters,
    and active/inactive filters. Scopes returned users based on the caller's role:
    - Super Admin: All users.
    - Admin: Mentors and Students assigned to the Admin.
    - Mentor: Students assigned to the Mentor.
    - Student: Only their own profile.
    """
    # Restrict include_deleted to Super Admin only
    if include_deleted and current_user.role != UserRole.SUPER_ADMIN.value:
        raise APIException(
            message="Only Super Admins can query deleted users.",
            code="UNAUTHORIZED",
            status_code=status.HTTP_403_FORBIDDEN
        )

    # Set scoping filters based on caller role
    admin_id = None
    mentor_id = None
    student_id = None

    if current_user.role == UserRole.ADMIN.value:
        admin_id = current_user.id
    elif current_user.role == UserRole.MENTOR.value:
        mentor_id = current_user.id
    elif current_user.role == UserRole.STUDENT.value:
        student_id = current_user.id

    users, total_count = UserRepository.get_all(
        db=db,
        role=role,
        search_query=search,
        is_active=is_active,
        include_deleted=include_deleted,
        admin_id=admin_id,
        mentor_id=mentor_id,
        student_id=student_id,
        limit=limit,
        offset=offset
    )

    users_data = [UserRead.model_validate(u).model_dump() for u in users]
    return success_response(
        data={
            "users": users_data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        },
        message="Users retrieved successfully."
    )

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(PermissionRequired("users:create")),
    db: Session = Depends(get_db)
):
    """
    Creates a new user (Admin, Mentor, Student) with a default standard password.
    
    Rules:
    - Super Admin can create any user, automatically approved.
    - Admin can create Mentors and Students. Students require Super Admin approval (created with is_approved=False).
    - Newly created users are set with is_first_login=True so they must change password.
    """
    # Check duplicate email
    existing_user = UserRepository.get_by_email(db, user_in.email)
    if existing_user:
        raise APIException(
            message="A user with this email already exists.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Validate roles and assignments
    role_upper = user_in.role.upper()
    if role_upper not in [r.value for r in UserRole]:
        raise APIException(
            message=f"Invalid role: {user_in.role}",
            code="INVALID_ROLE",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Default approval state
    is_approved = True
    admin_id = user_in.admin_id
    mentor_id = user_in.mentor_id

    # If the creator is an Admin, they can only create Mentors and Students
    if current_user.role == UserRole.ADMIN.value:
        if role_upper not in [UserRole.STUDENT.value, UserRole.MENTOR.value]:
            raise APIException(
                message="Admins are only authorized to create Mentors and Students.",
                code="UNAUTHORIZED_ROLE_CREATION",
                status_code=status.HTTP_403_FORBIDDEN
            )
        # Student created by Admin requires Super Admin approval, Mentor does not
        if role_upper == UserRole.STUDENT.value:
            is_approved = False
        else:
            is_approved = True

        # User must be assigned to the creating Admin
        admin_id = current_user.id

        # Verify mentor if provided
        if mentor_id:
            mentor = UserRepository.get_by_id(db, mentor_id)
            if not mentor or mentor.role != UserRole.MENTOR.value or mentor.admin_id != current_user.id:
                raise APIException(
                    message="Mentor must be a valid mentor assigned to you.",
                    code="INVALID_MENTOR_ASSIGNMENT",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

    # If creator is Super Admin, validate assignments
    elif current_user.role == UserRole.SUPER_ADMIN.value:
        if role_upper == UserRole.STUDENT.value:
            # Super Admin can create student directly, defaults to approved
            is_approved = True
            # Validate Admin assignment if provided
            if admin_id:
                adm = UserRepository.get_by_id(db, admin_id)
                if not adm or adm.role != UserRole.ADMIN.value:
                    raise APIException(
                        message="Assigned admin must be a valid Admin.",
                        code="INVALID_ADMIN_ASSIGNMENT",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            # Validate Mentor assignment if provided
            if mentor_id:
                men = UserRepository.get_by_id(db, mentor_id)
                if not men or men.role != UserRole.MENTOR.value:
                    raise APIException(
                        message="Assigned mentor must be a valid Mentor.",
                        code="INVALID_MENTOR_ASSIGNMENT",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

    # Hash the default standard password
    hashed_pw = get_password_hash(DEFAULT_STANDARD_PASSWORD)

    # Create the user
    new_user = UserRepository.create(
        db=db,
        email=user_in.email,
        hashed_password=hashed_pw,
        role=role_upper,
        name=user_in.name,
        is_first_login=True,
        is_approved=is_approved,
        admin_id=admin_id,
        mentor_id=mentor_id
    )

    user_read = UserRead.model_validate(new_user)
    
    message = "User created successfully."
    if not is_approved:
        message += " Pending Super Admin approval."

    return success_response(
        data=user_read.model_dump(),
        message=message
    )

@router.post("/{user_id}/approve")
def approve_student(
    user_id: uuid.UUID,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint to approve a student created by an Admin.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    if target_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Only student accounts can be approved",
            code="INVALID_APPROVAL_TARGET",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if target_user.is_approved:
        return success_response(
            message="Student is already approved."
        )

    UserRepository.update(db, target_user, {"is_approved": True})
    
    return success_response(
        message="Student approved successfully."
    )

@router.get("/{user_id}")
def get_user_profile(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves user profile details. Enforces data scoping rules.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Scoping checks
    check_data_access(current_user, target_user)

    user_read = UserRead.model_validate(target_user)
    return success_response(
        data=user_read.model_dump(),
        message="User profile retrieved successfully."
    )

@router.put("/{user_id}")
def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edits a user profile. Enforces data scoping rules:
    - Super Admin can edit any user.
    - Admin can edit assigned mentors/students (but cannot change roles).
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Scoping checks
    check_data_access(current_user, target_user)

    update_dict = user_update.model_dump(exclude_unset=True)

    # Restriction: Only Super Admin can change a user's role
    if "role" in update_dict:
        if current_user.role != UserRole.SUPER_ADMIN.value:
            raise APIException(
                message="Only Super Admins are authorized to change user roles.",
                code="UNAUTHORIZED_ROLE_CHANGE",
                status_code=status.HTTP_403_FORBIDDEN
            )
        role_upper = update_dict["role"].upper()
        if role_upper not in [r.value for r in UserRole]:
            raise APIException(
                message=f"Invalid role: {update_dict['role']}",
                code="INVALID_ROLE",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        update_dict["role"] = role_upper

    # Restriction: Admin can only assign mentor/student to valid ones
    if current_user.role == UserRole.ADMIN.value:
        # Admins cannot re-assign admin_id
        if "admin_id" in update_dict and update_dict["admin_id"] != current_user.id:
            raise APIException(
                message="Admins cannot change the assigned Admin of this user.",
                code="UNAUTHORIZED_ADMIN_CHANGE",
                status_code=status.HTTP_403_FORBIDDEN
            )
        # If changing mentor_id (only for students), verify that the mentor belongs to the Admin
        if "mentor_id" in update_dict and update_dict["mentor_id"] is not None:
            mentor = UserRepository.get_by_id(db, update_dict["mentor_id"])
            if not mentor or mentor.role != UserRole.MENTOR.value or mentor.admin_id != current_user.id:
                raise APIException(
                    message="Mentor must be a valid mentor assigned to you.",
                    code="INVALID_MENTOR_ASSIGNMENT",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

    # Perform update
    updated_user = UserRepository.update(db, target_user, update_dict)
    user_read = UserRead.model_validate(updated_user)
    return success_response(
        data=user_read.model_dump(),
        message="User updated successfully."
    )

@router.delete("/{user_id}")
def soft_delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Soft deletes a user. Restricted to Super Admin.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    UserRepository.update(db, target_user, {"is_deleted": True})
    return success_response(
        message="User soft-deleted successfully."
    )

@router.patch("/{user_id}/activate")
def activate_user(
    user_id: uuid.UUID,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Activates a user. Restricted to Super Admin.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    UserRepository.update(db, target_user, {"is_active": True})
    return success_response(
        message="User activated successfully."
    )

@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: uuid.UUID,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Deactivates a user. Restricted to Super Admin.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    UserRepository.update(db, target_user, {"is_active": False})
    return success_response(
        message="User deactivated successfully."
    )

@router.patch("/{user_id}/reset-password")
def reset_user_password(
    user_id: uuid.UUID,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Resets user password to standard default and sets is_first_login to True.
    Restricted to Super Admin.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user or target_user.is_deleted:
        raise APIException(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    hashed_pw = get_password_hash(DEFAULT_STANDARD_PASSWORD)
    UserRepository.update(db, target_user, {
        "hashed_password": hashed_pw,
        "is_first_login": True
    })
    return success_response(
        message=f"User password reset successfully to standard default '{DEFAULT_STANDARD_PASSWORD}'."
    )

@router.post("/{user_id}/permissions")
def grant_user_permission(
    user_id: uuid.UUID,
    grant_in: UserPermissionGrant,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint to grant a custom permission override directly to a user.
    """
    # Verify user exists
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user:
        raise APIException(
            message="Target user not found.",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Verify permission exists
    permission = RolePermissionRepository.get_permission_by_id(db, grant_in.permission_id)
    if not permission:
        raise APIException(
            message="Permission not found.",
            code="PERMISSION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Check if already granted
    existing_grant = RolePermissionRepository.get_user_permission(db, user_id, grant_in.permission_id)
    if existing_grant:
        raise APIException(
            message="User already has this custom permission granted.",
            code="PERMISSION_ALREADY_GRANTED",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Grant permission
    user_perm = RolePermissionRepository.grant_custom_permission(
        db=db,
        user_id=user_id,
        permission_id=grant_in.permission_id,
        granted_by=current_user.id
    )

    user_perm_read = UserPermissionRead.model_validate(user_perm)
    return success_response(
        data=user_perm_read.model_dump(),
        message=f"Permission '{permission.name}' successfully granted to user."
    )

@router.delete("/{user_id}/permissions/{permission_id}")
def revoke_user_permission(
    user_id: uuid.UUID,
    permission_id: int,
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Super Admin endpoint to revoke a custom direct permission override from a user.
    """
    revoked = RolePermissionRepository.revoke_custom_permission(db, user_id, permission_id)
    if not revoked:
        raise APIException(
            message="Custom permission grant not found for this user.",
            code="GRANT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return success_response(
        message="Custom permission successfully revoked from user."
    )

@router.get("/{user_id}/permissions")
def get_user_permissions(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all permissions for a user, categorized by role-based and custom-granted.
    Enforces data scoping checks.
    """
    target_user = UserRepository.get_by_id(db, user_id)
    if not target_user:
        raise APIException(
            message="User not found.",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Scoping checks
    check_data_access(current_user, target_user)

    # 1. Role-based permissions
    role_perms = RolePermissionRepository.get_role_permissions(db, target_user.role)
    role_perms_data = [PermissionRead.model_validate(p).model_dump() for p in role_perms]

    # 2. Custom override permissions
    custom_perms = RolePermissionRepository.get_custom_permissions(db, target_user.id)
    custom_perms_data = [UserPermissionRead.model_validate(cp).model_dump() for cp in custom_perms]

    # 3. Combined distinct permissions list
    combined_names = set(p.name for p in role_perms) | set(cp.permission.name for cp in custom_perms)

    # Bypass logic if SUPER_ADMIN
    if target_user.role == UserRole.SUPER_ADMIN.value:
        # Super admin has all permissions implicitly
        all_perms = RolePermissionRepository.get_all_permissions(db)
        combined_names = set(p.name for p in all_perms)

    return success_response(
        data={
            "role_permissions": role_perms_data,
            "custom_permissions": custom_perms_data,
            "all_permission_names": list(combined_names),
        },
        message="User permissions retrieved successfully."
    )

