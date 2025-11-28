"""User service - business logic for user operations"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserCreate, UserResponse
from core.security import hash_password


def create_user(db: Session, user_data: UserCreate) -> UserResponse:
    """Create a new user account"""
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at.isoformat() if new_user.created_at else ""
    )


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get a user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

