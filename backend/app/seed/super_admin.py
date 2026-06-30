import logging
from sqlalchemy.orm import Session

from ..repositories.user import UserRepository
from ..core.security import get_password_hash
from ..core.permissions import UserRole, PermissionName

logger = logging.getLogger(__name__)


# ─── Permission assignments per role ───────────────────────────────────────────

ROLE_PERMISSIONS: dict[str, list[str]] = {
    UserRole.SUPER_ADMIN: [p.value for p in PermissionName],  # All permissions
    UserRole.ADMIN: [
        PermissionName.USERS_UPDATE.value,
        PermissionName.USERS_DELETE.value,
        PermissionName.STUDENTS_VIEW.value,
        PermissionName.STUDENTS_CREATE.value,
        PermissionName.STUDENTS_UPDATE.value,
        PermissionName.ATTENDANCE_MANAGE.value,
        PermissionName.PROJECTS_ASSIGN.value,
        PermissionName.TODOS_ASSIGN.value,
        PermissionName.DAILY_CONTENT_ASSIGN.value,
        PermissionName.REPORTS_VIEW.value,
    ],
    UserRole.MENTOR: [
        PermissionName.STUDENTS_VIEW.value,
        PermissionName.ATTENDANCE_MANAGE.value,
        PermissionName.PROJECTS_ASSIGN.value,
        PermissionName.TODOS_ASSIGN.value,
        PermissionName.DAILY_CONTENT_ASSIGN.value,
        PermissionName.REPORTS_VIEW.value,
    ],
    UserRole.STUDENT: [
        PermissionName.STUDENTS_VIEW.value,  # Own data only — enforced in service layer
    ],
}

# Human-readable descriptions
PERMISSION_DESCRIPTIONS: dict[str, str] = {
    PermissionName.USERS_CREATE.value: "Create new user accounts",
    PermissionName.USERS_UPDATE.value: "Update user account details",
    PermissionName.USERS_DELETE.value: "Deactivate or delete user accounts",
    PermissionName.STUDENTS_VIEW.value: "View student profiles and data",
    PermissionName.STUDENTS_CREATE.value: "Create student records",
    PermissionName.STUDENTS_UPDATE.value: "Update student records",
    PermissionName.ATTENDANCE_MANAGE.value: "Manage attendance records",
    PermissionName.PROJECTS_ASSIGN.value: "Assign projects to students",
    PermissionName.TODOS_ASSIGN.value: "Assign to-do tasks to students",
    PermissionName.DAILY_CONTENT_ASSIGN.value: "Assign daily content to students",
    PermissionName.REPORTS_VIEW.value: "View reports and analytics",
}

ROLE_DESCRIPTIONS: dict[str, str] = {
    UserRole.SUPER_ADMIN: "Full system access — manages all users and permissions",
    UserRole.ADMIN: "Manages assigned mentors and students",
    UserRole.MENTOR: "Manages assigned students",
    UserRole.STUDENT: "Access to own data only",
}


from ..models.role import Role
from ..models.permission import Permission
from ..models.role_permission import RolePermission

def seed_roles_and_permissions(db: Session) -> None:
    """
    Idempotently seeds all roles and permissions, then assigns them.
    Safe to run on every startup.
    """
    logger.info("Seeding roles and permissions...")

    # 1. Seed Roles
    role_objects: dict[str, Role] = {}
    for role_name in UserRole:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            role = Role(name=role_name, description=ROLE_DESCRIPTIONS.get(role_name))
            db.add(role)
            db.flush()
            role_objects[role_name] = role
            logger.info(f"  Created role: {role_name}")
        else:
            role_objects[role_name] = existing

    # 2. Seed Permissions
    perm_objects: dict[str, Permission] = {}
    for perm in PermissionName:
        existing = db.query(Permission).filter(Permission.name == perm.value).first()
        if not existing:
            p = Permission(name=perm.value, description=PERMISSION_DESCRIPTIONS.get(perm.value))
            db.add(p)
            db.flush()
            perm_objects[perm.value] = p
            logger.info(f"  Created permission: {perm.value}")
        else:
            perm_objects[perm.value] = existing

    # 3. Assign permissions to roles
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        role = role_objects[role_name]
        for perm_name in perm_names:
            perm = perm_objects[perm_name]
            exists = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id
            ).first()
            if not exists:
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
                logger.info(f"  Assigned {perm_name} → {role_name}")

    db.commit()
    logger.info("Roles and permissions seeded successfully.")


def seed_super_admin(db: Session) -> None:
    """
    Seeds a default super admin user if one doesn't exist.
    Also triggers roles and permissions seeding on every startup.
    """
    # Always seed roles & permissions first (idempotent)
    seed_roles_and_permissions(db)

    logger.info("Checking if super admin user needs to be seeded...")

    # Default credentials. In production, load from secure settings/env vars.
    admin_email = "admin@sms.com"
    admin_password = "SuperAdminSecurePassword123!"

    existing_admin = UserRepository.get_by_email(db, admin_email)
    if not existing_admin:
        logger.info(f"Super admin user not found. Creating new super admin with email: {admin_email}")
        hashed_pw = get_password_hash(admin_password)

        UserRepository.create(
            db=db,
            email=admin_email,
            hashed_password=hashed_pw,
            role=UserRole.SUPER_ADMIN,
            is_first_login=False  # Super admin does not need to change password on first login
        )
        logger.info("Super admin user successfully seeded.")
    else:
        logger.info("Super admin user already exists in the database. Seeding skipped.")
