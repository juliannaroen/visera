"""Integration tests for API dependencies"""
import pytest
import os
import jwt
from datetime import datetime, timedelta
from fastapi import status
from core.security import create_access_token
from tests.fixtures.factories import create_user_model


class TestGetCurrentUser:
    """Test suite for get_current_user dependency"""

    def test_get_current_user_invalid_token_payload_no_sub(self, test_client, test_session):
        """Test get_current_user with token missing 'sub' field"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a token without 'sub' field
        payload = {
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "invalid token payload" in data["detail"].lower() or "payload" in data["detail"].lower()


class TestGetVerifiedUser:
    """Test suite for get_verified_user dependency"""

    def test_get_verified_user_unverified_email(self, test_client, test_session):
        """Test get_verified_user with unverified email"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create an unverified user
        user = create_user_model(test_session, email="test@example.com", is_email_verified=False)

        # Create a valid token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "verification" in data["detail"].lower() or "verified" in data["detail"].lower()

    def test_get_verified_user_verified_email(self, test_client, test_session):
        """Test get_verified_user with verified email"""
        # Set JWT_SECRET_KEY if not set
        if not os.getenv("JWT_SECRET_KEY"):
            os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

        # Create a verified user
        user = create_user_model(test_session, email="test@example.com", is_email_verified=True)

        # Create a valid token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["is_email_verified"] is True

