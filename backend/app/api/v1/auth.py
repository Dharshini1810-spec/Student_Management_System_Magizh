from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.exceptions import APIException
from app.core.permissions import UserRole
from app.core.response import success_response
from app.core.security import create_access_token
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, ChangePasswordRequest
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


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password for current user (first-login or voluntary)."""
    AuthService.change_password(
        db=db,
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return success_response(message="Password changed successfully. Please log in again.")


