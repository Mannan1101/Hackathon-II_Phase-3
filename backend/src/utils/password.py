"""
Password hashing and verification utilities.

This module provides bcrypt-based password hashing with minimum 12 rounds
as required by the constitution.
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 rounds (minimum per constitution).

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password as a string

    Example:
        ```python
        hashed = hash_password("SecurePass123")
        ```
    """
    # Convert password to bytes
    password_bytes = password.encode("utf-8")

    # Generate salt with 12 rounds (constitution requirement)
    salt = bcrypt.gensalt(rounds=12)

    # Hash password
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        ```python
        is_valid = verify_password("SecurePass123", stored_hash)
        ```
    """
    # Convert inputs to bytes
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # Verify password
    return bcrypt.checkpw(plain_bytes, hashed_bytes)
