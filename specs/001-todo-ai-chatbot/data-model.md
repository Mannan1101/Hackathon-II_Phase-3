# Data Model: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-15
**Phase**: Phase 1 - Data Model Design

## Overview

This document defines the database schema and entity relationships for the Todo AI Chatbot feature. The chatbot reuses the existing `todos` table from the application's Phase II infrastructure, ensuring data consistency and avoiding duplication.

## Entities

### 1. User (Existing)

Managed by Better Auth, already exists in the database.

**Attributes**:
- `id` (INTEGER, PRIMARY KEY): Unique user identifier
- `email` (VARCHAR, UNIQUE, NOT NULL): User's email address
- `password_hash` (VARCHAR, NOT NULL): Hashed password (bcrypt)
- `created_at` (TIMESTAMP, DEFAULT NOW()): Account creation timestamp
- `updated_at` (TIMESTAMP, DEFAULT NOW()): Last update timestamp

**Notes**:
- Better Auth manages this table
- Chatbot does not modify user table
- user_id is extracted from authentication session and used for task isolation

### 2. Todo/Task (Existing, Reused)

Represents a task/todo item created by users.

**Attributes**:
- `id` (INTEGER, PRIMARY KEY, AUTO INCREMENT): Unique task identifier
- `user_id` (INTEGER, FOREIGN KEY → users.id, NOT NULL, ON DELETE CASCADE): Owner of the task
- `title` (VARCHAR(200), NOT NULL): Task title/description (max 200 characters per FR-011)
- `description` (VARCHAR(1000), NULLABLE): Optional detailed description (max 1000 characters)
- `status` (VARCHAR(20), DEFAULT 'pending', CHECK IN ('pending', 'completed')): Task completion status
- `created_at` (TIMESTAMP, DEFAULT NOW()): Task creation timestamp
- `updated_at` (TIMESTAMP, DEFAULT NOW()): Last modification timestamp

**Constraints**:
- `user_id` foreign key references `users(id)` with CASCADE delete (if user deleted, their tasks deleted)
- `status` must be either 'pending' or 'completed' (enforced by CHECK constraint)
- `title` length limit: 200 characters (application-level validation + database VARCHAR limit)
- `description` length limit: 1000 characters (application-level validation + database VARCHAR limit)

**Indexes**:
- `PRIMARY KEY (id)`: Fast lookups by task ID
- `INDEX idx_todos_user_status (user_id, status)`: Fast filtering by user and status (e.g., "show my incomplete tasks")
- `INDEX idx_todos_user_created (user_id, created_at DESC)`: Fast sorting by creation date for newest/oldest queries

**Notes**:
- This table already exists from Phase II todo management features
- Chatbot reuses this table (no new table created)
- All MCP tools operate on this table via SQLModel ORM

### 3. Chat Message (Ephemeral, Not Persisted)

Represents a user's natural language input and the chatbot's response. **NOT stored in database** per FR-003 (stateless architecture).

**Attributes** (In-memory only):
- `user_id` (INTEGER): User who sent the message (from session)
- `user_message` (STRING): User's natural language input
- `bot_response` (STRING): Chatbot's generated response
- `timestamp` (TIMESTAMP): Request timestamp (for logging only)

**Notes**:
- No conversation history table
- Each request is independent (stateless)
- Messages logged for observability but not persisted as user data
- If conversation history is needed in future, it would require constitution amendment (Phase III feature)

## Relationships

```
User (1) ←→ (N) Todo
  │
  └── user_id (FK)

Chat Message (ephemeral, not persisted)
  │
  └── References User via session context (not FK)
```

**Relationship Details**:
- One user can have many todos (1:N)
- User deletion cascades to todos (ON DELETE CASCADE)
- Chat messages are not related to any entity (ephemeral)

## SQL Schema Verification

### Existing Schema (Should Already Exist)

```sql
-- Users table (managed by Better Auth)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Todos table (Phase II, should exist)
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_todos_user_status ON todos(user_id, status);
CREATE INDEX IF NOT EXISTS idx_todos_user_created ON todos(user_id, created_at DESC);
```

### Migration Strategy

**If Schema Exists** (Expected):
- No migration needed
- Verify indexes exist
- Verify constraints are correct

**If Schema Missing** (Unlikely):
- Create Alembic migration: `alembic revision -m "create_todos_table"`
- Apply migration: `alembic upgrade head`

**Migration File** (if needed):

```python
# alembic/versions/xxx_create_todos_table.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_check_constraint(
        'status_check',
        'todos',
        "status IN ('pending', 'completed')"
    )
    op.create_index('idx_todos_user_status', 'todos', ['user_id', 'status'])
    op.create_index('idx_todos_user_created', 'todos', ['user_id', 'created_at'], postgresql_ops={'created_at': 'DESC'})

def downgrade():
    op.drop_index('idx_todos_user_created', table_name='todos')
    op.drop_index('idx_todos_user_status', table_name='todos')
    op.drop_table('todos')
```

## SQLModel Entity Definitions

### Todo Model (backend/src/models/todo.py)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class TodoBase(SQLModel):
    """Base Todo model with shared attributes"""
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)

class Todo(TodoBase, table=True):
    """Database Todo model"""
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (if User model exists)
    # user: Optional["User"] = Relationship(back_populates="todos")

class TodoCreate(TodoBase):
    """Schema for creating a todo (no id, user_id from session)"""
    pass

