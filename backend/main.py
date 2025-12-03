"""Main FastAPI application"""
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.config import get_cors_config, settings
from core.database import get_db
from api.v1 import auth, users
from fastapi import status

app = FastAPI(title="Visera API", version="1.0.0")

# Configure CORS
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Exception handler to clear session cookie on 401
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    """Clear auth cookie on 401 Unauthorized responses"""
    response = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail},
    )
    # Clear the cookie with same settings used when setting it
    cookie_settings = settings.get_auth_cookie_settings()
    response.delete_cookie(
        key=settings.auth_cookie_name,
        **cookie_settings
    )
    return response

# Include routers with API versioning
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "Visera API is running"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Simple health check that also verifies database connection"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
