"""User model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func, text
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_email_verified = Column(Boolean, nullable=False, server_default=text('false'))
    deleted_at = Column(DateTime(timezone=True), nullable=True)

