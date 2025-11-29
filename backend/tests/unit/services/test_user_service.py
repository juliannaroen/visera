"""Unit tests for user service"""
import pytest
from fastapi import HTTPException, status
from services.user_service import create_user, get_user_by_id, get_user_by_email, verify_user_email
from schemas.user import UserCreate
from tests.fixtures.factories import create_user_model


class TestGetUserById:
    """Test suite for get_user_by_id function"""

    def test_get_user_by_id_success(self, test_session):
        """Test getting user by ID successfully"""
        user = create_user_model(test_session, email="test@example.com")
        result = get_user_by_id(test_session, user.id)

        assert result.id == user.id
        assert result.email == user.email

    def test_get_user_by_id_not_found(self, test_session):
        """Test getting user by ID when user doesn't exist"""
        with pytest.raises(HTTPException) as exc_info:
            get_user_by_id(test_session, 99999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()


class TestGetUserByEmail:
    """Test suite for get_user_by_email function"""

    def test_get_user_by_email_success(self, test_session):
        """Test getting user by email successfully"""
        user = create_user_model(test_session, email="test@example.com")
        result = get_user_by_email(test_session, "test@example.com")

        assert result is not None
        assert result.id == user.id
        assert result.email == user.email

    def test_get_user_by_email_not_found(self, test_session):
        """Test getting user by email when user doesn't exist"""
        result = get_user_by_email(test_session, "nonexistent@example.com")
        assert result is None


class TestVerifyUserEmail:
    """Test suite for verify_user_email function"""

    def test_verify_user_email_success(self, test_session):
        """Test successfully verifying user email"""
        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)
        assert user.is_email_verified is False

        result = verify_user_email(test_session, user.id)

        assert result.is_email_verified is True
        assert result.id == user.id

        # Verify in database
        test_session.refresh(user)
        assert user.is_email_verified is True

    def test_verify_user_email_user_not_found(self, test_session):
        """Test verifying email for non-existent user"""
        with pytest.raises(HTTPException) as exc_info:
            verify_user_email(test_session, 99999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestCreateUser:
    """Test suite for create_user function"""

    def test_create_user_email_already_exists(self, test_session):
        """Test creating user when email already exists"""
        existing_user = create_user_model(test_session, email="existing@example.com")

        user_data = UserCreate(email="existing@example.com", password="password123")

        with pytest.raises(HTTPException) as exc_info:
            create_user(test_session, user_data)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in exc_info.value.detail.lower()

