"""
MCP Tools for Todo AI Chatbot.

This module implements the 5 MCP tools that the AI agent uses to manage todos:
- add_task: Create a new todo
- list_tasks: Retrieve user's todos (with optional status filter)
- complete_task: Mark a todo as completed
- delete_task: Remove a todo
- update_task: Modify todo title/description

All tools enforce user isolation (user_id filtering) per FR-008 and SC-008.
All tools return user-friendly messages per FR-010.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.todo import Todo, TaskStatus
from ..mcp.schemas import (
    AddTaskInput, AddTaskOutput,
    ListTasksInput, ListTasksOutput, TaskItem,
    CompleteTaskInput, CompleteTaskOutput,
    DeleteTaskInput, DeleteTaskOutput,
    UpdateTaskInput, UpdateTaskOutput
)
from ..utils.errors import (
    ValidationError, NotFoundError, DatabaseError,
    validation_error_response, not_found_error_response, database_error_response
)
from ..config import get_logger

logger = get_logger("mcp.tools")


# ==================== ADD_TASK TOOL ====================

def add_task(db: Session, input_data: AddTaskInput) -> AddTaskOutput:
    """
    Create a new todo task for the authenticated user.

    Args:
        db: Database session
        input_data: Validated input (user_id, title, description)

    Returns:
        AddTaskOutput: Success status, task_id, and confirmation message

    Raises:
        ValidationError: If title/description validation fails
        DatabaseError: If database operation fails
    """
    try:
        # Validate input (already done by Pydantic, but double-check)
        if not input_data.title or len(input_data.title) > 200:
            raise ValidationError(
                message=f"Title validation failed: length={len(input_data.title)}",
                user_message=validation_error_response("Title", "must be between 1 and 200 characters"),
                context={"user_id": input_data.user_id, "title_length": len(input_data.title)}
            )

        if input_data.description and len(input_data.description) > 1000:
            raise ValidationError(
                message=f"Description validation failed: length={len(input_data.description)}",
                user_message=validation_error_response("Description", "must be under 1000 characters"),
                context={"user_id": input_data.user_id, "description_length": len(input_data.description)}
            )

        # Create new todo
        new_todo = Todo(
            user_id=UUID(input_data.user_id),
            title=input_data.title,
            description=input_data.description,
            status=TaskStatus.PENDING
        )

        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)

        logger.info(f"Task created successfully", extra={
            "user_id": input_data.user_id,
            "task_id": str(new_todo.id),
            "title": input_data.title
        })

        return AddTaskOutput(
            success=True,
            task_id=str(new_todo.id),
            message=f"I've added '{input_data.title}' to your tasks!"
        )

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Database error in add_task: {str(e)}", extra={
            "user_id": input_data.user_id,
            "error": str(e)
        })
        raise DatabaseError(
            message=f"Failed to create task: {str(e)}",
            user_message=database_error_response("saving"),
            context={"user_id": input_data.user_id}
        )


# ==================== LIST_TASKS TOOL ====================

def list_tasks(db: Session, input_data: ListTasksInput) -> ListTasksOutput:
    """
    Retrieve all todo tasks for the authenticated user.

    Args:
        db: Database session
        input_data: Validated input (user_id, optional status filter)

    Returns:
        ListTasksOutput: Array of tasks and count

    Raises:
        DatabaseError: If database operation fails
    """
    try:
        # Build query with user isolation
        query = db.query(Todo).filter(Todo.user_id == UUID(input_data.user_id))

        # Apply status filter if provided
        if input_data.status:
            query = query.filter(Todo.status == input_data.status)

        # Order by created_at descending (newest first)
        query = query.order_by(Todo.created_at.desc())

        # Execute query
        todos = query.all()

        # Convert to response format
        task_items = [
            TaskItem(
                id=str(todo.id),
                title=todo.title,
                description=todo.description,
                status=todo.status.value,
                created_at=todo.created_at.isoformat(),
                updated_at=todo.updated_at.isoformat()
            )
            for todo in todos
        ]

        logger.info(f"Tasks listed successfully", extra={
            "user_id": input_data.user_id,
            "count": len(task_items),
            "status_filter": input_data.status.value if input_data.status else None
        })

        return ListTasksOutput(
            tasks=task_items,
            count=len(task_items)
        )

    except Exception as e:
        logger.error(f"Database error in list_tasks: {str(e)}", extra={
            "user_id": input_data.user_id,
            "error": str(e)
        })
        raise DatabaseError(
            message=f"Failed to list tasks: {str(e)}",
            user_message=database_error_response("retrieving"),
            context={"user_id": input_data.user_id}
        )


# ==================== COMPLETE_TASK TOOL ====================

def complete_task(db: Session, input_data: CompleteTaskInput) -> CompleteTaskOutput:
    """
    Mark a todo task as completed.

    Args:
        db: Database session
        input_data: Validated input (user_id, task_id)

    Returns:
        CompleteTaskOutput: Success status and confirmation message

    Raises:
        NotFoundError: If task not found or doesn't belong to user
        DatabaseError: If database operation fails
    """
    try:
        # Fetch task with user isolation
        task = db.query(Todo).filter(
            Todo.id == UUID(input_data.task_id),
            Todo.user_id == UUID(input_data.user_id)
        ).first()

        if not task:
            raise NotFoundError(
                message=f"Task not found: task_id={input_data.task_id}, user_id={input_data.user_id}",
                user_message=not_found_error_response("task"),
                context={"user_id": input_data.user_id, "task_id": input_data.task_id}
            )

        # Check if already completed
        if task.status == TaskStatus.COMPLETED:
            return CompleteTaskOutput(
                success=True,
                message="That task is already marked as complete!"
            )

        # Update status
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Task completed successfully", extra={
            "user_id": input_data.user_id,
            "task_id": input_data.task_id,
            "title": task.title
        })

        return CompleteTaskOutput(
            success=True,
            message=f"Great! I've marked '{task.title}' as completed."
        )

    except (ValidationError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Database error in complete_task: {str(e)}", extra={
            "user_id": input_data.user_id,
            "task_id": input_data.task_id,
            "error": str(e)
        })
        raise DatabaseError(
            message=f"Failed to complete task: {str(e)}",
            user_message=database_error_response("updating"),
            context={"user_id": input_data.user_id, "task_id": input_data.task_id}
        )


# ==================== DELETE_TASK TOOL ====================

def delete_task(db: Session, input_data: DeleteTaskInput) -> DeleteTaskOutput:
    """
    Delete a todo task.

    Args:
        db: Database session
        input_data: Validated input (user_id, task_id)

    Returns:
        DeleteTaskOutput: Success status and confirmation message

    Raises:
        NotFoundError: If task not found or doesn't belong to user
        DatabaseError: If database operation fails
    """
    try:
        # Fetch task with user isolation
        task = db.query(Todo).filter(
            Todo.id == UUID(input_data.task_id),
            Todo.user_id == UUID(input_data.user_id)
        ).first()

        if not task:
            raise NotFoundError(
                message=f"Task not found: task_id={input_data.task_id}, user_id={input_data.user_id}",
                user_message="I couldn't find a task matching that. Your tasks are still intact.",
                context={"user_id": input_data.user_id, "task_id": input_data.task_id}
            )

        # Store title for confirmation message
        task_title = task.title

        # Delete task
        db.delete(task)
        db.commit()

        logger.info(f"Task deleted successfully", extra={
            "user_id": input_data.user_id,
            "task_id": input_data.task_id,
            "title": task_title
        })

        return DeleteTaskOutput(
            success=True,
            message=f"I've deleted the '{task_title}' task."
        )

    except (ValidationError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Database error in delete_task: {str(e)}", extra={
            "user_id": input_data.user_id,
            "task_id": input_data.task_id,
            "error": str(e)
        })
        raise DatabaseError(
            message=f"Failed to delete task: {str(e)}",
            user_message=database_error_response("deleting"),
            context={"user_id": input_data.user_id, "task_id": input_data.task_id}
        )


# ==================== UPDATE_TASK TOOL ====================

def update_task(db: Session, input_data: UpdateTaskInput) -> UpdateTaskOutput:
    """
    Update a todo task's title and/or description.

    Args:
        db: Database session
        input_data: Validated input (user_id, task_id, title?, description?)

    Returns:
        UpdateTaskOutput: Success status and confirmation message

    Raises:
        ValidationError: If validation fails (no fields provided, invalid length)
        NotFoundError: If task not found or doesn't belong to user
        DatabaseError: If database operation fails
    """
    try:
        # Validate at least one field provided (already done by Pydantic)
        if input_data.title is None and input_data.description is None:
            raise ValidationError(
                message="No fields to update",
                user_message="Please provide a new title or description to update.",
                context={"user_id": input_data.user_id, "task_id": input_data.task_id}
            )

        # Fetch task with user isolation
        task = db.query(Todo).filter(
            Todo.id == UUID(input_data.task_id),
            Todo.user_id == UUID(input_data.user_id)
        ).first()

        if not task:
            raise NotFoundError(
                message=f"Task not found: task_id={input_data.task_id}, user_id={input_data.user_id}",
                user_message="I couldn't find that task to update.",
                context={"user_id": input_data.user_id, "task_id": input_data.task_id}
            )

        # Update fields
        updated_fields = []
        if input_data.title is not None:
            task.title = input_data.title
            updated_fields.append("title")

        if input_data.description is not None:
            task.description = input_data.description
            updated_fields.append("description")

        task.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Task updated successfully", extra={
            "user_id": input_data.user_id,
            "task_id": input_data.task_id,
            "updated_fields": updated_fields
        })

        # Generate appropriate message
        if "title" in updated_fields:
            message = f"I've updated your task to '{task.title}'."
        else:
            message = "I've added the note to your task."

        return UpdateTaskOutput(
            success=True,
            message=message
        )

    except (ValidationError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Database error in update_task: {str(e)}", extra={
            "user_id": input_data.user_id,
            "task_id": input_data.task_id,
            "error": str(e)
        })
        raise DatabaseError(
            message=f"Failed to update task: {str(e)}",
            user_message=database_error_response("updating"),
            context={"user_id": input_data.user_id, "task_id": input_data.task_id}
        )
