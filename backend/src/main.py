"""
FastAPI application entry point.

This module initializes the FastAPI application with CORS middleware,
routers, and exception handlers.
"""

# IMPORTANT: Load .env BEFORE importing any local modules
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env file (override any existing environment variables)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Now import local modules (they will use the correct environment variables)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .middleware.logging_middleware import LoggingMiddleware
from .routers import health, auth, todos, chat

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL[:50] if DATABASE_URL else "None")  # optional, test




# Create FastAPI application
app = FastAPI(
    title="Phase II Todo App API with AI Chatbot",
    description="RESTful API for todo management with user authentication and natural language AI chatbot",
    version="1.1.0",  # Bumped for chatbot feature
    docs_url="/docs",
    redoc_url="/redoc",
)
"""
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(chat.router)  # Feature: 001-todo-ai-chatbot

# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint returning API information.

    Returns:
        dict: API name and version
    """
    return {
        "name": "Phase II Todo App API",
        "version": "1.0.0",
        "status": "running",
    }
