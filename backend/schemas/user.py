"""User schemas"""
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str
    is_email_verified: bool = False

    class Config:
        from_attributes = True

