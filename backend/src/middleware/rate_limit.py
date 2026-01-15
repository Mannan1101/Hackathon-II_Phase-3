"""
Rate limiting middleware for chatbot endpoints.

Implements simple in-memory rate limiting to prevent abuse.
For production, consider using Redis-based rate limiting.
"""
from fastapi import HTTPException, Request
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import threading

from ..config import get_logger

logger = get_logger("middleware.rate_limit")


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Tracks requests per user (by user_id) and enforces limits.
    For production with multiple servers, use Redis-based implementation.
    """

    def __init__(
        self,
        max_requests: int = 30,
        window_seconds: int = 60
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        # Track requests: {user_id: [(timestamp, count), ...]}
        self.requests: Dict[str, list[Tuple[datetime, int]]] = defaultdict(list)

        # Lock for thread safety
        self.lock = threading.Lock()

    def check_rate_limit(self, user_id: str) -> Tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User ID to check

        Returns:
            Tuple of (allowed, requests_made, requests_remaining)
        """
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.window_seconds)

            # Clean old requests
            self.requests[user_id] = [
                (ts, count) for ts, count in self.requests[user_id]
                if ts > cutoff
            ]

            # Count requests in current window
            total_requests = sum(count for _, count in self.requests[user_id])

            if total_requests >= self.max_requests:
                # Rate limit exceeded
                remaining = 0
                allowed = False
                logger.warning(f"Rate limit exceeded for user {user_id}", extra={
                    "user_id": user_id,
                    "requests_made": total_requests,
                    "max_requests": self.max_requests
                })
            else:
                # Allow request and increment counter
                self.requests[user_id].append((now, 1))
                remaining = self.max_requests - total_requests - 1
                allowed = True

            return allowed, total_requests, remaining

    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limit for a specific user.

        Args:
            user_id: User ID to reset
        """
        with self.lock:
            self.requests[user_id] = []

    def get_reset_time(self, user_id: str) -> int:
        """
        Get seconds until rate limit resets for user.

        Args:
            user_id: User ID to check

        Returns:
            int: Seconds until oldest request expires
        """
        with self.lock:
            if not self.requests[user_id]:
                return 0

            oldest_request = min(ts for ts, _ in self.requests[user_id])
            reset_time = oldest_request + timedelta(seconds=self.window_seconds)
            seconds_remaining = max(0, int((reset_time - datetime.utcnow()).total_seconds()))

            return seconds_remaining


# Global rate limiter instance
# Configuration: 30 requests per 60 seconds (30 req/min)
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)


async def check_chat_rate_limit(request: Request, user_id: str) -> None:
    """
    FastAPI dependency to check rate limit for chat endpoint.

    Args:
        request: FastAPI request object
        user_id: User ID from authentication

    Raises:
        HTTPException 429: If rate limit exceeded

    Usage:
        ```python
        @router.post("/chat")
        async def chat(
            user_id: str = Depends(get_user_id),
            _: None = Depends(check_chat_rate_limit)
        ):
            ...
        ```
    """
    allowed, requests_made, remaining = rate_limiter.check_rate_limit(user_id)

    # Add rate limit headers to response
    if hasattr(request.state, "rate_limit_info"):
        request.state.rate_limit_info = {
            "limit": rate_limiter.max_requests,
            "remaining": remaining,
            "reset": rate_limiter.get_reset_time(user_id)
        }

    if not allowed:
        reset_seconds = rate_limiter.get_reset_time(user_id)
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Please wait {reset_seconds} seconds and try again.",
            headers={
                "Retry-After": str(reset_seconds),
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_seconds)
            }
        )

    logger.info(f"Rate limit check passed", extra={
        "user_id": user_id,
        "requests_made": requests_made + 1,
        "remaining": remaining
    })
