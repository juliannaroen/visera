"""OTP Code model for storing one-time passwords"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


# OTP type constants (for validation, not database enum)
class OtpType:
    """OTP code type constants"""
    EMAIL_VERIFICATION = "email_verification"


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # OTP type (e.g., "email_verification")
    hashed_code = Column(String, nullable=False)  # Hashed OTP code
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to user
    user = relationship("User", backref="otp_codes")

    # Composite index for efficient latest code lookup
    __table_args__ = (
        Index("idx_otp_user_type_created", "user_id", "type", "created_at"),
    )

