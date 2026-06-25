from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError

# Monkey-patch bcrypt to resolve passlib wrap bug compatibility with bcrypt 4.0+/5.0.0
import bcrypt
_original_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)
bcrypt.hashpw = _patched_hashpw

from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """
    Creates a JWT access token containing the subject.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its hashed value.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a password hash.
    """
    return pwd_context.hash(password)

def decode_token(token: str) -> Union[dict, None]:
    """
    Decodes and validates a JWT token. Returns the payload or None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
