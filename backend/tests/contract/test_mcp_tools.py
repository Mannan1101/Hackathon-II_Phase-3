"""
Contract tests for MCP tools.

These tests verify that MCP tool inputs/outputs conform to their schemas
and that tools behave correctly with valid and invalid inputs.

Tests follow TDD principles:
- T013: Contract test for add_task
- T032: Contract test for list_tasks
- T045: Contract test for complete_task
- T058: Contract test for delete_task
- T068: Contract test for update_task
"""
import pytest
from uuid import uuid4, UUID
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task
from src.mcp.schemas import (
    AddTaskInput, AddTaskOutput,
    ListTasksInput, ListTasksOutput,
    CompleteTaskInput, CompleteTaskOutput,
    DeleteTaskInput, DeleteTaskOutput,
    UpdateTaskInput, UpdateTaskOutput
)
from src.models.todo import Todo, TaskStatus
from src.models.user import User
from src.utils.errors import ValidationError, NotFoundError, ForbiddenError


# ==================== FIXTURES ====================

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user for testing."""
    user = User(
        id=uuid4(),
        email=f"test_{uuid4()}@example.com",
        hashed_password="$2b$12$dummy_hash_for_testing"  # Dummy bcrypt hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user2(db: Session) -> User:
    """Create a second test user for isolation testing."""
    user = User(
        id=uuid4(),
        email=f"test2_{uuid4()}@example.com",
        hashed_password="$2b$12$dummy_hash_for_testing"  # Dummy bcrypt hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_todo(db: Session, test_user: User) -> Todo:
    """Create a test todo for testing."""
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Test Task",
        description="Test description",
        status=TaskStatus.PENDING
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ==================== T013: ADD_TASK CONTRACT TESTS ====================

def test_add_task_input_schema_valid():
    """T013: Verify AddTaskInput accepts valid data."""
    input_data = AddTaskInput(
        user_id=str(uuid4()),
        title="Buy groceries",
        description="Milk, eggs, bread"
    )
    assert input_data.title == "Buy groceries"
    assert input_data.description == "Milk, eggs, bread"


def test_add_task_input_schema_title_too_long():
    """T013: Verify AddTaskInput rejects titles > 200 characters."""
    with pytest.raises(PydanticValidationError):
        AddTaskInput(
            user_id=str(uuid4()),
            title="x" * 201,
            description="Test"
        )


def test_add_task_input_schema_description_too_long():
    """T013: Verify AddTaskInput rejects descriptions > 1000 characters."""
    with pytest.raises(PydanticValidationError):
        AddTaskInput(
            user_id=str(uuid4()),
            title="Test",
            description="x" * 1001
        )


def test_add_task_input_schema_empty_title():
    """T013: Verify AddTaskInput rejects empty titles."""
    with pytest.raises(PydanticValidationError):
        AddTaskInput(
            user_id=str(uuid4()),
            title="",
            description="Test"
        )


def test_add_task_output_schema():
    """T013: Verify AddTaskOutput schema."""
    output = AddTaskOutput(
        success=True,
        task_id=str(uuid4()),
        message="Task added"
    )
    assert output.success is True
    assert UUID(output.task_id)  # Verify valid UUID
    assert output.message == "Task added"


def test_add_task_creates_todo(db: Session, test_user: User):
    """T013: Verify add_task creates a todo in database."""
    input_data = AddTaskInput(
        user_id=str(test_user.id),
        title="Buy groceries",
        description="Milk and eggs"
    )

    result = add_task(db, input_data)

    assert result.success is True
    assert result.task_id is not None
    assert "Buy groceries" in result.message

    # Verify in database
    todo = db.query(Todo).filter(Todo.id == UUID(result.task_id)).first()
    assert todo is not None
    assert todo.title == "Buy groceries"
    assert todo.description == "Milk and eggs"
    assert todo.status == TaskStatus.PENDING
    assert todo.user_id == test_user.id


def test_add_task_without_description(db: Session, test_user: User):
    """T013: Verify add_task works without description."""
    input_data = AddTaskInput(
        user_id=str(test_user.id),
        title="Buy groceries"
    )

    result = add_task(db, input_data)

    assert result.success is True
    todo = db.query(Todo).filter(Todo.id == UUID(result.task_id)).first()
    assert todo.description is None


# ==================== T032: LIST_TASKS CONTRACT TESTS ====================

def test_list_tasks_input_schema_valid():
    """T032: Verify ListTasksInput accepts valid data."""
    input_data = ListTasksInput(
        user_id=str(uuid4()),
        status="pending"
    )
    assert input_data.status == "pending"


def test_list_tasks_input_schema_invalid_status():
    """T032: Verify ListTasksInput rejects invalid status."""
    with pytest.raises(PydanticValidationError):
        ListTasksInput(
            user_id=str(uuid4()),
            status="invalid_status"
        )


def test_list_tasks_output_schema():
    """T032: Verify ListTasksOutput schema."""
    output = ListTasksOutput(
        tasks=[
            {
                "id": str(uuid4()),
                "title": "Test",
                "description": "Desc",
                "status": "pending",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        count=1
    )
    assert output.count == 1
    assert len(output.tasks) == 1


def test_list_tasks_returns_user_todos(db: Session, test_user: User, test_todo: Todo):
    """T032: Verify list_tasks returns user's todos."""
    input_data = ListTasksInput(user_id=str(test_user.id))

    result = list_tasks(db, input_data)

    assert result.count >= 1
    assert any(task.id == str(test_todo.id) for task in result.tasks)


