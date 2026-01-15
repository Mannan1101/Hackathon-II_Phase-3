"""
Pytest configuration and shared fixtures for all tests.

Provides database session fixtures and test utilities.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.config import settings

# Import all models to register them with SQLModel.metadata
from src.models.user import User
from src.models.todo import Todo


# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Create a fresh database session for each test.

    Uses in-memory SQLite for fast, isolated tests.
    All tables are created before each test and dropped after.
    """
    # Create engine with in-memory SQLite
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Required for in-memory SQLite
    )

    # Create all tables using SQLModel metadata
    SQLModel.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def test_settings():
    """
    Provide test settings.

    Override production settings for testing.
    """
    return settings
