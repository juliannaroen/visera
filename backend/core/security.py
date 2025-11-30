"""Security utilities for authentication and authorization"""
import bcrypt
import jwt
import secrets
import string
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


def generate_otp_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric OTP code.

    Args:
        length: Length of the OTP code (default: 6)

    Returns:
        Random alphanumeric string (uppercase letters and digits)
    """
    # Use uppercase letters and digits for better readability
    alphabet = string.ascii_uppercase + string.digits
    # Exclude similar-looking characters: 0, O, I, 1
    alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_otp_code(code: str) -> str:
    """
    Hash an OTP code using bcrypt.

    Args:
        code: Plain text OTP code

    Returns:
        Hashed OTP code
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(code.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_otp_code(plain_code: str, hashed_code: str) -> bool:
    """
    Verify an OTP code against its hash.

    Args:
        plain_code: Plain text OTP code to verify
        hashed_code: Hashed OTP code to verify against

    Returns:
        True if code matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_code.encode('utf-8'),
            hashed_code.encode('utf-8')
        )
    except Exception:
        return False

