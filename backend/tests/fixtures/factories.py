"""Test data factories"""
from faker import Faker
from models.user import User

fake = Faker()


def create_user_factory(**kwargs) -> dict:
    """Factory function to create user test data"""
    defaults = {
        "email": fake.email(),
        "hashed_password": fake.password(length=12),
    }
    defaults.update(kwargs)
    return defaults


def create_user_model(db_session, **kwargs) -> User:
    """Create a User model instance in the database"""
    user_data = create_user_factory(**kwargs)
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

