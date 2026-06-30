from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
<<<<<<< HEAD
from app.core.response import success_response
from app.core.security import create_access_token, get_password_hash
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.schemas.auth import LoginRequest, ChangePasswordRequest, SignupRequest, ForgotPasswordRequest, ResetPasswordRequest
=======
from app.core.exceptions import APIException
from app.core.permissions import UserRole
from app.core.response import success_response
from app.core.security import create_access_token
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, ChangePasswordRequest
>>>>>>> 9474bc19262d9715051791b4bc94b87a919d16ab
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.models.user import User

router = APIRouter()

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token and user details."""
    user = AuthService.authenticate(
        db,
        email=login_data.email,
        password=login_data.password,
    )
    access_token = create_access_token({"sub": str(user.id)})
    user_read = UserRead.model_validate(user)
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_read.model_dump(),
            "must_change_password": user.is_first_login,
        },
        message="Login successful",
    )

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    """Retrieve current logged-in user info."""
    user_read = UserRead.model_validate(current_user)
    return success_response(
        data=user_read.model_dump(),
        message="User profile retrieved successfully"
    )

<<<<<<< HEAD
@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Changes the password for the currently authenticated user.
    """
=======

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password for current user (first-login or voluntary)."""
>>>>>>> 9474bc19262d9715051791b4bc94b87a919d16ab
    AuthService.change_password(
        db=db,
        user=current_user,
        current_password=data.current_password,
<<<<<<< HEAD
        new_password=data.new_password
    )
    return success_response(
        message="Password has been changed successfully."
    )

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generates a password recovery reset token.
    For easy local testing, the token is returned directly in the response payload.
    """
    reset_token = AuthService.forgot_password(db, email=data.email)
    return success_response(
        data={"reset_token": reset_token},
        message="Password reset instructions generated successfully"
    )

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Resets the password utilizing a valid, non-expired recovery token.
    """
    AuthService.reset_password(
        db, 
        token=data.token, 
        new_password=data.new_password
    )
    return success_response(
        message="Password has been reset successfully"
    )
=======
        new_password=data.new_password,
    )
    return success_response(message="Password changed successfully. Please log in again.")


>>>>>>> 9474bc19262d9715051791b4bc94b87a919d16ab
