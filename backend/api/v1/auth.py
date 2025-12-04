"""Authentication routes"""
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from models.user import User
from schemas.auth import LoginRequest, LoginResponse, SendOtpEmailRequest, VerifyOtpRequest
from schemas.user import UserResponse
from services.auth_service import (
    authenticate_user,
    send_verification_email,
    send_verification_email_by_email,
    verify_otp_code
)
from core.security import create_access_token
from api.deps import get_verified_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user with email and password.

    If user is unverified, sends a new OTP email and returns user info without creating session.
    If user is verified, sets an httpOnly cookie with the JWT token and returns user information.

    - **email**: User's email address
    - **password**: User's password
    """
    login_response = authenticate_user(db, login_data)

    # If user is not verified, send OTP email and return without creating session
    if not login_response.user.is_email_verified:
        # Send new OTP email
        send_verification_email(db, login_response.user.id)
        # Return response without setting cookie (user needs to verify OTP first)
        return login_response

    # User is verified - set httpOnly cookie with token
    cookie_settings = settings.get_auth_cookie_settings()
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=login_response.access_token,
        max_age=settings.auth_cookie_max_age,
        **cookie_settings
    )

    return login_response


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_verified_user)):
    """
    Get the current authenticated user's information.
    Requires a valid JWT token in the Authorization header and verified email.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        is_email_verified=current_user.is_email_verified
    )


@router.post("/verify-otp", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def verify_otp(
    verify_data: VerifyOtpRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify a user's email address using an OTP code.
    After successful verification, creates a session (sets cookie) and returns user info.

    - **email**: User's email address
    - **code**: 6-character OTP code received via email
    """
    # Verify OTP code and mark email as verified
    verified_user = verify_otp_code(db, verify_data.email, verify_data.code)

    # Create access token and session
    access_token = create_access_token(data={"sub": str(verified_user.id), "email": verified_user.email})

    # Set httpOnly cookie with token
    cookie_settings = settings.get_auth_cookie_settings()
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=access_token,
        max_age=settings.auth_cookie_max_age,
        **cookie_settings
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=verified_user.id,
            email=verified_user.email,
            created_at=verified_user.created_at.isoformat() if verified_user.created_at else "",
            is_email_verified=verified_user.is_email_verified
        )
    )


@router.post("/send-otp-email", status_code=status.HTTP_200_OK)
async def send_otp_email_endpoint(
    request: SendOtpEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP email for email verification.
    Requires email in request body.
    """
    from services.user_service import get_user_by_email

    # Check if user exists and is already verified
    user = get_user_by_email(db, request.email)
    if user and user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    success = send_verification_email_by_email(db, request.email)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email"
        )

    return {"message": "OTP email sent successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Logout the current user by clearing the authentication cookie.
    """
    cookie_settings = settings.get_auth_cookie_settings()
    response.delete_cookie(
        key=settings.auth_cookie_name,
        **cookie_settings
    )
    return {"message": "Logged out successfully"}

