"""
Authentication middleware for session validation.

This middleware validates session cookies and extracts user information.
"""

from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ..database import get_db
from ..services.auth_service import AuthService
from ..models.user import User


def get_session_token(request: Request) -> Optional[str]:
    """
    Extract session token from cookie.

    Args:
        request: FastAPI request object

    Returns:
        Optional[str]: Session token if present, None otherwise
    """
    return request.cookies.get("session_id")


def require_auth(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """
    Dependency to require authentication.

    Validates session token and returns current user.
    Use this as a dependency in protected routes.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException 401: If session token is missing or invalid

    Example:
        ```python
        @router.get("/todos")
        async def get_todos(current_user: User = Depends(require_auth)):
            # current_user is the authenticated user
            return {"user_id": current_user.id}
        ```
    """
    token = get_session_token(request)

    if not token:
        raise HTTPException(
            status_code=401, detail="Authentication required. Please sign in."
        )

    auth_service = AuthService(db)

    try:
        user = auth_service.get_current_user(token)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


def optional_auth(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Dependency for optional authentication.

    Returns user if authenticated, None otherwise.
    Use this for routes that work with or without authentication.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Optional[User]: Current user if authenticated, None otherwise

    Example:
        ```python
        @router.get("/public")
        async def public_endpoint(current_user: Optional[User] = Depends(optional_auth)):
            if current_user:
                return {"message": f"Hello {current_user.email}"}
            return {"message": "Hello guest"}
        ```
    """
    token = get_session_token(request)

    if not token:
        return None

    auth_service = AuthService(db)

    try:
        user = auth_service.get_current_user(token)
        return user
    except Exception:
        return None
