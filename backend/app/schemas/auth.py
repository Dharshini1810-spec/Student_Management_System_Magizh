from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserRead

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

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
