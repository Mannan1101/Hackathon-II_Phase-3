"""
Todo model for database persistence.

Represents a todo item with user ownership, completion status, and timestamps.

Updated for Feature 001-todo-ai-chatbot: Added description field and status enum.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Enum as SAEnum, String


class TaskStatus(str, Enum):
    """Task completion status enum."""
    PENDING = "pending"
    COMPLETED = "completed"


class Todo(SQLModel, table=True):
    """
    Todo model with user ownership and completion tracking.

    Constitutional requirements:
    - User isolation via user_id FK
    - Immutable created_at timestamp
    - Updated_at timestamp for modification tracking

    Chatbot requirements (FR-001 to FR-014):
    - Title: 1-200 characters (validated by chatbot MCP tools)
    - Description: 0-1000 characters (optional, validated by chatbot MCP tools)
    - Status: "pending" or "completed" (enum)
    """
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000, nullable=True)
    # Use sa_column to properly configure the PostgreSQL enum type
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        sa_column=Column(
            SAEnum(TaskStatus, values_callable=lambda x: [e.value for e in x], native_enum=True, name="taskstatus"),
            nullable=False
        )
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    @property
    def is_complete(self) -> bool:
        """Return True if task status is COMPLETED (for API compatibility)."""
        return self.status == TaskStatus.COMPLETED

    @is_complete.setter
    def is_complete(self, value: bool) -> None:
        """Set status based on boolean completion value."""
        self.status = TaskStatus.COMPLETED if value else TaskStatus.PENDING
