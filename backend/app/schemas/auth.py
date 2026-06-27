from pydantic import BaseModel
from typing import Optional
from ..schemas.user import UserRead

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    referral_code: Optional[str] = None
    name: Optional[str] = None
