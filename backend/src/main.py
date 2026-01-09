"""
FastAPI application entry point.

This module initializes the FastAPI application with CORS middleware,
routers, and exception handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .middleware.logging_middleware import LoggingMiddleware
from .routers import health, auth, todos
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Database URL:", DATABASE_URL)  # optional, test




# Create FastAPI application
app = FastAPI(
    title="Phase II Todo App API",
    description="RESTful API for todo management with user authentication",
    version="1.0.0",
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
