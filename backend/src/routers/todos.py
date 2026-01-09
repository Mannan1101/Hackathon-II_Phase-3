"""
Todos router with CRUD endpoints.

All endpoints require authentication and enforce user data isolation.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import require_auth
from ..models.user import User
from ..schemas.todo import (
    TodoCreate,
    TodoListResponse,
    TodoResponse,
    TodoUpdate,
)
from ..services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", status_code=status.HTTP_200_OK, response_model=TodoListResponse)
async def get_todos(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Get all todos for the authenticated user.

    Returns todos sorted by created_at DESC.
    Enforces data isolation - users can only see their own todos.

    Returns:
        TodoListResponse with list of todos and total count

    Raises:
        401: If user is not authenticated
        500: If database error occurs
    """
    try:
        todo_service = TodoService(db)
        todos = todo_service.get_todos(current_user.id)

        return TodoListResponse(
            todos=[TodoResponse.model_validate(todo) for todo in todos],
            total=len(todos),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve todos: {str(e)}"
        )


@router.get("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def get_todo(
    todo_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Get a specific todo by ID.

    Enforces ownership - users can only access their own todos.

    Args:
        todo_id: UUID of the todo to retrieve

    Returns:
        TodoResponse with todo details

    Raises:
        401: If user is not authenticated
        404: If todo not found or not owned by user
    """
    todo_service = TodoService(db)
    todo = todo_service.get_todo_by_id(todo_id, current_user.id)
    return TodoResponse.model_validate(todo)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(
    request: TodoCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Create a new todo for the authenticated user.

    Args:
        request: TodoCreate with title

    Returns:
        TodoResponse with created todo details

    Raises:
        400: If validation fails (empty title, too long, etc.)
        401: If user is not authenticated
    """
    try:
        todo_service = TodoService(db)
        todo = todo_service.create_todo(current_user.id, request)
        return TodoResponse.model_validate(todo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    todo_id: UUID,
    request: TodoUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Update an existing todo.

    Can update title and/or is_complete status.
    Enforces ownership - users can only update their own todos.

    Args:
        todo_id: UUID of the todo to update
        request: TodoUpdate with optional title and is_complete

    Returns:
        TodoResponse with updated todo details

    Raises:
        400: If validation fails or no fields to update
        401: If user is not authenticated
        404: If todo not found or not owned by user
    """
    todo_service = TodoService(db)
    todo = todo_service.update_todo(todo_id, current_user.id, request)
    return TodoResponse.model_validate(todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Delete a todo.

    Enforces ownership - users can only delete their own todos.

    Args:
        todo_id: UUID of the todo to delete

    Returns:
        204 No Content on success

    Raises:
        401: If user is not authenticated
        404: If todo not found or not owned by user
    """
    todo_service = TodoService(db)
    todo_service.delete_todo(todo_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{todo_id}/toggle", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def toggle_todo_completion(
    todo_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """
    Toggle the completion status of a todo.

    Convenience endpoint for toggling is_complete without needing to know current state.
    Enforces ownership - users can only toggle their own todos.

    Args:
        todo_id: UUID of the todo to toggle

    Returns:
        TodoResponse with updated todo details

    Raises:
        401: If user is not authenticated
        404: If todo not found or not owned by user
    """
    todo_service = TodoService(db)
    todo = todo_service.toggle_todo_completion(todo_id, current_user.id)
    return TodoResponse.model_validate(todo)
