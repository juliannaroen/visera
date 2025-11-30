"""API dependencies"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from core.security import verify_token
from models.user import User

security = HTTPBearer(auto_error=False)


def get_token_from_request(request: Request, credentials: HTTPAuthorizationCredentials | None = None) -> str | None:
    """
    Extract JWT token from request.
    Priority: 1) Cookie, 2) Authorization header (for API clients)
    """
    # Try cookie first (primary method for web app)
    token = request.cookies.get(settings.auth_cookie_name)

    # Fallback to Authorization header (for API clients or backwards compatibility)
    if not token and credentials:
        token = credentials.credentials

    return token


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Reads token from httpOnly cookie (primary) or Authorization header (fallback).
    Can be used in other endpoints that require authentication.
    """
    token = get_token_from_request(request, credentials)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Optional dependency to get the current authenticated user from JWT token.
    Reads token from httpOnly cookie (primary) or Authorization header (fallback).
    Returns None if not authenticated instead of raising an exception.
    """
    token = get_token_from_request(request, credentials)

    if not token:
        return None

    payload = verify_token(token)

    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    return user


def get_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current authenticated user with verified email.
    Requires both authentication and email verification.
    Can be used in endpoints that require verified users.
    """
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required. Please verify your email address.",
        )

    return current_user

