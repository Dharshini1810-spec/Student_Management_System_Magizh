import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.user import UserRepository
from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import AuthenticationException, APIException

class AuthService:
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User:
        """
        Authenticates a user by email and password.
        Raises AuthenticationException on failure.
        """
        user = UserRepository.get_by_email(db, email)
        if not user:
            raise AuthenticationException(
                message="Incorrect email or password",
                code="INVALID_CREDENTIALS"
            )
        
        if not user.is_active:
            raise AuthenticationException(
                message="User account is deactivated",
                code="INACTIVE_ACCOUNT"
            )
            
        if not user.is_approved:
            raise AuthenticationException(
                message="Your account is pending approval by the Super Admin.",
                code="PENDING_APPROVAL"
            )

        if not verify_password(password, user.hashed_password):
            raise AuthenticationException(
                message="Incorrect email or password",
                code="INVALID_CREDENTIALS"
            )
            
        return user

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
        """
        Validates current password and updates it to the new password.
        Also clears is_first_login flag.
        """
        if not verify_password(current_password, user.hashed_password):
            raise APIException(
                message="Incorrect current password",
                code="INCORRECT_CURRENT_PASSWORD",
                status_code=400
            )

        hashed = get_password_hash(new_password)
        UserRepository.update(db, user, {
            "hashed_password": hashed,
            "is_first_login": False
        })
        return user
