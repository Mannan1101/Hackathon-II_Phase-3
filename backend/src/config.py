"""
Application configuration management.

This module loads and validates environment variables using Pydantic settings.

Updated for Feature 001-todo-ai-chatbot: Added logging and database pooling config.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import sys

# Load .env file first to ensure correct environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"[Config] Loaded .env from: {env_path}")
    print(f"[Config] DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:60]}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/todo_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Better Auth (Optional)
    BETTER_AUTH_API_KEY: str | None = None
    BETTER_AUTH_SECRET: str | None = None

    # AI Chatbot Configuration (Feature: 001-todo-ai-chatbot)
    COHERE_API_KEY: str | None = None
    CHATBOT_MODEL: str = "command-r-plus"  # Note: command-r deprecated Sept 2025
    CHATBOT_MAX_TOKENS: int = 500
    CHATBOT_TEMPERATURE: float = 0.7

    # Application Configuration
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Pooling Configuration (Feature: 001-todo-ai-chatbot)
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600  # 1 hour

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration instance
    """
    return Settings()


# Global settings instance
settings = get_settings()


# ==================== LOGGING CONFIGURATION ====================

def configure_logging() -> None:
    """
    Configure structured logging for chatbot feature.

    Per FR-010: User-friendly error messages with no stack traces exposed to users.
    Stack traces and technical details are logged for debugging.

    Logging levels:
    - DEBUG: Detailed debugging information (intent detection, tool calls)
    - INFO: General information (user actions, successful operations)
    - WARNING: Warning messages (rate limiting, deprecated features)
    - ERROR: Error messages (validation errors, database errors, agent errors)
    - CRITICAL: Critical errors (service unavailable, unrecoverable errors)
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        datefmt='%Y-%m-%dT%H:%M:%S%z',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create chatbot logger
    chatbot_logger = logging.getLogger("chatbot")
    chatbot_logger.setLevel(log_level)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("cohere").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with proper configuration.

    Args:
        name: Logger name (e.g., "chatbot.agent", "chatbot.mcp")

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(f"chatbot.{name}")


# Initialize logging on module import
configure_logging()
