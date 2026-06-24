from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.response import success_response
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.models.user import User

router = APIRouter()

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token and user role details.
    """
    user = AuthService.authenticate(
        db, 
        email=login_data.email, 
        password=login_data.password
    )
    
    # Create the access token using the user's UUID
    access_token = create_access_token(subject=user.id)
    user_read = UserRead.model_validate(user)
    
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_read.model_dump()
        },
        message="Login successful"
    )

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Retrieves information about the currently logged-in user.
    """
    user_read = UserRead.model_validate(current_user)
    return success_response(
        data=user_read.model_dump(),
        message="User profile retrieved successfully"
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
