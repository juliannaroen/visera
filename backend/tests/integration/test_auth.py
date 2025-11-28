"""Integration tests for authentication endpoints"""
import pytest
import os
import jwt
from datetime import datetime, timedelta
from fastapi import status
from core.security import hash_password, create_access_token
from tests.fixtures.factories import create_user_model


class TestLogin:
    """Test suite for POST /api/v1/auth/login endpoint"""

    def test_login_success(self, test_client, test_session):
        """Test successful login with correct credentials"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a user with a known password
        password = "testpassword123"
        hashed = hash_password(password)
        user = create_user_model(test_session, email="test@example.com", hashed_password=hashed)

        login_data = {
            "email": "test@example.com",
            "password": password
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["id"] == user.id
        assert len(data["access_token"]) > 0

    def test_login_wrong_email(self, test_client, test_session):
        """Test login with non-existent email"""
        # Create a user
        password = "testpassword123"
        hashed = hash_password(password)
        create_user_model(test_session, email="test@example.com", hashed_password=hashed)

        login_data = {
            "email": "wrong@example.com",
            "password": password
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_login_wrong_password(self, test_client, test_session):
        """Test login with incorrect password"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a user
        password = "testpassword123"
        hashed = hash_password(password)
        create_user_model(test_session, email="test@example.com", hashed_password=hashed)

        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_login_missing_email(self, test_client, test_session):
        """Test login without email"""
        login_data = {
            "password": "testpassword123"
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_login_missing_password(self, test_client, test_session):
        """Test login without password"""
        login_data = {
            "email": "test@example.com"
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_login_invalid_email_format(self, test_client, test_session):
        """Test login with invalid email format"""
        login_data = {
            "email": "not-an-email",
            "password": "testpassword123"
        }

        response = test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data


class TestGetCurrentUser:
    """Test suite for GET /api/v1/auth/me endpoint"""

    def test_get_current_user_success(self, test_client, test_session):
        """Test getting current user info with valid token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a user
        user = create_user_model(test_session, email="test@example.com")

        # Create a valid token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert "created_at" in data

    def test_get_current_user_no_token(self, test_client, test_session):
        """Test getting current user without token"""
        response = test_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data

    def test_get_current_user_invalid_token(self, test_client, test_session):
        """Test getting current user with invalid token"""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()

    def test_get_current_user_expired_token(self, test_client, test_session):
        """Test getting current user with expired token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an expired token
        expire = datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        payload = {
            "sub": "1",
            "email": "test@example.com",
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        expired_token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()

    def test_get_current_user_nonexistent_user(self, test_client, test_session):
        """Test getting current user with token for non-existent user"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a token for a user that doesn't exist
        token = create_access_token(data={"sub": "99999", "email": "nonexistent@example.com"})

        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_current_user_malformed_token(self, test_client, test_session):
        """Test getting current user with malformed token"""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.valid.jwt.token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data

    def test_get_current_user_wrong_auth_scheme(self, test_client, test_session):
        """Test getting current user with wrong authorization scheme"""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dXNlcjpwYXNz"}
        )

        # FastAPI HTTPBearer will reject non-Bearer schemes
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        data = response.json()
        assert "detail" in data

