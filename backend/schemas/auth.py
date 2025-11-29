"""Authentication schemas"""
from pydantic import BaseModel, EmailStr, Field
from schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Email verification token")


class SendVerificationEmailRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send verification to")

