"""
Authentication middleware and dependencies for FastAPI routes.

Provides get_current_user dependency for protecting routes that require authentication.
"""
from typing import Annotated
from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..models.user import User
from ..services.auth_service import AuthService


def get_current_user(
    session_id: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current authenticated user from session cookie.

    This dependency extracts the session_id cookie, validates it, and returns
    the authenticated user. Used in route handlers that require authentication.

    Args:
        session_id: Session token from cookie (automatically extracted by FastAPI)
        db: Database session dependency

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException 401: If session cookie is missing, invalid, or expired
        HTTPException 401: If user not found in database

    Usage:
        ```python
        @router.get("/protected")
        async def protected_route(
            current_user: User = Depends(get_current_user)
        ):
            return {"user_id": current_user.id}
        ```
    """
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to access this resource"
        )

    # Use AuthService to verify token and get user
    auth_service = AuthService(db)

    try:
        user = auth_service.get_current_user(session_id)
        return user
    except HTTPException:
        # Re-raise auth-related HTTPExceptions
        raise
    except Exception as e:
        # Log unexpected errors and return generic 401
        import logging
        logger = logging.getLogger("chatbot.auth")
        logger.error(f"Unexpected error in get_current_user: {str(e)}", extra={"error": str(e)})
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )


def get_user_id(
    current_user: User = Depends(get_current_user)
) -> UUID:
    """
    FastAPI dependency to get current user's ID.

    Convenience dependency that extracts just the user_id from the authenticated user.
    Useful for MCP tools and other services that only need the user ID.

    Args:
        current_user: Authenticated user (from get_current_user dependency)

    Returns:
        UUID: Current user's ID

    Usage:
        ```python
        @router.get("/my-resource")
        async def get_resource(
            user_id: UUID = Depends(get_user_id)
        ):
            return {"user_id": user_id}
        ```
    """
    return current_user.id
