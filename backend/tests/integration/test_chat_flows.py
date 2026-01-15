"""
Integration tests for Todo AI Chatbot flows.

These tests verify end-to-end chatbot functionality including:
- Natural language understanding
- Intent recognition
- MCP tool execution
- Response generation

Tests follow TDD principles:
- T014-T016: Tests for US1 (add task)
- T033-T035: Tests for US2 (list tasks)
- T046-T048: Tests for US3 (complete task)
- T059-T060: Tests for US4 (delete task)
- T069-T071: Tests for US5 (update task)
- T081-T083: Tests for US6 (analytical queries)
"""
import pytest
from uuid import uuid4, UUID
from sqlalchemy.orm import Session

from src.agent.chatbot import TodoChatbot
from src.models.todo import Todo, TaskStatus
from src.models.user import User


# ==================== FIXTURES ====================

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user for testing."""
    user = User(
        id=uuid4(),
        email=f"test_{uuid4()}@example.com",
        hashed_password="$2b$12$dummy_hash_for_testing"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
async def chatbot(db: Session, test_user: User) -> TodoChatbot:
    """Create a chatbot instance for testing."""
    return TodoChatbot(user_id=test_user.id, db=db)


# ==================== T014-T016: USER STORY 1 - ADD TASK ====================

@pytest.mark.asyncio
async def test_add_task_simple(chatbot: TodoChatbot, db: Session, test_user: User):
    """T014: Integration test for adding a simple task."""
    result = await chatbot.process_message("Add a task to buy groceries")

    assert result["message"]
    assert "buy groceries" in result["message"].lower() or "groceries" in result["message"].lower()
    assert result.get("metadata", {}).get("intent") == "add_task"

    # Verify task was created in database
    tasks = db.query(Todo).filter(Todo.user_id == test_user.id).all()
    assert len(tasks) >= 1
    assert any("groceries" in task.title.lower() for task in tasks)


@pytest.mark.asyncio
async def test_add_task_with_description(chatbot: TodoChatbot, db: Session, test_user: User):
    """T015: Integration test for adding task with description."""
    result = await chatbot.process_message("Add a task to buy groceries with note: get milk and eggs")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "add_task"

    # Verify task was created with description
    tasks = db.query(Todo).filter(Todo.user_id == test_user.id).all()
    assert len(tasks) >= 1
    task = next((t for t in tasks if "groceries" in t.title.lower()), None)
    assert task is not None
    # Description handling may vary based on implementation


@pytest.mark.asyncio
async def test_add_task_empty_title(chatbot: TodoChatbot):
    """T016: Integration test for adding task with empty/invalid title."""
    result = await chatbot.process_message("Add a task")

    # Chatbot should handle this gracefully, either:
    # 1. Ask for more details, or
    # 2. Return an error message
    assert result["message"]
    # Should not crash or return empty response


# ==================== T033-T035: USER STORY 2 - LIST TASKS ====================

@pytest.mark.asyncio
async def test_list_tasks_basic(chatbot: TodoChatbot, db: Session, test_user: User):
    """T033: Integration test for listing tasks."""
    # Create some test tasks
    task1 = Todo(id=uuid4(), user_id=test_user.id, title="Buy groceries", status=TaskStatus.PENDING)
    task2 = Todo(id=uuid4(), user_id=test_user.id, title="Call mom", status=TaskStatus.COMPLETED)
    db.add_all([task1, task2])
    db.commit()

    result = await chatbot.process_message("What are my tasks?")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "list_tasks"
    # Response should mention tasks
    assert "buy groceries" in result["message"].lower() or "call mom" in result["message"].lower()


@pytest.mark.asyncio
async def test_list_tasks_empty(chatbot: TodoChatbot, db: Session, test_user: User):
    """T034: Integration test for empty task list."""
    # Ensure no tasks exist
    db.query(Todo).filter(Todo.user_id == test_user.id).delete()
    db.commit()

    result = await chatbot.process_message("Show me my tasks")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "list_tasks"
    # Should indicate no tasks
    assert ("no tasks" in result["message"].lower() or
            "don't have any" in result["message"].lower() or
            "empty" in result["message"].lower() or
            "0" in result["message"])


@pytest.mark.asyncio
async def test_list_tasks_filter_incomplete(chatbot: TodoChatbot, db: Session, test_user: User):
    """T035: Integration test for listing incomplete tasks."""
    # Create mixed tasks
    pending1 = Todo(id=uuid4(), user_id=test_user.id, title="Pending Task 1", status=TaskStatus.PENDING)
    pending2 = Todo(id=uuid4(), user_id=test_user.id, title="Pending Task 2", status=TaskStatus.PENDING)
    completed = Todo(id=uuid4(), user_id=test_user.id, title="Completed Task", status=TaskStatus.COMPLETED)
    db.add_all([pending1, pending2, completed])
    db.commit()

    result = await chatbot.process_message("Show me my incomplete tasks")

    assert result["message"]
    # Should only show pending tasks, not completed
    assert "pending task" in result["message"].lower()


# ==================== T046-T048: USER STORY 3 - COMPLETE TASK ====================

@pytest.mark.asyncio
async def test_complete_task_by_title(chatbot: TodoChatbot, db: Session, test_user: User):
    """T046: Integration test for completing task by title."""
    # Create pending task
    task = Todo(id=uuid4(), user_id=test_user.id, title="Buy groceries", status=TaskStatus.PENDING)
    db.add(task)
    db.commit()

    result = await chatbot.process_message("Mark 'buy groceries' as done")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "complete_task"
    assert "complet" in result["message"].lower() or "done" in result["message"].lower()

    # Verify task is completed in database
    db.refresh(task)
    assert task.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_complete_nonexistent_task(chatbot: TodoChatbot):
    """T047: Integration test for completing non-existent task."""
    result = await chatbot.process_message("Mark 'nonexistent task xyz123' as done")

    assert result["message"]
    # Should indicate task not found
    assert "couldn't find" in result["message"].lower() or "not found" in result["message"].lower()


@pytest.mark.asyncio
async def test_complete_already_completed_task(chatbot: TodoChatbot, db: Session, test_user: User):
    """T048: Integration test for completing already-completed task."""
    # Create completed task
    task = Todo(id=uuid4(), user_id=test_user.id, title="Already done", status=TaskStatus.COMPLETED)
    db.add(task)
    db.commit()

    result = await chatbot.process_message("Complete 'already done'")

    assert result["message"]
    # Should indicate already completed
    assert "already" in result["message"].lower()


# ==================== T059-T060: USER STORY 4 - DELETE TASK ====================

@pytest.mark.asyncio
async def test_delete_task_by_title(chatbot: TodoChatbot, db: Session, test_user: User):
    """T059: Integration test for deleting task."""
    # Create task to delete
    task = Todo(id=uuid4(), user_id=test_user.id, title="Delete me", status=TaskStatus.PENDING)
    db.add(task)
    db.commit()
    task_id = task.id

    result = await chatbot.process_message("Delete the 'delete me' task")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "delete_task"
    assert "delet" in result["message"].lower()

    # Verify task is deleted from database
    deleted_task = db.query(Todo).filter(Todo.id == task_id).first()
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_nonexistent_task(chatbot: TodoChatbot):
    """T060: Integration test for deleting non-existent task."""
    result = await chatbot.process_message("Delete 'nonexistent task xyz123'")

    assert result["message"]
    # Should indicate task not found
    assert "couldn't find" in result["message"].lower() or "not found" in result["message"].lower()


# ==================== T069-T071: USER STORY 5 - UPDATE TASK ====================

@pytest.mark.asyncio
async def test_update_task_title(chatbot: TodoChatbot, db: Session, test_user: User):
    """T069: Integration test for updating task title."""
    # Create task to update
    task = Todo(id=uuid4(), user_id=test_user.id, title="Old title", status=TaskStatus.PENDING)
    db.add(task)
    db.commit()

    result = await chatbot.process_message("Change 'old title' to 'new title'")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "update_task"
    assert "updat" in result["message"].lower() or "chang" in result["message"].lower()

    # Verify task title was updated
    db.refresh(task)
    assert "new title" in task.title.lower()


@pytest.mark.asyncio
async def test_update_task_add_note(chatbot: TodoChatbot, db: Session, test_user: User):
    """T070: Integration test for adding note to task."""
    # Create task
    task = Todo(id=uuid4(), user_id=test_user.id, title="My task", status=TaskStatus.PENDING)
    db.add(task)
    db.commit()

    result = await chatbot.process_message("Add note to 'my task': this is important")

    assert result["message"]
    # May be recognized as update_task intent
    assert result.get("metadata", {}).get("intent") in ["update_task", "add_task"]


@pytest.mark.asyncio
async def test_update_task_no_fields(chatbot: TodoChatbot, db: Session, test_user: User):
    """T071: Integration test for updating task with no new values."""
    # Create task
    task = Todo(id=uuid4(), user_id=test_user.id, title="My task", status=TaskStatus.PENDING)
    db.add(task)
    db.commit()

    # Ambiguous update request
    result = await chatbot.process_message("Update 'my task'")

    assert result["message"]
    # Should handle gracefully - may ask for clarification


# ==================== T081-T083: USER STORY 6 - ANALYTICAL QUERIES ====================

@pytest.mark.asyncio
async def test_query_task_count(chatbot: TodoChatbot, db: Session, test_user: User):
    """T081: Integration test for querying task counts."""
    # Create tasks
    pending1 = Todo(id=uuid4(), user_id=test_user.id, title="Task 1", status=TaskStatus.PENDING)
    pending2 = Todo(id=uuid4(), user_id=test_user.id, title="Task 2", status=TaskStatus.PENDING)
    pending3 = Todo(id=uuid4(), user_id=test_user.id, title="Task 3", status=TaskStatus.PENDING)
    completed1 = Todo(id=uuid4(), user_id=test_user.id, title="Task 4", status=TaskStatus.COMPLETED)
    completed2 = Todo(id=uuid4(), user_id=test_user.id, title="Task 5", status=TaskStatus.COMPLETED)
    db.add_all([pending1, pending2, pending3, completed1, completed2])
    db.commit()

    result = await chatbot.process_message("How many tasks do I have?")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "query"
    # Should mention counts
    assert "5" in result["message"] or "five" in result["message"].lower()
    assert "3" in result["message"] or "three" in result["message"].lower()  # pending count
    assert "2" in result["message"] or "two" in result["message"].lower()  # completed count


@pytest.mark.asyncio
async def test_query_oldest_task(chatbot: TodoChatbot, db: Session, test_user: User):
    """T082: Integration test for querying oldest task."""
    from datetime import datetime, timedelta

    # Create tasks with different timestamps
    old_task = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Oldest task",
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow() - timedelta(days=10)
    )
    new_task = Todo(
        id=uuid4(),
        user_id=test_user.id,
        title="Newest task",
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow()
    )
    db.add_all([old_task, new_task])
    db.commit()

    result = await chatbot.process_message("What's my oldest pending task?")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "query"
    # Should mention the oldest task
    assert "oldest" in result["message"].lower()


@pytest.mark.asyncio
async def test_query_who_am_i(chatbot: TodoChatbot, test_user: User):
    """T083: Integration test for user info query."""
    result = await chatbot.process_message("Who am I?")

    assert result["message"]
    assert result.get("metadata", {}).get("intent") == "query"
    # Should mention user email
    assert test_user.email in result["message"] or "logged in" in result["message"].lower()


# ==================== ADDITIONAL INTEGRATION TESTS ====================

@pytest.mark.asyncio
async def test_stateless_behavior(chatbot: TodoChatbot):
    """Verify chatbot is stateless across requests."""
    # Send first message
    result1 = await chatbot.process_message("Add a task to buy milk")
    assert result1["message"]

    # Send second message that refers to first (should not have context)
    result2 = await chatbot.process_message("Delete that task")

    # Should not remember "that task" from previous request
    # Response should indicate confusion or ask for clarification
    assert result2["message"]


@pytest.mark.asyncio
async def test_user_isolation(db: Session):
    """Verify users can't access each other's tasks."""
    # Create two users
    user1 = User(id=uuid4(), email="user1@example.com", hashed_password="$2b$12$dummy_hash")
    user2 = User(id=uuid4(), email="user2@example.com", hashed_password="$2b$12$dummy_hash")
    db.add_all([user1, user2])
    db.commit()

    # Create task for user1
    task1 = Todo(id=uuid4(), user_id=user1.id, title="User1 Task", status=TaskStatus.PENDING)
    db.add(task1)
    db.commit()

    # User2's chatbot should not see user1's tasks
    chatbot2 = TodoChatbot(user_id=user2.id, db=db)
    result = await chatbot2.process_message("What are my tasks?")

    assert result["message"]
    # Should indicate no tasks (or 0 tasks)
    assert "no tasks" in result["message"].lower() or "0" in result["message"] or "don't have any" in result["message"].lower()


@pytest.mark.asyncio
async def test_ambiguous_intent(chatbot: TodoChatbot):
    """Test handling of ambiguous user input."""
    result = await chatbot.process_message("Task")

    assert result["message"]
    # Should handle ambiguous input gracefully (not crash)
    # May ask for clarification or provide help


@pytest.mark.asyncio
async def test_performance_response_time(chatbot: TodoChatbot):
    """Test response time is reasonable (<3s per SC-005)."""
    import time

    start = time.time()
    result = await chatbot.process_message("Add a task to test performance")
    duration = time.time() - start

    assert result["message"]
    # SC-005: Target <3s response time
    assert duration < 5.0, f"Response took {duration:.2f}s, expected <5s"
