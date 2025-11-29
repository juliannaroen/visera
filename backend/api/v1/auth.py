"""Authentication routes"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import LoginRequest, LoginResponse, VerifyEmailRequest
from schemas.user import UserResponse
from services.auth_service import authenticate_user
from services.user_service import verify_user_email
from services.auth_service import send_verification_email
from api.deps import get_current_user
from core.security import verify_email_verification_token
from models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user with email and password.

    Returns a JWT access token that can be used for authenticated requests.

    - **email**: User's email address
    - **password**: User's password
    """
    return authenticate_user(db, login_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's information.
    Requires a valid JWT token in the Authorization header.
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send email verification email to the current authenticated user.
    Can be used for initial send or resend.
    Requires a valid JWT token in the Authorization header.
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    success = send_verification_email(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

    return {"message": "Verification email sent successfully"}

