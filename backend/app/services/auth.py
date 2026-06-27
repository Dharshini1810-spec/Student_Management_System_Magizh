from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from ..repositories.user import UserRepository
from ..models.user import User
from ..core.security import verify_password, get_password_hash, generate_reset_token
from ..core.exceptions import AuthenticationException, APIException, NotFoundException

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
            "is_first_login": False,
        })

    @staticmethod
    def forgot_password(db: Session, email: str) -> str:
        user = UserRepository.get_by_email(db, email)
        if not user:
            raise NotFoundException(message="No account found with this email.")
        token = generate_reset_token()
        user.reset_token = token
        user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
        db.commit()
        return token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> None:
        user = UserRepository.get_by_reset_token(db, token)
        if not user or not user.reset_token_expiry:
            raise APIException(message="Invalid or expired reset token.", code="INVALID_TOKEN", status_code=400)
        if user.reset_token_expiry < datetime.now(timezone.utc):
            raise APIException(message="Reset token has expired.", code="TOKEN_EXPIRED", status_code=400)
        hashed = get_password_hash(new_password)
        UserRepository.update(db, user, {
            "hashed_password": hashed,
            "reset_token": None,
            "reset_token_expiry": None,
            "is_first_login": False,
        })

