"""Authentication service - business logic for authentication"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from schemas.auth import LoginRequest, LoginResponse
from schemas.user import UserResponse
from core.security import verify_password, create_access_token, create_email_verification_token
from core.email import send_verification_email as send_verification_email_core


def authenticate_user(db: Session, login_data: LoginRequest) -> LoginResponse:
    """Authenticate a user and return JWT token"""
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

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
            created_at=user.created_at.isoformat() if user.created_at else "",
            is_email_verified=user.is_email_verified
        )
    )


def send_verification_email(db: Session, user_id: int) -> bool:
    """
    Send email verification email to user.
    Can be used for initial send or resend.
    Part of the authentication/identity verification flow.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    # Don't send if already verified
    if user.is_email_verified:
        return False

    # Generate verification token and send email
    try:
        verification_token = create_email_verification_token(user.id, user.email)
        send_verification_email_core(user.email, verification_token)
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False

