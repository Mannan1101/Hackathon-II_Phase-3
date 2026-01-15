"""
MCP Tool Schemas for Todo AI Chatbot.

This module defines input/output schemas for all MCP tools based on contracts/mcp-tools.json.
Schemas are used for validation and documentation.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum for filtering."""
    PENDING = "pending"
    COMPLETED = "completed"


# ==================== ADD_TASK SCHEMAS ====================

class AddTaskInput(BaseModel):
    """Input schema for add_task MCP tool."""
    user_id: str = Field(..., description="User ID from authentication context")
    title: str = Field(..., min_length=1, max_length=200, description="Task title (1-200 characters)")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description (0-1000 characters)")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or just whitespace")
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        """Trim description whitespace."""
        if v is not None:
            return v.strip() if v.strip() else None
        return None


class AddTaskOutput(BaseModel):
    """Output schema for add_task MCP tool."""
    success: bool = Field(..., description="Whether the operation succeeded")
    task_id: str = Field(..., description="UUID of the created task")
    message: str = Field(..., description="User-friendly confirmation message")


# ==================== LIST_TASKS SCHEMAS ====================

class ListTasksInput(BaseModel):
    """Input schema for list_tasks MCP tool."""
    user_id: str = Field(..., description="User ID from authentication context")
    status: Optional[TaskStatus] = Field(None, description="Filter by status (pending/completed)")


class TaskItem(BaseModel):
    """Individual task item in list response."""
    id: str = Field(..., description="Task UUID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status (pending/completed)")
    created_at: str = Field(..., description="ISO timestamp when task was created")
    updated_at: str = Field(..., description="ISO timestamp when task was last updated")


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks MCP tool."""
    tasks: List[TaskItem] = Field(..., description="Array of task items")
    count: int = Field(..., description="Total number of tasks returned")


# ==================== COMPLETE_TASK SCHEMAS ====================

class CompleteTaskInput(BaseModel):
    """Input schema for complete_task MCP tool."""
    user_id: str = Field(..., description="User ID from authentication context")
    task_id: str = Field(..., description="UUID of the task to complete")


class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task MCP tool."""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="User-friendly confirmation message")


# ==================== DELETE_TASK SCHEMAS ====================

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task MCP tool."""
    user_id: str = Field(..., description="User ID from authentication context")
    task_id: str = Field(..., description="UUID of the task to delete")


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task MCP tool."""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="User-friendly confirmation message")


# ==================== UPDATE_TASK SCHEMAS ====================

class UpdateTaskInput(BaseModel):
    """Input schema for update_task MCP tool."""
    user_id: str = Field(..., description="User ID from authentication context")
    task_id: str = Field(..., description="UUID of the task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New title (1-200 characters)")
    description: Optional[str] = Field(None, max_length=1000, description="New description (0-1000 characters)")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or just whitespace")
        return v.strip() if v else None

    @field_validator('description')
    @classmethod
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        """Trim description whitespace."""
        if v is not None:
            return v.strip() if v.strip() else None
        return None

    def model_post_init(self, __context):
        """Validate at least one field is provided."""
        if self.title is None and self.description is None:
            raise ValueError("At least one of title or description must be provided")


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task MCP tool."""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="User-friendly confirmation message")
