"""User routes"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.user import UserCreate, UserResponse
from services.user_service import create_user

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

