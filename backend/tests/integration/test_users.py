"""Integration tests for user endpoints"""
import pytest
from fastapi import status
from core.security import hash_password
from tests.fixtures.factories import create_user_model


class TestCreateUser:
    """Test suite for POST /api/v1/users endpoint"""

    def test_create_user_success(self, test_client, test_session):
        """Test creating a user with valid data"""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be in response
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_create_user_duplicate_email(self, test_client, test_session):
        """Test creating a user with an email that already exists"""
        # Create a user first
        existing_user = create_user_model(test_session, email="existing@example.com")

        user_data = {
            "email": "existing@example.com",
            "password": "anotherpassword123"
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    def test_create_user_invalid_email(self, test_client, test_session):
        """Test creating a user with an invalid email format"""
        user_data = {
            "email": "not-an-email",
            "password": "securepassword123"
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_user_password_too_short(self, test_client, test_session):
        """Test creating a user with a password that's too short"""
        user_data = {
            "email": "user@example.com",
            "password": "short"  # Less than 8 characters
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_user_missing_email(self, test_client, test_session):
        """Test creating a user without an email"""
        user_data = {
            "password": "securepassword123"
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_user_missing_password(self, test_client, test_session):
        """Test creating a user without a password"""
        user_data = {
            "email": "user@example.com"
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_create_user_empty_email(self, test_client, test_session):
        """Test creating a user with an empty email"""
        user_data = {
            "email": "",
            "password": "securepassword123"
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_password_exactly_8_chars(self, test_client, test_session):
        """Test creating a user with password exactly 8 characters (minimum)"""
        user_data = {
            "email": "user@example.com",
            "password": "12345678"  # Exactly 8 characters
        }

        response = test_client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]

