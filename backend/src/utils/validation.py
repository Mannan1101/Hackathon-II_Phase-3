"""
Input validation utilities.

This module provides common validation functions for user input.
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email is valid, False otherwise

    Example:
        ```python
        is_valid = validate_email("user@example.com")
        ```
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets minimum strength requirements.

    Requirements:
    - Minimum 8 characters
    - Maximum 100 characters

    Args:
        password: Password to validate

    Returns:
        tuple: (is_valid, error_message)

    Example:
        ```python
        is_valid, error = validate_password_strength("SecurePass123")
        if not is_valid:
            raise ValueError(error)
        ```
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 100:
        return False, "Password must be at most 100 characters long"

    return True, None


def validate_todo_title(title: str) -> tuple[bool, Optional[str]]:
    """
    Validate todo title meets requirements.

    Requirements:
    - Not empty or whitespace only
    - Maximum 200 characters

    Args:
        title: Todo title to validate

    Returns:
        tuple: (is_valid, error_message)

    Example:
        ```python
        is_valid, error = validate_todo_title("Buy groceries")
        ```
    """
    # Check if title is empty or whitespace only
    if not title or not title.strip():
        return False, "Title cannot be empty or whitespace only"

    # Check length
    if len(title) > 200:
        return False, "Title must be at most 200 characters long"

    return True, None


def sanitize_string(value: str) -> str:
    """
    Sanitize string input by trimming whitespace.

    Args:
        value: String to sanitize

    Returns:
        str: Sanitized string

    Example:
        ```python
        clean = sanitize_string("  hello  ")  # Returns "hello"
        ```
    """
    return value.strip()
