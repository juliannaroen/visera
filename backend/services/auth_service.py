"""Authentication service - business logic for authentication"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from models.user import User
from models.otp_code import OtpCode, OtpType
from schemas.auth import LoginRequest, LoginResponse
from schemas.user import UserResponse
from core.security import (
    verify_password,
    create_access_token,
    generate_otp_code,
    hash_otp_code,
    verify_otp_code as verify_otp_hash
)
from core.email import send_verification_email as send_verification_email_core
from services.user_service import get_user_by_email, verify_user_email


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
            created_at=user.created_at.isoformat() if user.created_at else "",
            is_email_verified=user.is_email_verified
        )
    )


def send_verification_email(db: Session, user_id: int) -> bool:
    """
    Send email verification OTP to user by ID.
    Can be used for initial send or resend.
    Part of the authentication/identity verification flow.
    Generates a new 6-character OTP code, invalidates any existing OTPs for this user.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    # Don't send if already verified
    if user.is_email_verified:
        return False

    # Generate 6-character OTP code
    otp_code = generate_otp_code(length=6)
    hashed_code = hash_otp_code(otp_code)

    # Set expiration to 15 minutes from now (use timezone-aware datetime)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Invalidate any existing OTPs for this user and type by deleting them
    # (We only keep the latest one)
    # Use text() to bypass SQLAlchemy's enum conversion which uses enum name instead of value
    db.execute(
        text("DELETE FROM otp_codes WHERE user_id = :user_id AND type = :otp_type"),
        {"user_id": user_id, "otp_type": "email_verification"}
    )
    db.commit()

    # Create new OTP code record
    # Use raw SQL to insert with enum value directly to avoid SQLAlchemy enum conversion
    db.execute(
        text("""
            INSERT INTO otp_codes (user_id, type, hashed_code, expires_at)
            VALUES (:user_id, :otp_type, :hashed_code, :expires_at)
        """),
        {
            "user_id": user_id,
            "otp_type": "email_verification",
            "hashed_code": hashed_code,
            "expires_at": expires_at
        }
    )
    db.commit()

    # Send OTP code via email
    try:
        send_verification_email_core(user.email, otp_code)
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False


def send_verification_email_by_email(db: Session, email: str) -> bool:
    """
    Send email verification OTP to user by email address.
    Used when user is not authenticated.
    Generates a new 6-character OTP code, invalidates any existing OTPs for this user.
    """
    user = get_user_by_email(db, email)

    if not user:
        return False  # Don't reveal if user exists or not

    # Don't send if already verified
    if user.is_email_verified:
        return False

    # Use the same logic as send_verification_email
    return send_verification_email(db, user.id)


def verify_otp_code(db: Session, email: str, code: str) -> User:
    """
    Verify an OTP code for email verification.

    Args:
        db: Database session
        email: User's email address
        code: 6-character OTP code to verify

    Returns:
        Verified User object

    Raises:
        HTTPException if code is invalid, expired, or user not found
    """
    # Find user by email
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get the latest OTP code for this user and type
    # Use text() with explicit column casting to avoid SQLAlchemy enum conversion
    result = db.execute(
        text("""
            SELECT
                id,
                user_id,
                type::text as type,
                hashed_code,
                expires_at,
                created_at
            FROM otp_codes
            WHERE user_id = :user_id AND type = :otp_type
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"user_id": user.id, "otp_type": "email_verification"}
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new code."
        )

    # Check if code has expired
    # Use database's NOW() for accurate comparison to avoid timezone issues
    result_check = db.execute(
        text("SELECT expires_at > NOW() as is_valid FROM otp_codes WHERE id = :otp_id"),
        {"otp_id": row.id}
    )
    is_valid = result_check.scalar()
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )

    # Verify the code hash
    if not verify_otp_hash(code, row.hashed_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code."
        )

    # Code is valid - verify user's email
    verified_user = verify_user_email(db, user.id)

    # Delete the used OTP code using raw SQL to avoid enum conversion
    db.execute(
        text("DELETE FROM otp_codes WHERE id = :otp_id"),
        {"otp_id": row.id}
    )
    db.commit()

    return verified_user

