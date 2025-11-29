"""User service - business logic for user operations"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserCreate, UserResponse
from core.security import hash_password
from services.auth_service import send_verification_email


def create_user(db: Session, user_data: UserCreate) -> UserResponse:
    """Create a new user account"""
    # Check if user with this email already exists
    existing_user = get_user_by_email(db, user_data.email)
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

    # Send verification email
    try:
        send_verification_email(db, new_user.id)
    except Exception as e:
        # Log error but don't fail user creation
        # In production, you might want to log this to a monitoring service
        print(f"Failed to send verification email: {e}")

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at.isoformat() if new_user.created_at else "",
        is_email_verified=new_user.is_email_verified
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


def verify_user_email(db: Session, user_id: int) -> User:
    """Mark a user's email as verified"""
    user = get_user_by_id(db, user_id)
    user.is_email_verified = True
    db.commit()
    db.refresh(user)
    return user

