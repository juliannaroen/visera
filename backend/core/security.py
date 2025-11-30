"""Security utilities for authentication and authorization"""
import bcrypt
import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Optional
from core.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if not settings.jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY environment variable must be set")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    if not settings.jwt_secret_key:
        return None

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except ExpiredSignatureError:
        return None
    except PyJWTError:
        return None


def create_email_verification_token(user_id: int, user_email: str) -> str:
    """Create a JWT token for email verification (expires in 24 hours)"""
    if not settings.jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY environment variable must be set")

    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "sub": str(user_id),
        "email": user_email,
        "type": "email_verification",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[dict]:
    """Verify and decode an email verification token"""
    if not settings.jwt_secret_key:
        return None

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        # Verify this is an email verification token
        if payload.get("type") != "email_verification":
            return None
        return payload
    except ExpiredSignatureError:
        return None
    except PyJWTError:
        return None

