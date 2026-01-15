"""
Initialize database by creating all tables using SQLModel.

This script creates all database tables defined in SQLModel models.
Run this before starting the application for the first time.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (override any existing environment variables)
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

# Import after loading .env
from sqlmodel import SQLModel, create_engine
from src.models.user import User
from src.models.todo import Todo

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set!")
    print("Please check your .env file.")
    exit(1)

print(f"Connecting to database: {DATABASE_URL[:50]}...")

try:
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Create all tables
    print("\nCreating database tables...")
    SQLModel.metadata.create_all(engine)

    print("\n[SUCCESS] Database tables created successfully!")
    print("Tables created:")
    for table in SQLModel.metadata.sorted_tables:
        print(f"  - {table.name}")

except Exception as e:
    print(f"\n[ERROR] Error creating database tables: {e}")
    exit(1)
