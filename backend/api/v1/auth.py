"""Authentication routes"""
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from schemas.auth import LoginRequest, LoginResponse, SendVerificationEmailRequest, VerifyEmailRequest
from schemas.user import UserResponse
from services.auth_service import authenticate_user
from services.user_service import verify_user_email
from services.auth_service import send_verification_email, send_verification_email_by_email
from api.deps import get_current_user, get_verified_user, get_optional_current_user
from core.security import verify_email_verification_token
from models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user with email and password.

    Sets an httpOnly cookie with the JWT token and returns user information.
    The cookie is automatically sent with subsequent requests.

    - **email**: User's email address
    - **password**: User's password
    """
    login_response = authenticate_user(db, login_data)

    # Set httpOnly cookie with token
    # httpOnly prevents JavaScript access (XSS protection)
    # secure=True in production (HTTPS only)
    # samesite="lax" provides CSRF protection
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=login_response.access_token,
        httponly=True,
        secure=settings.is_production,  # HTTPS only in production
        samesite="lax",
        max_age=settings.auth_cookie_max_age,
        path="/"
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


@router.post("/verify-email", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def verify_email(
    verify_data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify a user's email address using a verification token.

    - **token**: Email verification token received via email
    """
    # Verify the token
    payload = verify_email_verification_token(verify_data.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    user_id = int(payload.get("sub"))
    user_email = payload.get("email")

    # Verify the user exists and email matches
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.email != user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token email does not match user email"
        )

    # Check if already verified
    if user.is_email_verified:
        return UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at.isoformat() if user.created_at else "",
            is_email_verified=user.is_email_verified
        )

    # Mark email as verified
    verified_user = verify_user_email(db, user_id)

    return UserResponse(
        id=verified_user.id,
        email=verified_user.email,
        created_at=verified_user.created_at.isoformat() if verified_user.created_at else "",
        is_email_verified=verified_user.is_email_verified
    )


@router.post("/send-verification-email", status_code=status.HTTP_200_OK)
async def send_verification_email_endpoint(
    request: SendVerificationEmailRequest | None = None,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Send email verification email.
    Can be used with authentication (sends to current user) or with email parameter (no auth required).
    """
    if current_user:
        # Authenticated user
        if current_user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        success = send_verification_email(db, current_user.id)
    elif request and request.email:
        # Not authenticated, using email from request body
        success = send_verification_email_by_email(db, request.email)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication required or email must be provided in request body"
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

    return {"message": "Verification email sent successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Logout the current user by clearing the authentication cookie.
    """
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        httponly=True,
        samesite="lax"
    )
    return {"message": "Logged out successfully"}

