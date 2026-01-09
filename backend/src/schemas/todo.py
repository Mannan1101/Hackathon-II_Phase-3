"""
Pydantic schemas for todo request/response validation.

Defines the API contract for todo endpoints.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TodoBase(BaseModel):
    """Base schema with common todo fields."""
    title: str = Field(..., min_length=1, max_length=200)


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo."""
    title: str | None = Field(None, min_length=1, max_length=200)
    is_complete: bool | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Ensure title is not just whitespace if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty or whitespace only")
            return v.strip()
        return v


class TodoResponse(TodoBase):
    """Schema for todo responses."""
    id: UUID
    user_id: UUID
    is_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TodoListResponse(BaseModel):
    """Schema for list of todos response."""
    todos: list[TodoResponse]
    total: int
