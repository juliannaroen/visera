"""Integration tests for main application"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


class TestRoot:
    """Test suite for GET / endpoint"""

    def test_root(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "running" in data["message"].lower()


class TestHealth:
    """Test suite for GET /health endpoint"""

    def test_health_success(self, test_client):
        """Test health endpoint with successful database connection"""
        response = test_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_health_database_error(self, test_client, test_session):
        """Test health endpoint with database error"""
        from core.database import get_db
        from main import app
        from sqlalchemy import text

        def failing_get_db():
            db = MagicMock()
            db.execute.side_effect = Exception("Database connection failed")
            try:
                yield db
            finally:
                pass

        app.dependency_overrides[get_db] = failing_get_db

        try:
            response = test_client.get("/health")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "error" in data
        finally:
            app.dependency_overrides.clear()

