"""Unit tests for auth service"""
import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status
from services.auth_service import authenticate_user, send_verification_email
from schemas.auth import LoginRequest
from tests.fixtures.factories import create_user_model
from core.security import hash_password


class TestAuthenticateUser:
    """Test suite for authenticate_user function"""

    def test_authenticate_user_success(self, test_session):
        """Test successful authentication"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        password = "testpassword123"
        hashed = hash_password(password)
        user = create_user_model(test_session, email="test@example.com", hashed_password=hashed)

        login_data = LoginRequest(email="test@example.com", password=password)
        result = authenticate_user(test_session, login_data)

        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.user.email == user.email
        assert result.user.id == user.id

    def test_authenticate_user_wrong_email(self, test_session):
        """Test authentication with wrong email"""
        password = "testpassword123"
        hashed = hash_password(password)
        create_user_model(test_session, email="test@example.com", hashed_password=hashed)

        login_data = LoginRequest(email="wrong@example.com", password=password)

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(test_session, login_data)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_user_wrong_password(self, test_session):
        """Test authentication with wrong password"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        password = "testpassword123"
        hashed = hash_password(password)
        create_user_model(test_session, email="test@example.com", hashed_password=hashed)

        login_data = LoginRequest(email="test@example.com", password="wrongpassword")

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(test_session, login_data)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestSendVerificationEmail:
    """Test suite for send_verification_email function"""

    def test_send_verification_email_success(self, test_session):
        """Test successfully sending verification email"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        with patch('services.auth_service.send_verification_email_core', return_value=True):
            result = send_verification_email(test_session, user.id)
            assert result is True

    def test_send_verification_email_user_not_found(self, test_session):
        """Test sending verification email for non-existent user"""
        result = send_verification_email(test_session, 99999)
        assert result is False

    def test_send_verification_email_already_verified(self, test_session):
        """Test sending verification email when already verified"""
        user = create_user_model(test_session, email="test@example.com", is_email_verified=True)

        result = send_verification_email(test_session, user.id)
        assert result is False

    def test_send_verification_email_failure(self, test_session):
        """Test sending verification email when email service fails"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        with patch('services.auth_service.send_verification_email_core', side_effect=Exception("SMTP error")):
            result = send_verification_email(test_session, user.id)
            assert result is False

