"""Shared pytest fixtures"""
import os

# Set required environment variables before any imports that might use them
# This ensures Settings is initialized correctly at import time
if not os.getenv("JWT_SECRET_KEY"):
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
if not os.getenv("AUTH_COOKIE_NAME"):
    os.environ["AUTH_COOKIE_NAME"] = "test.sid"
if not os.getenv("AUTH_COOKIE_MAX_AGE"):
    os.environ["AUTH_COOKIE_MAX_AGE"] = "3600"
if not os.getenv("JWT_EXPIRE_MINUTES"):
    os.environ["JWT_EXPIRE_MINUTES"] = "30"
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
if not os.getenv("SMTP_HOST"):
    os.environ["SMTP_HOST"] = "smtp.test.com"
if not os.getenv("SMTP_PORT"):
    os.environ["SMTP_PORT"] = "587"
if not os.getenv("SMTP_USER"):
    os.environ["SMTP_USER"] = "test@test.com"
if not os.getenv("SMTP_PASSWORD"):
    os.environ["SMTP_PASSWORD"] = "testpass"
if not os.getenv("SMTP_FROM_EMAIL"):
    os.environ["SMTP_FROM_EMAIL"] = "test@test.com"
if not os.getenv("FRONTEND_URL"):
    os.environ["FRONTEND_URL"] = "http://localhost:3000"
if not os.getenv("ALLOWED_ORIGINS"):
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.database import Base, get_db
from main import app


# Use in-memory SQLite for testing (fast, no external dependencies)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_client(test_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up dependency override
    app.dependency_overrides.clear()

