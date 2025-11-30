"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Lazy initialization - only create engine when needed
# This prevents import-time errors if DATABASE_URL is not set
engine = None
SessionLocal = None

def get_engine():
    """Get or create the database engine"""
    global engine
    if engine is None:
        if not settings.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=300,    # Recycle connections after 5 minutes
            echo=False           # Set to True for SQL query logging
        )
    return engine

def get_session_local():
    """Get or create the session maker"""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

