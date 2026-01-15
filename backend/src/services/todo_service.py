"""
TodoService handles all todo-related business logic.

Implements CRUD operations with user ownership enforcement.
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.todo import Todo, TaskStatus
from ..schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    """Service layer for todo operations."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def get_todos(self, user_id: UUID) -> list[Todo]:
        """
        Retrieve all todos for a specific user, sorted by created_at DESC.

        Args:
            user_id: UUID of the authenticated user

        Returns:
            List of Todo objects owned by the user
        """
        todos = (
            self.db.query(Todo)
            .filter(Todo.user_id == user_id)  # type: ignore[arg-type]
            .order_by(desc(Todo.created_at))  # type: ignore[arg-type]
            .all()
        )
        return todos

    def get_todo_by_id(self, todo_id: UUID, user_id: UUID) -> Todo:
        """
        Retrieve a specific todo by ID with ownership verification.

        Args:
            todo_id: UUID of the todo
            user_id: UUID of the authenticated user

        Returns:
            Todo object if found and owned by user

        Raises:
            HTTPException: 404 if todo not found or not owned by user
        """
        todo = (
            self.db.query(Todo)
            .filter(Todo.id == todo_id, Todo.user_id == user_id)  # type: ignore[arg-type]
            .first()
        )

        if not todo:
            raise HTTPException(
                status_code=404,
                detail="Todo not found"
            )

        return todo

    def create_todo(self, user_id: UUID, request: TodoCreate) -> Todo:
        """
        Create a new todo for a user.

        Args:
            user_id: UUID of the authenticated user
            request: TodoCreate schema with todo data

        Returns:
            Created Todo object
        """
        todo = Todo(
            user_id=user_id,
            title=request.title,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)

        return todo

    def update_todo(self, todo_id: UUID, user_id: UUID, request: TodoUpdate) -> Todo:
        """
        Update an existing todo with ownership verification.

        Args:
            todo_id: UUID of the todo to update
            user_id: UUID of the authenticated user
            request: TodoUpdate schema with update data

        Returns:
            Updated Todo object

        Raises:
            HTTPException: 404 if todo not found or not owned by user
            HTTPException: 400 if no fields to update
        """
        todo = self.get_todo_by_id(todo_id, user_id)

        # Track if any fields were updated
        updated = False

        if request.title is not None:
            todo.title = request.title
            updated = True

        if request.is_complete is not None:
            todo.status = TaskStatus.COMPLETED if request.is_complete else TaskStatus.PENDING
            updated = True

        if not updated:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )

        todo.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(todo)

        return todo

    def delete_todo(self, todo_id: UUID, user_id: UUID) -> None:
        """
        Delete a todo with ownership verification.

        Args:
            todo_id: UUID of the todo to delete
            user_id: UUID of the authenticated user

        Raises:
            HTTPException: 404 if todo not found or not owned by user
        """
        todo = self.get_todo_by_id(todo_id, user_id)

        self.db.delete(todo)
        self.db.commit()

    def toggle_todo_completion(self, todo_id: UUID, user_id: UUID) -> Todo:
        """
        Toggle the completion status of a todo.

        Args:
            todo_id: UUID of the todo to toggle
            user_id: UUID of the authenticated user

        Returns:
            Updated Todo object

        Raises:
            HTTPException: 404 if todo not found or not owned by user
        """
        todo = self.get_todo_by_id(todo_id, user_id)

        # Toggle status between PENDING and COMPLETED
        todo.status = TaskStatus.PENDING if todo.status == TaskStatus.COMPLETED else TaskStatus.COMPLETED
        todo.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(todo)

        return todo
