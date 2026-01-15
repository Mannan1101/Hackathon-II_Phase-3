"""
Error handling utilities for Todo AI Chatbot.

Provides user-friendly error messages per FR-010 (no technical jargon, no stack traces).
All exceptions include context for logging but display friendly messages to users.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException


class ChatbotError(Exception):
    """
    Base exception for chatbot operations.

    All chatbot errors should inherit from this class to enable consistent
    error handling and logging.
    """
    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize chatbot error.

        Args:
            message: Technical error message for logging
            user_message: User-friendly message to display (defaults to message)
            context: Additional context for logging (user_id, task_id, etc.)
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message
        self.context = context or {}


class ValidationError(ChatbotError):
    """
    Input validation error.

    Raised when user input doesn't meet requirements (e.g., title too long,
    missing required fields, invalid format).

    User-friendly message format: "Title must be between 1 and 200 characters"
    """
    pass


class NotFoundError(ChatbotError):
    """
    Resource not found error.

    Raised when a requested task doesn't exist or doesn't belong to the user.

    User-friendly message format: "I couldn't find that task. Would you like to see your current tasks?"
    """
    pass


class ForbiddenError(ChatbotError):
    """
    Authorization error (user trying to access someone else's task).

    Raised when user attempts to access or modify a task they don't own.
    Per FR-008, this should rarely occur due to user_id filtering.

    User-friendly message format: "You don't have permission to access that task."
    """
    pass


class DatabaseError(ChatbotError):
    """
    Database operation error.

    Raised when database operations fail (connection issues, constraint violations, etc.).

    User-friendly message format: "Something went wrong while saving your task. Please try again in a moment."
    """
    pass


class AgentError(ChatbotError):
    """
    AI agent error (Cohere API failure, tool calling issues, etc.).

    Raised when the Cohere API or OpenAI Agents SDK encounters an error.

    User-friendly message format: "Sorry, I couldn't understand that. Please try again."
    """
    pass


class MCPToolError(ChatbotError):
    """
    MCP tool execution error.

    Raised when an MCP tool fails to execute properly (validation, database, etc.).

    User-friendly message format varies by tool and failure reason.
    """
    pass


# ==================== ERROR RESPONSE HELPERS ====================

def to_http_exception(error: ChatbotError, status_code: int = 500) -> HTTPException:
    """
    Convert ChatbotError to FastAPI HTTPException.

    Args:
        error: Chatbot error instance
        status_code: HTTP status code (default 500)

    Returns:
        HTTPException: FastAPI exception with user-friendly detail
    """
    return HTTPException(
        status_code=status_code,
        detail=error.user_message
    )


def validation_error_response(field: str, requirement: str) -> str:
    """
    Generate user-friendly validation error message.

    Args:
        field: Field name (e.g., "Title", "Description")
        requirement: Requirement description (e.g., "must be between 1 and 200 characters")

    Returns:
        str: User-friendly validation error message
    """
    return f"{field} {requirement}"


def not_found_error_response(resource_type: str = "task") -> str:
    """
    Generate user-friendly not found error message.

    Args:
        resource_type: Type of resource (default "task")

    Returns:
        str: User-friendly not found message with suggestion
    """
    return f"I couldn't find that {resource_type}. Would you like to see your current tasks?"


def database_error_response(operation: str = "saving") -> str:
    """
    Generate user-friendly database error message.

    Args:
        operation: Operation that failed (e.g., "saving", "updating", "deleting")

    Returns:
        str: User-friendly database error message
    """
    return f"Something went wrong while {operation} your task. Please try again in a moment."


def agent_error_response() -> str:
    """
    Generate user-friendly agent error message.

    Returns:
        str: Generic agent error message
    """
    return "Sorry, I couldn't understand that. Please try again."


# ==================== ERROR CONTEXT HELPERS ====================

def add_user_context(error: ChatbotError, user_id: str) -> ChatbotError:
    """
    Add user_id to error context for logging.

    Args:
        error: Chatbot error instance
        user_id: User ID to add to context

    Returns:
        ChatbotError: Same error with updated context
    """
    error.context["user_id"] = user_id
    return error


def add_task_context(error: ChatbotError, task_id: str) -> ChatbotError:
    """
    Add task_id to error context for logging.

    Args:
        error: Chatbot error instance
        task_id: Task ID to add to context

    Returns:
        ChatbotError: Same error with updated context
    """
    error.context["task_id"] = task_id
    return error
