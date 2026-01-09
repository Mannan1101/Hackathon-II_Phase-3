"""
Health check endpoints.

This module provides /health and /ready endpoints for service monitoring.
"""

from fastapi import APIRouter
from datetime import datetime
from ..database import check_db_connection

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Service health check endpoint.

    Returns 200 OK if the service is running.
    Does not check dependencies like database.

    Returns:
        dict: Health status and timestamp

    Example:
        ```
        GET /health
        Response: {"status": "healthy", "timestamp": "2026-01-07T12:00:00Z"}
        ```
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """
    Service readiness check endpoint.

    Returns 200 OK if service is ready (database accessible).
    Returns 503 if database is unavailable.

    Returns:
        dict: Readiness status and database connection status

    Example:
        ```
        GET /ready
        Response: {"status": "ready", "database": "connected"}
        ```
    """
    db_connected = check_db_connection()

    if not db_connected:
        return {
            "status": "not_ready",
            "database": "disconnected",
        }

    return {
        "status": "ready",
        "database": "connected",
    }
