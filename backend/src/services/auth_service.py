"""
Authentication service for user signup, signin, and session management.

This module provides business logic for user authentication operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Response
from datetime import datetime, timedelta
from jose import jwt, JWTError
from uuid import UUID
import secrets

from ..models.user import User
from ..schemas.auth import SignupRequest, SigninRequest, AuthResponse
from ..utils.password import hash_password, verify_password
from ..config import settings


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        """
        Initialize AuthService.

        Args:
            db: Database session
        """
        self.db = db

    def signup(self, request: SignupRequest) -> tuple[User, str]:
        """
        Create a new user account.

        Args:
            request: Signup request with email and password

        Returns:
            tuple: (Created user, session token)

        Raises:
            HTTPException: 409 if email already exists
            HTTPException: 500 if database error occurs
        """
        # Hash password
        hashed_pwd = hash_password(request.password)

        # Create user
        user = User(
            email=request.email.lower(),  # Normalize email to lowercase
            hashed_password=hashed_pwd,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409, detail="An account with this email already exists"
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred. Please try again later."
            )

        # Create session token
        session_token = self._create_session_token(user.id)

        return user, session_token

    def signin(self, request: SigninRequest) -> tuple[User, str]:
        """
        Sign in existing user.

        Args:
            request: Signin request with email and password

        Returns:
            tuple: (User, session token)

        Raises:
            HTTPException: 401 if credentials are invalid
        """
        # Find user by email
        user = (
            self.db.query(User)
            .filter(User.email == request.email.lower())
            .first()
        )

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create session token
        session_token = self._create_session_token(user.id)

        return user, session_token

    def _create_session_token(self, user_id: UUID) -> str:
        """
        Create JWT session token.

        Args:
            user_id: User ID to encode in token

        Returns:
            str: JWT session token
        """
        # Set expiration (7 days as per config)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Create JWT payload
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),  # Unique token ID
        }

        # Encode JWT
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return token

    def set_session_cookie(self, response: Response, token: str) -> None:
        """
        Set session cookie with security flags.

        Cookie configuration:
        - HttpOnly: Prevents JavaScript access (XSS protection)
        - Secure: HTTPS only in production
        - SameSite=Lax: CSRF protection
        - Max-Age: 7 days (604800 seconds)

        Args:
            response: FastAPI response object
            token: Session token to set in cookie
        """
        response.set_cookie(
            key="session_id",
            value=token,
            httponly=True,  # Prevent JavaScript access
            secure=settings.APP_ENV == "production",  # HTTPS only in production
            samesite="lax",  # CSRF protection
            max_age=604800,  # 7 days in seconds
            path="/",
        )

    def verify_session_token(self, token: str) -> UUID:
        """
        Verify and decode session token.

        Args:
            token: JWT session token

        Returns:
            UUID: User ID from token

        Raises:
            HTTPException: 401 if token is invalid or expired
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=401, detail="Invalid authentication credentials"
                )

            return UUID(user_id)

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    def get_current_user(self, token: str) -> User:
        """
        Get current user from session token.

        Args:
            token: JWT session token

        Returns:
            User: Current authenticated user

        Raises:
            HTTPException: 401 if token is invalid or user not found
        """
        user_id = self.verify_session_token(token)

        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
