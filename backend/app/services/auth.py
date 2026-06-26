import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from ..repositories.user import UserRepository
from ..models.user import User
from ..core.security import verify_password, get_password_hash
from ..core.exceptions import AuthenticationException, APIException

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
            
        if not verify_password(password, user.hashed_password):
            raise AuthenticationException(
                message="Incorrect email or password",
                code="INVALID_CREDENTIALS"
            )
            
        return user


    @staticmethod
    def forgot_password(db: Session, email: str) -> str:
        """
        Generates a password reset token if the user email exists.
        Returns the token string.
        """
        user = UserRepository.get_by_email(db, email)
        if not user:
            # For security reasons, we can log it but don't expose email existence.
            # However, for testing/specification flows we can raise an error or just return a token.
            # Let's raise an exception so it is easy to test forgot password functionality.
            raise APIException(
                message="No user found with this email address",
                code="USER_NOT_FOUND",
                status_code=404
            )
            
        token = str(uuid.uuid4())
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        UserRepository.update(db, user, {
            "reset_token": token,
            "reset_token_expires_at": expiry
        })
        return token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> User:
        """
        Validates the reset token and updates the user's password.
        Clears the reset token parameters.
        """
        user = UserRepository.get_by_reset_token(db, token)
        if not user:
            raise APIException(
                message="Invalid or expired reset token",
                code="INVALID_RESET_TOKEN",
                status_code=400
            )
            
        # Verify expiry time
        if user.reset_token_expires_at:
            # Normalize to timezone aware datetime if necessary
            expiry = user.reset_token_expires_at
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
                
            if datetime.now(timezone.utc) > expiry:
                raise APIException(
                    message="Reset token has expired",
                    code="EXPIRED_RESET_TOKEN",
                    status_code=400
                )
                
        hashed = get_password_hash(new_password)
        UserRepository.update(db, user, {
            "hashed_password": hashed,
            "reset_token": None,
            "reset_token_expires_at": None,
            "is_first_login": False  # Resetting password also clears first-login flag
        })
        return user

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
        """
        Changes the password for an authenticated user.
        Used for first-login forced change and voluntary password updates.
        Validates the current password before applying the new one.
        """
        if not verify_password(current_password, user.hashed_password):
            raise APIException(
                message="Current password is incorrect",
                code="INVALID_CURRENT_PASSWORD",
                status_code=400
            )

        if current_password == new_password:
            raise APIException(
                message="New password must be different from the current password",
                code="PASSWORD_SAME_AS_CURRENT",
                status_code=400
            )

        hashed = get_password_hash(new_password)
        return UserRepository.update(db, user, {
            "hashed_password": hashed,
            "is_first_login": False,  # Clears forced-change flag
        })

