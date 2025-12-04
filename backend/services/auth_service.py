"""Authentication service - business logic for authentication"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
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
            detail="We could not find an account with this email"
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect"
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
    db.query(OtpCode).filter(
        OtpCode.user_id == user_id,
        OtpCode.type == OtpType.EMAIL_VERIFICATION
    ).delete()
    db.commit()

    # Create new OTP code record
    otp_record = OtpCode(
        user_id=user_id,
        type=OtpType.EMAIL_VERIFICATION,
        hashed_code=hashed_code,
        expires_at=expires_at
    )
    db.add(otp_record)
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
    otp_record = db.query(OtpCode).filter(
        OtpCode.user_id == user.id,
        OtpCode.type == OtpType.EMAIL_VERIFICATION
    ).order_by(desc(OtpCode.created_at)).first()

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new code."
        )

    # Check if code has expired (use timezone-aware datetime)
    now_utc = datetime.now(timezone.utc)
    expires_at_utc = otp_record.expires_at
    if expires_at_utc.tzinfo is None:
        # If database returned naive datetime, assume it's UTC
        expires_at_utc = expires_at_utc.replace(tzinfo=timezone.utc)
    elif expires_at_utc.tzinfo != timezone.utc:
        # Convert to UTC if in different timezone
        expires_at_utc = expires_at_utc.astimezone(timezone.utc)

    if now_utc > expires_at_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )

    # Verify the code hash
    if not verify_otp_hash(code, otp_record.hashed_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code."
        )

    # Code is valid - verify user's email
    verified_user = verify_user_email(db, user.id)

    # Delete the used OTP code
    db.delete(otp_record)
    db.commit()

    return verified_user