class TodoUpdate(SQLModel):
    """Schema for updating a todo (partial updates allowed)"""
    title: Optional[str] = Field(default=None, max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None

class TodoResponse(TodoBase):
    """Schema for returning a todo to client"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
```

**Validation Rules** (Enforced in SQLModel):
- `title`: Required, 1-200 characters
- `description`: Optional, 0-1000 characters
- `status`: Enum (pending/completed), default pending
- `user_id`: Required (from session), must reference valid user
- Timestamps: Auto-generated on create/update

## Data Access Patterns

### MCP Tools Query Patterns

**add_task** (Create):
```python
new_todo = Todo(
    user_id=user_id,
    title=title,
    description=description,
    status=TaskStatus.PENDING
)
session.add(new_todo)
session.commit()
session.refresh(new_todo)
return new_todo
```

**list_tasks** (Read):
```python
query = select(Todo).where(Todo.user_id == user_id)
if status:
    query = query.where(Todo.status == status)
query = query.order_by(Todo.created_at.desc())
todos = session.exec(query).all()
return todos
```

**complete_task** (Update):
```python
todo = session.get(Todo, task_id)
if not todo or todo.user_id != user_id:
    raise NotFoundError("Task not found")
if todo.status == TaskStatus.COMPLETED:
    raise ValidationError("Task already completed")
todo.status = TaskStatus.COMPLETED
todo.updated_at = datetime.utcnow()
session.commit()
return todo
```

**delete_task** (Delete):
```python
todo = session.get(Todo, task_id)
if not todo or todo.user_id != user_id:
    raise NotFoundError("Task not found")
session.delete(todo)
session.commit()
```

**update_task** (Update):
```python
todo = session.get(Todo, task_id)
if not todo or todo.user_id != user_id:
    raise NotFoundError("Task not found")
if title:
    todo.title = title
if description is not None:
    todo.description = description
todo.updated_at = datetime.utcnow()
session.commit()
session.refresh(todo)
return todo
```

## Data Isolation & Security

### User Isolation (FR-008, SC-008)

**Enforced at Query Level**:
- All queries MUST include `WHERE user_id = ?` filter
- MCP tools validate `user_id` matches authenticated session
- No cross-user data leakage possible

**Example Secure Query**:
```python
# ✅ CORRECT: Filtered by user_id
todos = session.exec(
    select(Todo).where(Todo.user_id == current_user_id)
).all()

# ❌ WRONG: No user_id filter (would return all users' tasks)
todos = session.exec(select(Todo)).all()  # NEVER DO THIS
```

### Validation Rules

**Application-Level Validation**:
- Title: 1-200 characters (reject if outside range)
- Description: 0-1000 characters (reject if exceeds)
- Status: Must be "pending" or "completed" (enum validation)
- user_id: Must match authenticated session (security check)

**Database-Level Validation**:
- VARCHAR length limits (200 for title, 1000 for description)
- CHECK constraint on status (IN ('pending', 'completed'))
- Foreign key constraint on user_id (must reference valid user)
- NOT NULL constraints on required fields

## Performance Considerations

### Indexing Strategy

**Existing Indexes**:
1. `PRIMARY KEY (id)`: O(log n) lookups by task ID
2. `INDEX (user_id, status)`: Composite index for filtered queries (e.g., "my incomplete tasks")
3. `INDEX (user_id, created_at DESC)`: Sorted queries for newest/oldest tasks

**Query Performance**:
- List user's tasks: O(log n) using (user_id, status) index
- Get task by ID: O(log n) using primary key
- Complete/delete/update: O(log n) lookup + O(1) update

**Expected Load**:
- 100 concurrent users (SC-006)
- Assume 50 tasks per user average = 5,000 tasks total
- Indexed queries remain fast (<50ms) at this scale

### Database Connection Pooling

**SQLAlchemy Settings** (backend/src/config.py):
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,           # 10 persistent connections
    max_overflow=20,        # 20 additional connections under load
    pool_pre_ping=True,     # Verify connection before use
    pool_recycle=3600,      # Recycle connections every hour
)
```

## State Management

### Stateless Architecture (FR-003)

**No Persistence of**:
- Conversation history
- Chat context
- User preferences (beyond database)
- Agent state

**Only Persistent Data**:
- User accounts (users table)
- Todo tasks (todos table)
- Logs (for observability, not user data)

**Implications**:
- Each chat request is independent
- Agent reads fresh data from database each time
- No session storage beyond authentication
- No Redis, no in-memory cache

## Future Considerations (Out of Scope)

### Not Implemented in This Feature:
- Conversation history storage (would require new chat_messages table)
- Task categories/tags (would require new tables)
- Task due dates (would require todos.due_date column)
- Task priorities (would require todos.priority column)
- Collaborative tasks (would require task_shares table)
- Task attachments (would require attachments table)

These features require constitution amendment or Phase III approval.

## Summary

**Entities**: 2 database tables (users, todos) + 1 ephemeral (chat_message)
**New Tables**: 0 (reuse existing Phase II infrastructure)
**Indexes**: 3 (primary key + 2 composite indexes for performance)
**Relationships**: 1 (User 1:N Todo with CASCADE delete)
**Validation**: Application-level (SQLModel) + database-level (constraints)
**Performance**: Indexed queries <50ms, connection pooling configured
**Security**: User isolation via user_id filtering, SQL injection prevention via ORM

No schema changes required - feature reuses existing infrastructure.
