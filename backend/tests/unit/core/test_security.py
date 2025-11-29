"""Unit tests for core security"""
import pytest
import os
import jwt
from datetime import datetime, timedelta
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    create_email_verification_token,
    verify_email_verification_token
)


class TestHashPassword:
    """Test suite for hash_password function"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)

    def test_hash_password_different_salts(self):
        """Test that same password produces different hashes (different salts)"""
        password = "testpassword123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        assert hashed1 != hashed2  # Different salts should produce different hashes


class TestVerifyPassword:
    """Test suite for verify_password function"""

    def test_verify_password_success(self):
        """Test successful password verification"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test failed password verification"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestCreateAccessToken:
    """Test suite for create_access_token function"""

    def test_create_access_token_success(self):
        """Test creating access token successfully"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_create_access_token_with_expires_delta(self):
        """Test creating access token with custom expiry"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        data = {"sub": "123"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta=expires_delta)

        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload["exp"])
        iat = datetime.fromtimestamp(payload["iat"])

        # Expiry should be approximately 1 hour from issued time
        assert (exp - iat).total_seconds() == pytest.approx(3600, abs=60)

    def test_create_access_token_no_secret_key(self):
        """Test creating access token without SECRET_KEY"""
        # SECRET_KEY is set at module import time, so we need to mock it
        from unittest.mock import patch
        from core import security

        original_secret = security.SECRET_KEY
        try:
            with patch.object(security, 'SECRET_KEY', None):
                data = {"sub": "123"}

                with pytest.raises(ValueError) as exc_info:
                    create_access_token(data)

                assert "JWT_SECRET_KEY" in str(exc_info.value)
        finally:
            security.SECRET_KEY = original_secret


class TestVerifyToken:
    """Test suite for verify_token function"""

    def test_verify_token_success(self):
        """Test verifying valid token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_verify_token_expired(self):
        """Test verifying expired token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an expired token
        expire = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": "123",
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        expired_token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        result = verify_token(expired_token)

        assert result is None

    def test_verify_token_invalid(self):
        """Test verifying invalid token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        result = verify_token("invalid-token")

        assert result is None

    def test_verify_token_no_secret_key(self):
        """Test verifying token without SECRET_KEY"""
        original_value = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ.pop("JWT_SECRET_KEY", None)

            result = verify_token("some-token")

            assert result is None
        finally:
            if original_value:
                os.environ["JWT_SECRET_KEY"] = original_value


class TestCreateEmailVerificationToken:
    """Test suite for create_email_verification_token function"""

    def test_create_email_verification_token_success(self):
        """Test creating email verification token successfully"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        token = create_email_verification_token(123, "test@example.com")

        assert token is not None
        assert isinstance(token, str)

        # Verify token can be decoded
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "email_verification"

    def test_create_email_verification_token_no_secret_key(self):
        """Test creating email verification token without SECRET_KEY"""
        # SECRET_KEY is set at module import time, so we need to mock it
        from unittest.mock import patch
        from core import security

        original_secret = security.SECRET_KEY
        try:
            with patch.object(security, 'SECRET_KEY', None):
                with pytest.raises(ValueError) as exc_info:
                    create_email_verification_token(123, "test@example.com")

                assert "JWT_SECRET_KEY" in str(exc_info.value)
        finally:
            security.SECRET_KEY = original_secret


class TestVerifyEmailVerificationToken:
    """Test suite for verify_email_verification_token function"""

    def test_verify_email_verification_token_success(self):
        """Test verifying valid email verification token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        token = create_email_verification_token(123, "test@example.com")

        payload = verify_email_verification_token(token)

        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "email_verification"

    def test_verify_email_verification_token_wrong_type(self):
        """Test verifying token with wrong type"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an access token (wrong type)
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = verify_email_verification_token(token)

        assert payload is None

    def test_verify_email_verification_token_expired(self):
        """Test verifying expired email verification token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an expired token
        expire = datetime.utcnow() - timedelta(hours=25)
        payload = {
            "sub": "123",
            "email": "test@example.com",
            "type": "email_verification",
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(hours=26)
        }
        expired_token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        result = verify_email_verification_token(expired_token)

        assert result is None

    def test_verify_email_verification_token_invalid(self):
        """Test verifying invalid email verification token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        result = verify_email_verification_token("invalid-token")

        assert result is None

    def test_verify_email_verification_token_no_secret_key(self):
        """Test verifying email verification token without SECRET_KEY"""
        original_value = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ.pop("JWT_SECRET_KEY", None)

            result = verify_email_verification_token("some-token")

            assert result is None
        finally:
            if original_value:
                os.environ["JWT_SECRET_KEY"] = original_value

