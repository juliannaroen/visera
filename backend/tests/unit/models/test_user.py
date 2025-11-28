"""Unit tests for User model"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from models.user import User
from tests.fixtures.factories import create_user_factory


class TestUserModel:
    """Test suite for User model"""

    def test_user_creation(self, test_session):
        """Test creating a user with valid data"""
        user_data = create_user_factory()
        user = User(**user_data)

        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.hashed_password == user_data["hashed_password"]
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_email_required(self, test_session):
        """Test that email is required (not nullable)"""
        user = User(hashed_password="hashed_password")

        test_session.add(user)

        with pytest.raises(Exception):  # SQLAlchemy will raise an exception
            test_session.commit()

    def test_user_email_unique(self, test_session):
        """Test that email must be unique"""
        user_data = create_user_factory(email="test@example.com")
        user1 = User(**user_data)
        user2 = User(**user_data)  # Same email

        test_session.add(user1)
        test_session.commit()

        test_session.add(user2)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_user_password_can_be_null(self, test_session):
        """Test that hashed_password can be nullable"""
        user = User(email="test@example.com", hashed_password=None)

        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        assert user.hashed_password is None
        assert user.email == "test@example.com"

    def test_user_created_at_auto_generated(self, test_session):
        """Test that created_at is automatically generated"""
        user_data = create_user_factory()
        user = User(**user_data)

        # created_at should be None before commit (server_default)
        assert user.created_at is None

        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        # After commit, created_at should be set
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_repr(self, test_session):
        """Test that user can be converted to string without error"""
        user_data = create_user_factory(email="test@example.com")
        user = User(**user_data)

        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        # Basic check that user can be converted to string without error
        # Note: User model doesn't define __repr__, so it uses default object representation
        user_str = str(user)
        assert isinstance(user_str, str)
        assert len(user_str) > 0

    def test_user_query_by_email(self, test_session):
        """Test querying user by email"""
        user_data = create_user_factory(email="unique@example.com")
        user = User(**user_data)

        test_session.add(user)
        test_session.commit()

        # Query by email
        found_user = test_session.query(User).filter(User.email == "unique@example.com").first()

        assert found_user is not None
        assert found_user.email == "unique@example.com"
        assert found_user.id == user.id

    def test_user_query_by_id(self, test_session):
        """Test querying user by ID"""
        user_data = create_user_factory()
        user = User(**user_data)

        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)

        # Query by ID
        found_user = test_session.query(User).filter(User.id == user.id).first()

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == user.email

