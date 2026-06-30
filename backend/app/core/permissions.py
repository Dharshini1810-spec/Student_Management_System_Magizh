from enum import Enum

class Role(str, Enum):
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    MENTOR = 'MENTOR'
    STUDENT = 'STUDENT'

# Alias for backwards compatibility
UserRole = Role

class PermissionName(str, Enum):
    """Enum for all available permissions."""
    USERS_CREATE = 'users:create'
    USERS_UPDATE = 'users:update'
    USERS_DELETE = 'users:delete'
    STUDENTS_VIEW = 'students:view'
    STUDENTS_CREATE = 'students:create'
    STUDENTS_UPDATE = 'students:update'
    ATTENDANCE_MANAGE = 'attendance:manage'
    PROJECTS_ASSIGN = 'projects:assign'
    TODOS_ASSIGN = 'todos:assign'
    DAILY_CONTENT_ASSIGN = 'daily_content:assign'
    REPORTS_VIEW = 'reports:view'

# Permissions mapping (resource:action)
PERMISSIONS = {
    'users:create',
    'users:update',
    'users:delete',
    'students:view',
    'students:create',
    'students:update',
    'attendance:manage',
    'projects:assign',
    'todos:assign',
    'daily_content:assign',
    'reports:view',
}

def has_permission(user_role: Role, permission: str) -> bool:
    if user_role == Role.SUPER_ADMIN:
        return True
    # Simple role-based mapping (extend as needed)
    role_permissions = {
        Role.ADMIN: PERMISSIONS,
        Role.MENTOR: {
            'students:view',
            'students:update',
            'daily_content:assign',
            'reports:view',
        },
        Role.STUDENT: {'students:view', 'reports:view'},
    }
    return permission in role_permissions.get(user_role, set())
