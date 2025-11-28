"""Authentication service - business logic for authentication"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from schemas.auth import LoginRequest, LoginResponse
from schemas.user import UserResponse
from core.security import verify_password, create_access_token
from services.user_service import get_user_by_email


def authenticate_user(db: Session, login_data: LoginRequest) -> LoginResponse:
    """Authenticate a user and return JWT token"""
    # Find user by email
    user = get_user_by_email(db, login_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at.isoformat() if user.created_at else ""
        )
    )