def test_list_tasks_filters_by_status(db: Session, test_user: User):
    """T032: Verify list_tasks filters by status."""
    # Create pending and completed tasks
    pending = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Pending Task",
        status=TaskStatus.PENDING
    )
    completed = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Completed Task",
        status=TaskStatus.COMPLETED
    )
    db.add_all([pending, completed])
    db.commit()

    # List only pending
    input_data = ListTasksInput(user_id=str(test_user.id), status="pending")
    result = list_tasks(db, input_data)

    assert all(task.status == "pending" for task in result.tasks)


def test_list_tasks_user_isolation(db: Session, test_user: User, test_user2: User):
    """T032: Verify list_tasks enforces user isolation."""
    # Create task for user1
    todo_user1 = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="User1 Task",
        status=TaskStatus.PENDING
    )
    db.add(todo_user1)
    db.commit()

    # List tasks for user2
    input_data = ListTasksInput(user_id=str(test_user2.id))
    result = list_tasks(db, input_data)

    # Verify user2 doesn't see user1's tasks
    assert not any(task.id == str(todo_user1.id) for task in result.tasks)


def test_list_tasks_empty_list(db: Session, test_user: User):
    """T032: Verify list_tasks handles empty list."""
    # Ensure user has no tasks
    db.query(Todo).filter(Todo.user_id == test_user.id).delete()
    db.commit()

    input_data = ListTasksInput(user_id=str(test_user.id))
    result = list_tasks(db, input_data)

    assert result.count == 0
    assert result.tasks == []


# ==================== T045: COMPLETE_TASK CONTRACT TESTS ====================

def test_complete_task_input_schema_valid():
    """T045: Verify CompleteTaskInput accepts valid data."""
    input_data = CompleteTaskInput(
        user_id=str(uuid4()),
        task_id=str(uuid4())
    )
    assert UUID(input_data.user_id)
    assert UUID(input_data.task_id)


def test_complete_task_output_schema():
    """T045: Verify CompleteTaskOutput schema."""
    output = CompleteTaskOutput(
        success=True,
        message="Task completed"
    )
    assert output.success is True
    assert output.message == "Task completed"


def test_complete_task_marks_as_completed(db: Session, test_user: User, test_todo: Todo):
    """T045: Verify complete_task marks task as completed."""
    input_data = CompleteTaskInput(
        user_id=str(test_user.id),
        task_id=str(test_todo.id)
    )

    result = complete_task(db, input_data)

    assert result.success is True
    assert "completed" in result.message.lower()

    # Verify in database
    db.refresh(test_todo)
    assert test_todo.status == TaskStatus.COMPLETED


def test_complete_task_not_found(db: Session, test_user: User):
    """T045: Verify complete_task handles non-existent task."""
    input_data = CompleteTaskInput(
        user_id=str(test_user.id),
        task_id=str(uuid4())  # Non-existent task
    )

    with pytest.raises(NotFoundError) as exc_info:
        complete_task(db, input_data)

    assert "couldn't find" in exc_info.value.user_message.lower()


def test_complete_task_already_completed(db: Session, test_user: User):
    """T045: Verify complete_task handles already-completed task."""
    # Create completed task
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Already Done",
        status=TaskStatus.COMPLETED
    )
    db.add(todo)
    db.commit()

    input_data = CompleteTaskInput(
        user_id=str(test_user.id),
        task_id=str(todo.id)
    )

    result = complete_task(db, input_data)

    assert result.success is True
    assert "already" in result.message.lower()


def test_complete_task_wrong_user(db: Session, test_user: User, test_user2: User):
    """T045: Verify complete_task enforces user isolation."""
    # Create task for user1
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="User1 Task",
        status=TaskStatus.PENDING
    )
    db.add(todo)
    db.commit()

    # Try to complete as user2
    input_data = CompleteTaskInput(
        user_id=str(test_user2.id),
        task_id=str(todo.id)
    )

    with pytest.raises(NotFoundError):
        complete_task(db, input_data)


# ==================== T058: DELETE_TASK CONTRACT TESTS ====================

def test_delete_task_input_schema_valid():
    """T058: Verify DeleteTaskInput accepts valid data."""
    input_data = DeleteTaskInput(
        user_id=str(uuid4()),
        task_id=str(uuid4())
    )
    assert UUID(input_data.user_id)
    assert UUID(input_data.task_id)


def test_delete_task_output_schema():
    """T058: Verify DeleteTaskOutput schema."""
    output = DeleteTaskOutput(
        success=True,
        message="Task deleted"
    )
    assert output.success is True
    assert output.message == "Task deleted"


