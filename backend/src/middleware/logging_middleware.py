"""
Logging middleware for request/response logging.

This module provides structured JSON logging for all HTTP requests and responses.
"""

import time
import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses in JSON format.

    Logs include:
    - Request method, path, and client IP
    - Response status code
    - Request duration
    - Timestamp
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response: HTTP response
        """
        # Record start time
        start_time = time.time()

        # Extract request details
        request_details = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request/response
        log_data = {
            **request_details,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        }

        # Log as JSON
        logger.info(json.dumps(log_data))

        return response
