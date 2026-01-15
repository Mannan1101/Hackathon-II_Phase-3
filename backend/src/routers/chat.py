"""
Chat API endpoint for Todo AI Chatbot.

This module provides the POST /api/chat endpoint for natural language todo management.
Users send text messages and receive conversational responses powered by AI.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID

from ..database import get_db
from ..middleware.auth import get_current_user
from ..middleware.rate_limit import check_chat_rate_limit
from ..models.user import User
from ..agent.chatbot import TodoChatbot
from ..config import get_logger

logger = get_logger("routers.chat")

router = APIRouter(prefix="/api", tags=["Chatbot"])


# ==================== REQUEST/RESPONSE SCHEMAS ====================

class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.

    Per contracts/chat-api.yaml specification.
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language message from user"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {"text": "Add a task to buy groceries"},
                {"text": "What are my tasks?"},
                {"text": "Mark 'buy groceries' as done"},
                {"text": "Delete the groceries task"},
                {"text": "Change my groceries task to 'buy groceries and milk'"},
                {"text": "How many tasks do I have?"}
            ]
        }


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.

    Per contracts/chat-api.yaml specification.
    """
    message: str = Field(..., description="Conversational response from chatbot")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata about request processing"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "message": "I've added 'buy groceries' to your tasks!",
                    "metadata": {
                        "intent": "add_task",
                        "tool_called": "add_task",
                        "success": True
                    }
                }
            ]
        }


# ==================== CHAT ENDPOINT ====================

@router.post("/chat", response_model=ChatResponse, status_code=200)
async def chat_endpoint(
    chat_request: ChatRequest,
    fastapi_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process natural language chat message.

    This endpoint:
    1. Authenticates user (via get_current_user dependency)
    2. Checks rate limit (30 requests per 60 seconds)
    3. Creates stateless chatbot instance for this request
    4. Processes message using Cohere AI + MCP tools
    5. Returns conversational response

    **Authentication**: Required (session cookie)

    **Rate Limiting**: 30 requests per 60 seconds per user

    **Performance**: Target <3s response time (SC-005)

    Args:
        chat_request: Chat request with user message (1-1000 characters)
        fastapi_request: FastAPI request object for rate limiting
        current_user: Authenticated user (from dependency)
        db: Database session (from dependency)

    Returns:
        ChatResponse: Conversational message and optional metadata

    Raises:
        HTTPException 400: Invalid request (validation error)
        HTTPException 401: Unauthorized (missing or invalid session)
        HTTPException 429: Too many requests (rate limit exceeded)
        HTTPException 500: Internal server error (Cohere API, database, etc.)
        HTTPException 503: Service unavailable (Cohere API down)

    Example:
        ```bash
        curl -X POST http://localhost:8000/api/chat \\
             -H "Content-Type: application/json" \\
             -H "Cookie: session_id=YOUR_SESSION_TOKEN" \\
             -d '{"text": "Add a task to buy groceries"}'
        ```

        Response:
        ```json
        {
            "message": "I've added 'buy groceries' to your tasks!",
            "metadata": {
                "intent": "add_task",
                "tool_called": "add_task",
                "success": true,
                "task_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
        ```
    """
    # Check rate limit first (raises HTTPException 429 if exceeded)
    await check_chat_rate_limit(fastapi_request, str(current_user.id))

    try:
        logger.info("Chat request received", extra={
            "user_id": str(current_user.id),
            "message_length": len(chat_request.text)
        })

        # Create stateless chatbot instance for this request
        # Per FR-003: Agent is completely stateless, no conversation history
        chatbot = TodoChatbot(user_id=current_user.id, db=db)

        # Process message
        result = await chatbot.process_message(chat_request.text)

        logger.info("Chat request processed successfully", extra={
            "user_id": str(current_user.id),
            "intent": result.get("metadata", {}).get("intent"),
            "success": True
        })

        return ChatResponse(
            message=result["message"],
            metadata=result.get("metadata", {})
        )

    except ValueError as e:
        # Configuration error (missing API key, etc.)
        logger.error(f"Configuration error: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e)
        })
        raise HTTPException(
            status_code=503,
            detail="The chatbot is temporarily unavailable. Please try again later."
        )

    except HTTPException:
        # Re-raise FastAPI HTTP exceptions (auth errors, etc.)
        raise

    except Exception as e:
        # Unexpected error - log details but return generic message to user
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", extra={
            "user_id": str(current_user.id),
            "error": str(e),
            "error_type": type(e).__name__
        })
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again in a moment."
        )


# ==================== HEALTH CHECK (Optional) ====================

@router.get("/chat/health", status_code=200)
async def chat_health_check() -> Dict[str, str]:
    """
    Health check for chatbot service.

    Verifies Cohere API configuration is present.
    Does not actually call Cohere API (that would be expensive).

    Returns:
        Dict: Status message
    """
    from ..config import settings

    if not settings.COHERE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service not configured (missing COHERE_API_KEY)"
        )

    return {
        "status": "ok",
        "service": "todo-ai-chatbot",
        "model": settings.CHATBOT_MODEL
    }
