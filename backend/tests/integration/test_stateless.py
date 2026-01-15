"""
Test for stateless chatbot behavior (T089).

Verifies that the chatbot agent is completely stateless and does not
retain conversation context between requests (FR-003).
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from src.agent.chatbot import TodoChatbot
from src.models.user import User
from src.models.todo import Todo, TaskStatus


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


@pytest.mark.asyncio
async def test_stateless_no_context_retention(db: Session, test_user: User):
    """
    T089: Verify chatbot doesn't retain context between requests.

    Sends two sequential requests and verifies that the second request
    does not have access to context from the first request.
    """
    chatbot = TodoChatbot(user_id=test_user.id, db=db)

    # First request: Add a task
    result1 = await chatbot.process_message("Add a task to buy milk")
    assert result1["message"]
    assert result1.get("metadata", {}).get("intent") == "add_task"

    # Second request: Try to reference "that task" from first request
    result2 = await chatbot.process_message("Delete that task")

    # Chatbot should NOT remember "that task" from the first request
    # It should either:
    # 1. Ask for clarification about which task
    # 2. Return an error about not finding "that task"
    # 3. Respond with confusion

    assert result2["message"]

    # The key test: verify it didn't successfully delete the task by
    # remembering context. Check that the milk task still exists.
    tasks = db.query(Todo).filter(
        Todo.user_id == test_user.id,
        Todo.title.ilike("%milk%")
    ).all()

    # Task should still exist (wasn't deleted by context-aware deletion)
    assert len(tasks) > 0, "Chatbot incorrectly retained context and deleted the task"


@pytest.mark.asyncio
async def test_stateless_multiple_instances(db: Session, test_user: User):
    """
    T089: Verify multiple chatbot instances don't share state.

    Creates two separate chatbot instances and verifies they don't
    interfere with each other.
    """
    # Create first chatbot instance
    chatbot1 = TodoChatbot(user_id=test_user.id, db=db)
    result1 = await chatbot1.process_message("Add a task to test isolation")

    assert result1["message"]

    # Create second chatbot instance (simulating new request)
    chatbot2 = TodoChatbot(user_id=test_user.id, db=db)
    result2 = await chatbot2.process_message("What are my tasks?")

    assert result2["message"]

    # Verify both instances worked correctly but independently
    # Check that task from first instance is visible to second instance
    # (via database, not via memory)
    tasks = db.query(Todo).filter(
        Todo.user_id == test_user.id,
        Todo.title.ilike("%test isolation%")
    ).all()

    assert len(tasks) > 0, "Task should be visible via database"


@pytest.mark.asyncio
async def test_stateless_no_conversation_history(db: Session, test_user: User):
    """
    T089: Verify chatbot has no conversation history storage.

    Per FR-003, the agent should be completely stateless with no
    conversation history between requests.
    """
    chatbot = TodoChatbot(user_id=test_user.id, db=db)

    # Send multiple messages
    messages = [
        "Add a task to buy apples",
        "Add a task to buy oranges",
        "Add a task to buy bananas"
    ]

    for msg in messages:
        result = await chatbot.process_message(msg)
        assert result["message"]

    # Verify chatbot instance has no stored conversation history
    # Check that chatbot doesn't have attributes like 'history', 'messages', 'context'
    chatbot_dict = vars(chatbot)

    # These attributes should NOT exist or should be None/empty
    history_attrs = ['history', 'messages', 'conversation', 'context', 'memory']
    for attr in history_attrs:
        if attr in chatbot_dict:
            value = chatbot_dict[attr]
            assert value is None or value == [] or value == {}, \
                f"Chatbot should not store {attr}, but found: {value}"


@pytest.mark.asyncio
async def test_stateless_database_only_persistence(db: Session, test_user: User):
    """
    T089: Verify state persistence is only through database, not memory.

    All state changes should be persisted to the database, and subsequent
    requests should retrieve state from the database, not from memory.
    """
    # First request: Add a task
    chatbot1 = TodoChatbot(user_id=test_user.id, db=db)
    result1 = await chatbot1.process_message("Add a task to test persistence")
    assert result1["message"]

    # Delete first chatbot instance (simulating end of request)
    del chatbot1

    # Second request: List tasks (new chatbot instance, should read from DB)
    chatbot2 = TodoChatbot(user_id=test_user.id, db=db)
    result2 = await chatbot2.process_message("What are my tasks?")

    assert result2["message"]
    # Should see the task from the first request (via database)
    assert "test persistence" in result2["message"].lower() or "1" in result2["message"]

    # Verify task exists in database
    tasks = db.query(Todo).filter(
        Todo.user_id == test_user.id,
        Todo.title.ilike("%test persistence%")
    ).all()

    assert len(tasks) > 0, "Task should persist in database across chatbot instances"
