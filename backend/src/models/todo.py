"""
Todo model for database persistence.

Represents a todo item with user ownership, completion status, and timestamps.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Todo(SQLModel, table=True):
    """
    Todo model with user ownership and completion tracking.

    Constitutional requirements:
    - User isolation via user_id FK
    - Immutable created_at timestamp
    - Updated_at timestamp for modification tracking
    """
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    is_complete: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to User model (optional, for ORM convenience)
    # user: "User" = Relationship(back_populates="todos")
