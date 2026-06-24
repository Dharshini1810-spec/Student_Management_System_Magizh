from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.response import success_response
from app.core.security import create_access_token, get_password_hash
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.schemas.auth import LoginRequest, ChangePasswordRequest, SignupRequest
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.models.user import User
from app.repositories.user import UserRepository

router = APIRouter()

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    """
    Registration endpoint. Only allows Super Admin to register.
    All other users (Admins, Mentors, Students) are created via user management routes.
    """
    # Check if a user already exists with this email
    existing_user = UserRepository.get_by_email(db, data.email)
    if existing_user:
        raise APIException(
            message="A user with this email already exists.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Super admin registration logic
    hashed_pw = get_password_hash(data.password)
    new_user = UserRepository.create(
        db=db,
        email=data.email,
        hashed_password=hashed_pw,
        role=UserRole.SUPER_ADMIN.value,
        is_first_login=False,  # They set their password during signup, so not first login requirement
        is_approved=True
    )

    user_read = UserRead.model_validate(new_user)
    return success_response(
        data=user_read.model_dump(),
        message="Super Admin registered successfully."
    )

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

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows the logged-in user to change their password.
    """
    AuthService.change_password(
        db=db,
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password
    )
    return success_response(
        message="Password has been changed successfully."
    )
