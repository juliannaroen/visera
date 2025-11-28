from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from auth import hash_password, verify_password, create_access_token, verify_token

app = FastAPI(title="Visera API", version="1.0.0")

# Configure CORS to allow Next.js frontend
# Get allowed origins from environment variable, default to localhost for development
vercel_prod_url = os.getenv("VERCEL_PROD_URL", "")
allowed_origins = []

# Add production URL if provided
if vercel_prod_url:
    allowed_origins.extend([origin.strip() for origin in vercel_prod_url.split(",")])

# Always allow localhost for development
allowed_origins.append("http://localhost:3000")

# Remove duplicates and empty strings
allowed_origins = list(set([origin for origin in allowed_origins if origin]))

# Use regex to allow all Vercel preview deployments (*.vercel.app)
# This handles preview deployments that have different subdomains
allow_origin_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme for JWT
security = HTTPBearer()


@app.get("/")
async def root():
    return {"message": "Visera API is running"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    # Simple health check that also verifies database connection
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: User's email address (must be unique)
    - **password**: User's password (must be at least 8 characters)
    """
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


@app.post("/auth/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user with email and password.

    Returns a JWT access token that can be used for authenticated requests.

    - **email**: User's email address
    - **password**: User's password
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

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
            created_at=user.created_at.isoformat() if user.created_at else ""
        )
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Can be used in other endpoints that require authentication.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.get("/auth/me", response_model=UserResponse)
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

