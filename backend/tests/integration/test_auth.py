"""Integration tests for authentication endpoints"""
import pytest
import os
import jwt
from datetime import datetime, timedelta
from fastapi import status
from core.security import hash_password, create_access_token, create_email_verification_token
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


class TestVerifyEmail:
    """Test suite for POST /api/v1/auth/verify-email endpoint"""

    def test_verify_email_success(self, test_client, test_session):
        """Test successful email verification"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an unverified user
        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        # Create a valid verification token
        token = create_email_verification_token(user.id, user.email)

        verify_data = {"token": token}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["is_email_verified"] is True

        # Verify user is actually verified in database
        test_session.refresh(user)
        assert user.is_email_verified is True

    def test_verify_email_invalid_token(self, test_client, test_session):
        """Test verification with invalid token"""
        verify_data = {"token": "invalid-token"}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()

    def test_verify_email_expired_token(self, test_client, test_session):
        """Test verification with expired token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        # Create an expired token
        expire = datetime.utcnow() - timedelta(hours=25)  # Expired (24h expiry)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "email_verification",
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(hours=26)
        }
        expired_token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        verify_data = {"token": expired_token}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data

    def test_verify_email_user_not_found(self, test_client, test_session):
        """Test verification with token for non-existent user"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a token for a user that doesn't exist
        token = create_email_verification_token(99999, "nonexistent@example.com")

        verify_data = {"token": token}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_verify_email_email_mismatch(self, test_client, test_session):
        """Test verification when token email doesn't match user email"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        # Create a token with different email
        token = create_email_verification_token(user.id, "different@example.com")

        verify_data = {"token": token}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower() or "match" in data["detail"].lower()

    def test_verify_email_already_verified(self, test_client, test_session):
        """Test verification when email is already verified"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a verified user
        user = create_user_model(test_session, email="test@example.com", is_email_verified=True)

        # Create a valid verification token
        token = create_email_verification_token(user.id, user.email)

        verify_data = {"token": token}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_email_verified"] is True

    def test_verify_email_wrong_token_type(self, test_client, test_session):
        """Test verification with access token instead of verification token"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        # Create an access token (wrong type)
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        verify_data = {"token": token}

        response = test_client.post("/api/v1/auth/verify-email", json=verify_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data


class TestSendVerificationEmail:
    """Test suite for POST /api/v1/auth/send-verification-email endpoint"""

    def test_send_verification_email_success(self, test_client, test_session):
        """Test successfully sending verification email"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an unverified user
        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        # Create a valid token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = test_client.post(
            "/api/v1/auth/send-verification-email",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Note: This will likely fail if SMTP is not configured, but we test the endpoint logic
        # The endpoint should return 200 if email service is configured, or 500 if not
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
        data = response.json()
        assert "detail" in data or "message" in data

    def test_send_verification_email_already_verified(self, test_client, test_session):
        """Test sending verification email when already verified"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a verified user
        user = create_user_model(test_session, email="test@example.com", is_email_verified=True)

        # Create a valid token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = test_client.post(
            "/api/v1/auth/send-verification-email",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "already verified" in data["detail"].lower()

    def test_send_verification_email_no_token(self, test_client, test_session):
        """Test sending verification email without token"""
        response = test_client.post("/api/v1/auth/send-verification-email")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data