def test_delete_task_removes_from_database(db: Session, test_user: User, test_todo: Todo):
    """T058: Verify delete_task removes task from database."""
    task_id = test_todo.id
    input_data = DeleteTaskInput(
        user_id=str(test_user.id),
        task_id=str(task_id)
    )

    result = delete_task(db, input_data)

    assert result.success is True
    assert "deleted" in result.message.lower()

    # Verify removed from database
    todo = db.query(Todo).filter(Todo.id == task_id).first()
    assert todo is None


def test_delete_task_not_found(db: Session, test_user: User):
    """T058: Verify delete_task handles non-existent task."""
    input_data = DeleteTaskInput(
        user_id=str(test_user.id),
        task_id=str(uuid4())  # Non-existent task
    )

    with pytest.raises(NotFoundError) as exc_info:
        delete_task(db, input_data)

    assert "couldn't find" in exc_info.value.user_message.lower()


def test_delete_task_wrong_user(db: Session, test_user: User, test_user2: User):
    """T058: Verify delete_task enforces user isolation."""
    # Create task for user1
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="User1 Task",
        status=TaskStatus.PENDING
    )
    db.add(todo)
    db.commit()

    # Try to delete as user2
    input_data = DeleteTaskInput(
        user_id=str(test_user2.id),
        task_id=str(todo.id)
    )

    with pytest.raises(NotFoundError):
        delete_task(db, input_data)


# ==================== T068: UPDATE_TASK CONTRACT TESTS ====================

def test_update_task_input_schema_valid():
    """T068: Verify UpdateTaskInput accepts valid data."""
    input_data = UpdateTaskInput(
        user_id=str(uuid4()),
        task_id=str(uuid4()),
        title="New Title",
        description="New Description"
    )
    assert input_data.title == "New Title"
    assert input_data.description == "New Description"


def test_update_task_input_schema_title_too_long():
    """T068: Verify UpdateTaskInput rejects titles > 200 characters."""
    with pytest.raises(PydanticValidationError):
        UpdateTaskInput(
            user_id=str(uuid4()),
            task_id=str(uuid4()),
            title="x" * 201
        )


def test_update_task_input_schema_description_too_long():
    """T068: Verify UpdateTaskInput rejects descriptions > 1000 characters."""
    with pytest.raises(PydanticValidationError):
        UpdateTaskInput(
            user_id=str(uuid4()),
            task_id=str(uuid4()),
            description="x" * 1001
        )


def test_update_task_output_schema():
    """T068: Verify UpdateTaskOutput schema."""
    output = UpdateTaskOutput(
        success=True,
        message="Task updated"
    )
    assert output.success is True
    assert output.message == "Task updated"


def test_update_task_updates_title(db: Session, test_user: User, test_todo: Todo):
    """T068: Verify update_task updates title."""
    input_data = UpdateTaskInput(
        user_id=str(test_user.id),
        task_id=str(test_todo.id),
        title="New Title"
    )

    result = update_task(db, input_data)

    assert result.success is True
    assert "updated" in result.message.lower()

    # Verify in database
    db.refresh(test_todo)
    assert test_todo.title == "New Title"


def test_update_task_updates_description(db: Session, test_user: User, test_todo: Todo):
    """T068: Verify update_task updates description."""
    input_data = UpdateTaskInput(
        user_id=str(test_user.id),
        task_id=str(test_todo.id),
        description="New Description"
    )

    result = update_task(db, input_data)

    assert result.success is True

    # Verify in database
    db.refresh(test_todo)
    assert test_todo.description == "New Description"


def test_update_task_requires_at_least_one_field(db: Session, test_user: User, test_todo: Todo):
    """T068: Verify update_task requires at least one field."""
    # Validation happens at Pydantic schema level
    with pytest.raises(PydanticValidationError) as exc_info:
        UpdateTaskInput(
            user_id=str(test_user.id),
            task_id=str(test_todo.id)
            # No title or description
        )

    assert "at least one" in str(exc_info.value).lower()


def test_update_task_not_found(db: Session, test_user: User):
    """T068: Verify update_task handles non-existent task."""
    input_data = UpdateTaskInput(
        user_id=str(test_user.id),
        task_id=str(uuid4()),  # Non-existent task
        title="New Title"
    )

    with pytest.raises(NotFoundError) as exc_info:
        update_task(db, input_data)

    assert "couldn't find" in exc_info.value.user_message.lower()


def test_update_task_wrong_user(db: Session, test_user: User, test_user2: User):
    """T068: Verify update_task enforces user isolation."""
    # Create task for user1
    todo = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="User1 Task",
        status=TaskStatus.PENDING
    )
    db.add(todo)
    db.commit()

    # Try to update as user2
    input_data = UpdateTaskInput(
        user_id=str(test_user2.id),
        task_id=str(todo.id),
        title="Hacked Title"
    )

    with pytest.raises(NotFoundError):
        update_task(db, input_data)
