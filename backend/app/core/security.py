import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
<<<<<<< HEAD
import bcrypt
=======

# Monkey-patch bcrypt to resolve passlib wrap bug compatibility with bcrypt 4.0+/5.0.0
import bcrypt
_original_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)
bcrypt.hashpw = _patched_hashpw

from passlib.context import CryptContext
>>>>>>> 9474bc19262d9715051791b4bc94b87a919d16ab
from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def decode_token(token: str):
    """Alias for decode_access_token for backwards compatibility."""
    return decode_access_token(token)

def generate_reset_token(length: int = 48) -> str:
    """Generate a cryptographically secure random token for password reset."""
    return secrets.token_urlsafe(length)
