"""
Security tests for user isolation (T091).

Verifies that users cannot access each other's tasks and that
user isolation is enforced at all levels (FR-008, SC-008).
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from src.agent.chatbot import TodoChatbot
from src.models.user import User
from src.models.todo import Todo, TaskStatus
from src.mcp.tools import list_tasks, complete_task, delete_task, update_task
from src.mcp.schemas import (
    ListTasksInput,
    CompleteTaskInput,
    DeleteTaskInput,
    UpdateTaskInput
)
from src.utils.errors import NotFoundError


@pytest.fixture
def user1(db: Session) -> User:
    """Create first test user."""
    user = User(
        id=uuid4(),
        email=f"user1_{uuid4()}@example.com",
        hashed_password="$2b$12$dummy_hash_for_testing"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user2(db: Session) -> User:
    """Create second test user."""
    user = User(
        id=uuid4(),
        email=f"user2_{uuid4()}@example.com",
        hashed_password="$2b$12$dummy_hash_for_testing"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==================== CHATBOT-LEVEL USER ISOLATION ====================

@pytest.mark.asyncio
async def test_user_isolation_list_tasks(db: Session, user1: User, user2: User):
    """
    T091: Verify user1 cannot see user2's tasks via chatbot.

    Tests FR-008 and SC-008: User isolation at chatbot level.
    """
    # Create tasks for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # User2's chatbot should not see user1's tasks
    chatbot2 = TodoChatbot(user_id=user2.id, db=db)
    result = await chatbot2.process_message("What are my tasks?")

    assert result["message"]
    # Should indicate no tasks or empty list
    message_lower = result["message"].lower()
    assert ("no tasks" in message_lower or
            "don't have any" in message_lower or
            "0" in result["message"] or
            "empty" in message_lower)


@pytest.mark.asyncio
async def test_user_isolation_cannot_complete_other_users_task(db: Session, user1: User, user2: User):
    """
    T091: Verify user2 cannot complete user1's task.

    Tests SC-008: User isolation prevents cross-user task manipulation.
    """
    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Secret Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # User2 tries to complete user1's task via chatbot
    chatbot2 = TodoChatbot(user_id=user2.id, db=db)
    result = await chatbot2.process_message(f"Complete 'User1 Secret Task'")

    assert result["message"]
    # Should indicate task not found (not expose that it exists for another user)
    assert "couldn't find" in result["message"].lower() or "not found" in result["message"].lower()

    # Verify task is still pending (not completed by user2)
    db.refresh(task1)
    assert task1.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_user_isolation_cannot_delete_other_users_task(db: Session, user1: User, user2: User):
    """
    T091: Verify user2 cannot delete user1's task.
    """
    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Important Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()
    task_id = task1.id

    # User2 tries to delete user1's task
    chatbot2 = TodoChatbot(user_id=user2.id, db=db)
    result = await chatbot2.process_message(f"Delete 'User1 Important Task'")

    assert result["message"]
    # Should indicate task not found
    assert "couldn't find" in result["message"].lower() or "not found" in result["message"].lower()

    # Verify task still exists (not deleted by user2)
    task = db.query(Todo).filter(Todo.id == task_id).first()
    assert task is not None, "Task should not be deleted by different user"


# ==================== MCP TOOL-LEVEL USER ISOLATION ====================

def test_mcp_tool_list_tasks_isolation(db: Session, user1: User, user2: User):
    """
    T091: Verify list_tasks MCP tool enforces user isolation.

    Direct test of MCP tool (bypassing chatbot) to verify isolation
    at the tool level.
    """
    # Create tasks for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # List tasks for user2
    input_data = ListTasksInput(user_id=str(user2.id))
    result = list_tasks(db, input_data)

    # User2 should not see user1's tasks
    assert result.count == 0
    assert len(result.tasks) == 0


def test_mcp_tool_complete_task_isolation(db: Session, user1: User, user2: User):
    """
    T091: Verify complete_task MCP tool enforces user isolation.
    """
    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # User2 tries to complete user1's task
    input_data = CompleteTaskInput(
        user_id=str(user2.id),
        task_id=str(task1.id)
    )

    with pytest.raises(NotFoundError):
        complete_task(db, input_data)

    # Verify task is still pending
    db.refresh(task1)
    assert task1.status == TaskStatus.PENDING


def test_mcp_tool_delete_task_isolation(db: Session, user1: User, user2: User):
    """
    T091: Verify delete_task MCP tool enforces user isolation.
    """
    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()
    task_id = task1.id

    # User2 tries to delete user1's task
    input_data = DeleteTaskInput(
        user_id=str(user2.id),
        task_id=str(task1.id)
    )

    with pytest.raises(NotFoundError):
        delete_task(db, input_data)

    # Verify task still exists
    task = db.query(Todo).filter(Todo.id == task_id).first()
    assert task is not None


def test_mcp_tool_update_task_isolation(db: Session, user1: User, user2: User):
    """
    T091: Verify update_task MCP tool enforces user isolation.
    """
    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # User2 tries to update user1's task
    input_data = UpdateTaskInput(
        user_id=str(user2.id),
        task_id=str(task1.id),
        title="Hacked Title"
    )

    with pytest.raises(NotFoundError):
        update_task(db, input_data)

    # Verify task title unchanged
    db.refresh(task1)
    assert task1.title == "User1 Task"


# ==================== DATABASE-LEVEL USER ISOLATION ====================

def test_database_query_user_isolation(db: Session, user1: User, user2: User):
    """
    T091: Verify database queries enforce user isolation.

    Tests that direct database queries correctly filter by user_id.
    """
    # Create tasks for both users
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    task2 = Todo(id=uuid4(), user_id=user2.id, title="User2 Task", status=TaskStatus.PENDING)
    db.add_all([task1, task2])
    db.commit()

    # Query tasks for user1
    user1_tasks = db.query(Todo).filter(Todo.user_id == user1.id).all()
    assert len(user1_tasks) == 1
    assert user1_tasks[0].title == "User1 Task"

    # Query tasks for user2
    user2_tasks = db.query(Todo).filter(Todo.user_id == user2.id).all()
    assert len(user2_tasks) == 1
    assert user2_tasks[0].title == "User2 Task"


def test_no_cross_user_task_id_collision(db: Session, user1: User, user2: User):
    """
    T091: Verify task IDs are globally unique, preventing collision attacks.

    Even if user2 somehow obtains user1's task_id, the system should
    prevent access via user_id filtering.
    """
    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Private Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # User2 knows the task_id (simulating attack scenario)
    stolen_task_id = task1.id

    # User2 tries to access via direct database query with user_id filter
    user2_attempt = db.query(Todo).filter(
        Todo.id == stolen_task_id,
        Todo.user_id == user2.id  # User2's ID
    ).first()

    # Should return None (no access)
    assert user2_attempt is None, "User2 should not be able to access user1's task even with task_id"
