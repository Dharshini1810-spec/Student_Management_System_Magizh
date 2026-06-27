from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.exceptions import APIException
from app.core.permissions import UserRole
from app.core.response import success_response
from app.core.security import create_access_token, get_password_hash
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, SignupRequest, ChangePasswordRequest
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.models.user import User
from app.services.referral_link import ReferralLinkService
from app.models.student import MentorStudent

router = APIRouter()

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    """
    Registration endpoint.
    - Without referral_code: creates a Super Admin account.
    - With referral_code: creates a Student account linked to the referrer.
    """
    existing_user = UserRepository.get_by_email(db, data.email)
    if existing_user:
        raise APIException(
            message="A user with this email already exists.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    hashed_pw = get_password_hash(data.password)

    if data.referral_code:
        link = ReferralLinkService.validate_code(db, data.referral_code)
        if not link:
            raise APIException(
                message="Invalid or expired referral code.",
                code="INVALID_REFERRAL_CODE",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        referrer = UserRepository.get_by_id(db, link.user_id)
        if not referrer:
            raise APIException(
                message="Referrer account not found.",
                code="REFERRER_NOT_FOUND",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        student_user = UserRepository.create(
            db=db,
            email=data.email,
            hashed_password=hashed_pw,
            name=data.name or data.email.split("@")[0],
            role=UserRole.STUDENT.value,
            is_first_login=False,
            is_approved=True
        )
        if referrer.role == UserRole.MENTOR.value or referrer.role == UserRole.SUPER_ADMIN.value:
            from app.repositories.student import StudentRepository
            student = StudentRepository.create_profile(db, student_id=student_user.id)
            mentor_student = MentorStudent(mentor_id=referrer.id, student_id=student.id)
            db.add(mentor_student)
            db.commit()

        from app.repositories.referral_link import ReferralLinkRepository
        ReferralLinkRepository.increment_uses(db, link)

        user_read = UserRead.model_validate(student_user)
        return success_response(
            data=user_read.model_dump(),
            message="Student registered via referral link successfully."
        )

    hashed_pw = get_password_hash(data.password)
    new_user = UserRepository.create(
        db=db,
        email=data.email,
        hashed_password=hashed_pw,
        role=UserRole.SUPER_ADMIN.value,
        is_first_login=False,
        is_approved=True
    )

    user_read = UserRead.model_validate(new_user)
    return success_response(
        data=user_read.model_dump(),
        message="Super Admin registered successfully."
    )

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
