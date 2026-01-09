"""
Authentication request/response schemas.

This module defines Pydantic models for auth API validation.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
import re


class SignupRequest(BaseModel):
    """Request schema for user signup."""

    email: str = Field(..., max_length=255, description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets minimum requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 100:
            raise ValueError("Password must be at most 100 characters long")
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
            }
        }


class SigninRequest(BaseModel):
    """Request schema for user signin."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v.lower()

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
            }
        }


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints."""

    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-01-07T12:00:00Z",
            }
        }
