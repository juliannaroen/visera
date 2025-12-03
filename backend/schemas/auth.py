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


class VerifyOtpRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    code: str = Field(..., description="6-character OTP verification code", min_length=6, max_length=6)


class SendOtpEmailRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send OTP to")

