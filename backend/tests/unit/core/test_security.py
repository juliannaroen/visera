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
    generate_otp_code,
    hash_otp_code,
    verify_otp_code
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
        """Test creating access token without JWT_SECRET_KEY"""
        from unittest.mock import patch
        from core import config

        original_secret = config.settings.jwt_secret_key
        try:
            # Temporarily set jwt_secret_key to None
            config.settings.jwt_secret_key = None
            data = {"sub": "123"}

            with pytest.raises(ValueError) as exc_info:
                create_access_token(data)

            assert "JWT_SECRET_KEY" in str(exc_info.value)
        finally:
            config.settings.jwt_secret_key = original_secret


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


class TestGenerateOtpCode:
    """Test suite for generate_otp_code function"""

    def test_generate_otp_code_default_length(self):
        """Test generating OTP code with default length"""
        code = generate_otp_code()
        assert len(code) == 6
        assert code.isalnum()
        assert code.isupper()

    def test_generate_otp_code_custom_length(self):
        """Test generating OTP code with custom length"""
        code = generate_otp_code(length=8)
        assert len(code) == 8
        assert code.isalnum()
        assert code.isupper()

    def test_generate_otp_code_excludes_similar_chars(self):
        """Test that OTP code excludes similar-looking characters"""
        # Generate multiple codes to ensure excluded chars don't appear
        codes = [generate_otp_code() for _ in range(100)]
        all_chars = ''.join(codes)
        assert '0' not in all_chars
        assert 'O' not in all_chars
        assert 'I' not in all_chars
        assert '1' not in all_chars


class TestHashOtpCode:
    """Test suite for hash_otp_code function"""

    def test_hash_otp_code(self):
        """Test OTP code hashing"""
        code = "ABC123"
        hashed = hash_otp_code(code)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != code  # Should be different from original
        assert hashed.startswith("$2b$")  # bcrypt hash format

    def test_hash_otp_code_different_codes_different_hashes(self):
        """Test that different codes produce different hashes"""
        code1 = "ABC123"
        code2 = "XYZ789"

        hashed1 = hash_otp_code(code1)
        hashed2 = hash_otp_code(code2)

        assert hashed1 != hashed2


class TestVerifyOtpCode:
    """Test suite for verify_otp_code function"""

    def test_verify_otp_code_success(self):
        """Test verifying valid OTP code"""
        code = "ABC123"
        hashed = hash_otp_code(code)

        result = verify_otp_code(code, hashed)

        assert result is True

    def test_verify_otp_code_wrong_code(self):
        """Test verifying wrong OTP code"""
        code = "ABC123"
        wrong_code = "XYZ789"
        hashed = hash_otp_code(code)

        result = verify_otp_code(wrong_code, hashed)

        assert result is False

    def test_verify_otp_code_invalid_hash(self):
        """Test verifying with invalid hash"""
        code = "ABC123"
        invalid_hash = "invalid-hash"

        result = verify_otp_code(code, invalid_hash)

        assert result is False

