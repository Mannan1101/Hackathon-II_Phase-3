"""
Authentication endpoints.

This module provides /auth/signup and /auth/signin endpoints.
"""

from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import SignupRequest, SigninRequest, AuthResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=201, response_model=AuthResponse)
async def signup(
    request: SignupRequest, response: Response, db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Create new user account.

    Registers a new user with email and password. Returns user data and sets
    session cookie in response headers.

    Args:
        request: Signup request with email and password
        response: FastAPI response object (for setting cookie)
        db: Database session

    Returns:
        AuthResponse: User data (id, email, created_at)

    Raises:
        HTTPException 400: Validation error (invalid email, password too short)
        HTTPException 409: Email already registered
        HTTPException 500: Internal server error

    Example:
        ```
        POST /auth/signup
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }

        Response:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "created_at": "2026-01-07T12:00:00Z"
        }
        ```
    """
    auth_service = AuthService(db)

    try:
        # Create user and get session token
        user, session_token = auth_service.signup(request)

        # Set session cookie
        auth_service.set_session_cookie(response, session_token)

        # Return user data (without password)
        return AuthResponse(
            id=user.id, email=user.email, created_at=user.created_at
        )

    except HTTPException:
        # Re-raise HTTPExceptions from service
        raise
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.post("/signin", status_code=200, response_model=AuthResponse)
async def signin(
    request: SigninRequest, response: Response, db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Sign in to existing account.

    Authenticates user with email and password. Returns user data and sets
    session cookie in response headers.

    Args:
        request: Signin request with email and password
        response: FastAPI response object (for setting cookie)
        db: Database session

    Returns:
        AuthResponse: User data (id, email, created_at)

    Raises:
        HTTPException 400: Validation error (invalid email format)
        HTTPException 401: Invalid email or password
        HTTPException 500: Internal server error

    Example:
        ```
        POST /auth/signin
        {
            "email": "user@example.com",
            "password": "SecurePass123"
        }

        Response:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "created_at": "2026-01-07T12:00:00Z"
        }
        ```
    """
    auth_service = AuthService(db)

    try:
        # Sign in user and get session token
        user, session_token = auth_service.signin(request)

        # Set session cookie
        auth_service.set_session_cookie(response, session_token)

        # Return user data (without password)
        return AuthResponse(
            id=user.id, email=user.email, created_at=user.created_at
        )

    except HTTPException:
        # Re-raise HTTPExceptions from service
        raise
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )
