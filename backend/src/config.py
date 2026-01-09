"""
Application configuration management.

This module loads and validates environment variables using Pydantic settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


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

    # Application Configuration
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
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
