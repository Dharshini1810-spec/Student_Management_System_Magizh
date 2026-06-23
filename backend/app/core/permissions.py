from enum import Enum
from typing import List
from fastapi import HTTPException, status

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"

class PermissionChecker:
    """
    Dependency helper to check if the current user has the required roles.
    This is JWT-ready and roles-based.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_role: str) -> bool:
        if user_role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return True
