"""Authentication routes"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import LoginRequest, LoginResponse
from schemas.user import UserResponse
from services.auth_service import authenticate_user
from api.deps import get_current_user
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
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )

