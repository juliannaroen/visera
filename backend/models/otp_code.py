"""OTP Code model for storing one-time passwords"""
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class OtpType(str, enum.Enum):
    """OTP code types"""
    EMAIL_VERIFICATION = "email_verification"


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Use native_enum=False to support SQLite (uses String) and PostgreSQL (uses enum)
    type = Column(Enum(OtpType, native_enum=False), nullable=False, index=True)
    hashed_code = Column(String, nullable=False)  # Hashed OTP code
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to user
    user = relationship("User", backref="otp_codes")

    # Composite index for efficient latest code lookup
    __table_args__ = (
        Index("idx_otp_user_type_created", "user_id", "type", "created_at"),
    )

