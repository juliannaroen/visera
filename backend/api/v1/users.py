"""User routes"""
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from schemas.user import UserCreate, UserResponse
from services.user_service import create_user, soft_delete_user
from models.user import User
from api.deps import get_verified_user

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user account.

    - **email**: User's email address (must be unique)
    - **password**: User's password (must be at least 8 characters)
    """
    return create_user(db, user_data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    response: Response,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete the current user's account (GDPR compliant).
    The account will be marked as deleted but data will be retained
    for legal / compliance purposes.
    Also clears the authentication cookie to log the user out immediately.
    """
    soft_delete_user(db, current_user.id)

    # Clear the authentication cookie to log the user out immediately
    cookie_settings = settings.get_auth_cookie_settings()
    response.delete_cookie(
        key=settings.auth_cookie_name,
        **cookie_settings
    )

    return None
