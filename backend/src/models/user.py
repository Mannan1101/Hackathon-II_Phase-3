"""
User model for authentication and data ownership.

This module defines the User SQLModel for database persistence.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class User(SQLModel, table=True):
    """
    User model representing authenticated users.

    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique, indexed)
        hashed_password: Bcrypt hashed password
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-01-07T12:00:00Z",
                "updated_at": "2026-01-07T12:00:00Z",
            }
        }
