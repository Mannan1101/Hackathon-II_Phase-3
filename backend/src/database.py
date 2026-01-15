"""
Database connection and session management.

This module provides SQLAlchemy engine, session management, and base model class.
Uses SQLModel for ORM (compatible with the model definitions).
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from sqlmodel import SQLModel
from typing import Generator
from .config import settings

# Configure engine based on database type
def _create_engine():
    """Create database engine with appropriate configuration."""
    database_url = settings.DATABASE_URL

    # PostgreSQL-specific configuration
    if database_url.startswith("postgresql"):
        return create_engine(
            database_url,
            echo=settings.APP_ENV == "development",
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before use
        )
    # SQLite configuration (for testing)
    elif "sqlite" in database_url:
        return create_engine(
            database_url,
            echo=settings.APP_ENV == "development",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
    # Default configuration
    else:
        return create_engine(
            database_url,
            echo=settings.APP_ENV == "development",
        )

# Create SQLAlchemy engine
engine = _create_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models (using SQLModel's metadata)
Base = SQLModel


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Yields:
        Session: SQLAlchemy database session

    Example:
        ```python
        @app.get("/users")
        async def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should only be used for testing. In production, use Alembic migrations.
    """
    # Import models to ensure they are registered with SQLModel
    from .models.user import User
    from .models.todo import Todo

    SQLModel.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
