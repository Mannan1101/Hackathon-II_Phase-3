"""
Quick verification script for Todo AI Chatbot setup.

This script tests that all components are properly configured and can be imported.
"""
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all chatbot modules can be imported."""
    print("Testing imports...")

    try:
        from src.routers.chat import router, ChatRequest, ChatResponse
        print("[OK] Chat router imported")
    except Exception as e:
        print(f"[FAIL] Failed to import chat router: {e}")
        return False

    try:
        from src.agent.chatbot import TodoChatbot
        print("[OK] TodoChatbot imported")
    except Exception as e:
        print(f"[FAIL] Failed to import TodoChatbot: {e}")
        return False

    try:
        from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task
        print("[OK] MCP tools imported")
    except Exception as e:
        print(f"[FAIL] Failed to import MCP tools: {e}")
        return False

    try:
        from src.mcp.schemas import (
            AddTaskInput, ListTasksInput, CompleteTaskInput,
            DeleteTaskInput, UpdateTaskInput
        )
        print("[OK] MCP schemas imported")
    except Exception as e:
        print(f"[FAIL] Failed to import MCP schemas: {e}")
        return False

    try:
        from src.utils.errors import (
            ValidationError, NotFoundError, DatabaseError,
            AgentError, MCPToolError
        )
        print("[OK] Error classes imported")
    except Exception as e:
        print(f"[FAIL] Failed to import error classes: {e}")
        return False

    try:
        from src.middleware.auth import get_current_user, get_user_id
        print("[OK] Auth middleware imported")
    except Exception as e:
        print(f"[FAIL] Failed to import auth middleware: {e}")
        return False

    return True


def test_config():
    """Test configuration settings."""
    print("\nTesting configuration...")

    try:
        from src.config import settings

        # Check chatbot settings
        if settings.CHATBOT_MODEL:
            print(f"[OK] Chatbot model: {settings.CHATBOT_MODEL}")
        else:
            print("[FAIL] Chatbot model not set")
            return False

        if settings.COHERE_API_KEY:
            print(f"[OK] Cohere API key configured (length: {len(settings.COHERE_API_KEY)})")
        else:
            print("[WARN] Cohere API key not set (required for production)")

        # Check database pooling
        print(f"[OK] DB pool size: {settings.DB_POOL_SIZE}")
        print(f"[OK] DB max overflow: {settings.DB_MAX_OVERFLOW}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to load configuration: {e}")
        return False


def test_database_model():
    """Test Todo model with new fields."""
    print("\nTesting Todo model...")

    try:
        from src.models.todo import Todo, TaskStatus

        # Check TaskStatus enum
        assert hasattr(TaskStatus, 'PENDING'), "TaskStatus.PENDING missing"
        assert hasattr(TaskStatus, 'COMPLETED'), "TaskStatus.COMPLETED missing"
        print("[OK] TaskStatus enum defined")

        # Check Todo model fields
        assert hasattr(Todo, 'description'), "Todo.description field missing"
        assert hasattr(Todo, 'status'), "Todo.status field missing"
        print("[OK] Todo model has description and status fields")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to verify Todo model: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Todo AI Chatbot Setup Verification")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database Model", test_database_model()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[FAIL]"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n[SUCCESS] All verification tests passed!")
        print("\nNext steps:")
        print("1. Set COHERE_API_KEY in .env file")
        print("2. Run: uvicorn src.main:app --reload --port 8000")
        print("3. Test endpoint: curl http://localhost:8000/api/chat/health")
        return 0
    else:
        print("\n[ERROR] Some verification tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
