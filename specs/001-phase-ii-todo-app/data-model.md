# Data Model: Phase II Todo App

**Feature**: Phase II Todo App
**Date**: 2026-01-07
**Purpose**: Define database schema, entity relationships, validation rules, and state transitions

## Overview

The data model consists of two primary entities: **User** and **Todo**. Users have a one-to-many relationship with Todos, where each todo belongs to exactly one user. The schema enforces data isolation through foreign key constraints and application-level authorization checks.

---

## Entity Definitions

### User Entity

**Purpose**: Represents a registered user account with authentication credentials.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship (not persisted in database)
    todos: List["Todo"] = Relationship(back_populates="owner", cascade_delete=True)
```

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier for the user |
| `email` | String(255) | Unique, Not Null, Indexed | User's email address (used for login) |
| `hashed_password` | String(255) | Not Null | Bcrypt-hashed password (never store plaintext) |
| `created_at` | Timestamp | Not Null, Default: UTC now | Account creation timestamp |
| `updated_at` | Timestamp | Not Null, Default: UTC now | Last update timestamp |

**Validation Rules**:
- `email`: Must match email format regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- `email`: Case-insensitive uniqueness (normalize to lowercase before storage)
- `hashed_password`: Minimum 60 characters (bcrypt hash output length)
- `created_at`, `updated_at`: Immutable after creation (managed by database triggers)

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));
```

**Business Rules**:
1. Email addresses must be unique across all users (enforced by database constraint)
2. Passwords must be hashed with bcrypt (minimum 12 rounds) before storage
3. Users cannot be soft-deleted (hard delete only, cascading to todos)
4. Email cannot be changed after account creation (Phase II constraint, may change in future phases)

---

### Todo Entity

**Purpose**: Represents a single todo item belonging to a user.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    is_complete: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship (not persisted in database)
    owner: User = Relationship(back_populates="todos")
```

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier for the todo |
| `user_id` | UUID | Foreign Key → users.id, Not Null, Indexed | Owner of the todo (enforces data isolation) |
| `title` | String(200) | Not Null | Todo description/title |
| `is_complete` | Boolean | Not Null, Default: False | Completion status |
| `created_at` | Timestamp | Not Null, Default: UTC now | Todo creation timestamp |
| `updated_at` | Timestamp | Not Null, Default: UTC now | Last update timestamp (title or is_complete change) |

**Validation Rules**:
- `title`: Minimum 1 character (non-empty after trimming whitespace)
- `title`: Maximum 200 characters (enforced at database and application levels)
- `title`: Cannot be only whitespace (regex validation: `^\s*$` rejected)
- `is_complete`: Boolean only (true/false, no null allowed)
- `user_id`: Must reference an existing user (enforced by foreign key constraint)

**Indexes**:
```sql
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

**Business Rules**:
1. Todos must belong to exactly one user (enforced by foreign key constraint)
2. Todos are automatically deleted when their owner user is deleted (ON DELETE CASCADE)
3. Todos default to incomplete status when created
4. Todo titles are mutable (can be updated after creation)
5. Completion status can toggle between complete and incomplete freely
6. Todos are sorted by creation date descending (newest first) when retrieved

---

## Relationships

### User → Todos (One-to-Many)

**Relationship Type**: One-to-Many (one user has many todos)

**Foreign Key**: `todos.user_id` → `users.id`

**Cascade Behavior**: `ON DELETE CASCADE`
- When a user is deleted, all their todos are automatically deleted
- This ensures no orphaned todos remain in the database
- No manual cleanup required

**SQLModel Relationship Definition**:
```python
# In User model
todos: List["Todo"] = Relationship(back_populates="owner", cascade_delete=True)

# In Todo model
owner: User = Relationship(back_populates="todos")
```

**Navigation**:
- **Forward**: From User to Todos: `user.todos` returns list of Todo objects
- **Backward**: From Todo to User: `todo.owner` returns User object

**Cardinality**:
- One user can have 0 to N todos (unbounded)
- One todo belongs to exactly 1 user (required, not nullable)

**Data Isolation Enforcement**:
- Application layer MUST validate `todo.user_id == current_user.id` before any operation
- Database layer enforces foreign key constraint (cannot create todo with invalid user_id)
- Authorization middleware extracts `current_user` from session and passes to service layer

---

## API Request/Response Schemas

### Auth Schemas

**Signup Request**:
```python
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
```

**Signin Request**:
```python
class SigninRequest(BaseModel):
    email: EmailStr
    password: str
```

**Auth Response**:
```python
class AuthResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    # Note: hashed_password is NEVER included in responses
```

### Todo Schemas

**Create Todo Request**:
```python
class CreateTodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
```

**Update Todo Request**:
```python
class UpdateTodoRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    is_complete: Optional[bool] = None

    # At least one field must be provided
    @validator('title', 'is_complete')
    def check_at_least_one(cls, v, values):
        if not any([v, values.get('is_complete')]):
            raise ValueError('At least one field must be provided')
        return v
```

**Todo Response**:
```python
class TodoResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    is_complete: bool
    created_at: datetime
    updated_at: datetime
```

**Todo List Response**:
```python
class TodoListResponse(BaseModel):
    todos: List[TodoResponse]
    total: int
```

---

## Database Schema (SQL)

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));

-- Trigger to auto-update updated_at on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Todos Table

```sql
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    is_complete BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);

-- Trigger to auto-update updated_at on row modification
CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Database Constraints Summary

| Constraint | Table | Type | Purpose |
|------------|-------|------|---------|
| `users_pkey` | users | Primary Key | Unique identifier for users |
| `users_email_key` | users | Unique | Prevent duplicate email addresses |
| `idx_users_email` | users | Unique Index (lowercase) | Case-insensitive email uniqueness |
| `todos_pkey` | todos | Primary Key | Unique identifier for todos |
| `todos_user_id_fkey` | todos | Foreign Key | Link todo to owner user |
| `title_not_empty` | todos | Check | Prevent empty titles |
| `idx_todos_user_id` | todos | Index | Fast filtering by owner |
| `idx_todos_created_at` | todos | Index (DESC) | Fast sorting by creation date |

---

## State Transitions

### Todo Completion State Machine

**States**:
- `incomplete` (is_complete = false)
- `complete` (is_complete = true)

**Transitions**:
```
incomplete ←→ complete
```

**Transition Rules**:
1. **Mark Complete**: `incomplete` → `complete`
   - Trigger: User clicks completion toggle
   - Validation: User must own the todo
   - Side Effects: `updated_at` timestamp updated

2. **Mark Incomplete**: `complete` → `incomplete`
   - Trigger: User clicks completion toggle
   - Validation: User must own the todo
   - Side Effects: `updated_at` timestamp updated

**No Terminal State**: Todos can toggle between complete and incomplete indefinitely (no locked states).

---

## Data Validation Strategy

### Frontend Validation (Client-Side)

**Purpose**: Provide immediate user feedback, reduce unnecessary API calls.

**Rules**:
- Email format validation (regex or HTML5 email input)
- Password minimum 8 characters
- Todo title minimum 1 character, maximum 200 characters
- Trim whitespace from inputs before submission

**Note**: Frontend validation is NOT a security boundary (users can bypass). Always re-validate on backend.

### Backend Validation (Server-Side)

**Purpose**: Security boundary, enforce business rules, ensure data integrity.

**Layers**:
1. **Pydantic Model Validation**: Automatic validation via request schemas (type checking, min/max length)
2. **Database Constraints**: Final enforcement layer (unique constraints, foreign keys, check constraints)
3. **Service Layer Business Logic**: Custom validation (e.g., user owns todo before update)

**Validation Flow**:
```
Client Input
    ↓
Pydantic Schema Validation (FastAPI automatic)
    ↓
Service Layer Business Logic Validation
    ↓
Database Constraint Validation
    ↓
Success or Detailed Error Response
```

**Error Response Format**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

---

## Migration Strategy

### Initial Schema Migration (001_initial_schema.py)

**Alembic Migration Script**:
```python
"""Initial schema: users and todos tables

Revision ID: 001_initial
Revises:
Create Date: 2026-01-07
"""

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.create_index('idx_users_email', 'users', [sa.text('LOWER(email)')], unique=True)

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('is_complete', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("LENGTH(TRIM(title)) > 0", name='title_not_empty')
    )
    op.create_index('idx_todos_user_id', 'todos', ['user_id'])
    op.create_index('idx_todos_created_at', 'todos', [sa.text('created_at DESC')])

    # Create updated_at triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_todos_updated_at BEFORE UPDATE ON todos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

def downgrade():
    op.drop_table('todos')
    op.drop_table('users')
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;")
```

**Migration Execution**:
```bash
# Generate migration (if using autogenerate)
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Verify current version
alembic current

# Rollback (if needed)
alembic downgrade -1
```

---

## Data Access Patterns

### Common Queries

**1. User Signup (Create User)**:
```python
# Check if email exists
existing_user = await session.exec(
    select(User).where(User.email == email.lower())
).first()

# Create new user
new_user = User(email=email.lower(), hashed_password=hashed_pw)
session.add(new_user)
await session.commit()
await session.refresh(new_user)
```

**2. User Signin (Authenticate)**:
```python
# Find user by email
user = await session.exec(
    select(User).where(User.email == email.lower())
).first()

# Verify password
if user and verify_password(plain_password, user.hashed_password):
    return user
```

**3. Retrieve User's Todos (Sorted by created_at DESC)**:
```python
# Query todos for current user, sorted by creation date
todos = await session.exec(
    select(Todo)
    .where(Todo.user_id == current_user_id)
    .order_by(Todo.created_at.desc())
).all()
```

**4. Create Todo (with User Association)**:
```python
new_todo = Todo(user_id=current_user_id, title=title, is_complete=False)
session.add(new_todo)
await session.commit()
await session.refresh(new_todo)
```

**5. Update Todo (with Authorization Check)**:
```python
# Fetch todo and verify ownership
todo = await session.get(Todo, todo_id)
if not todo or todo.user_id != current_user_id:
    raise HTTPException(status_code=404, detail="Todo not found")

# Update fields
if title is not None:
    todo.title = title
if is_complete is not None:
    todo.is_complete = is_complete

await session.commit()
await session.refresh(todo)
```

**6. Delete Todo (with Authorization Check)**:
```python
# Fetch todo and verify ownership
todo = await session.get(Todo, todo_id)
if not todo or todo.user_id != current_user_id:
    raise HTTPException(status_code=404, detail="Todo not found")

await session.delete(todo)
await session.commit()
```

---

## Performance Considerations

### Query Optimization

1. **Index Usage**:
   - `idx_users_email`: Speeds up login queries (O(log n) lookup)
   - `idx_todos_user_id`: Enables fast filtering by owner (every todo query uses this)
   - `idx_todos_created_at`: Supports fast descending sort (avoids table scan)

2. **N+1 Query Prevention**:
   - Use eager loading for user → todos relationship (if fetching multiple users with todos)
   - Example: `select(User).options(selectinload(User.todos))`

3. **Connection Pooling**:
   - SQLModel async engine uses connection pooling (default: 5-10 connections)
   - Adjust pool size based on concurrent user load: `create_engine(..., pool_size=20, max_overflow=10)`

### Scalability Limits (Phase II)

- **User Count**: Designed for 100 concurrent users (per performance goals)
- **Todos per User**: No enforced limit (estimated 1000 todos/user max for Phase II)
- **Database Size**: Neon auto-scales, no manual sharding required in Phase II
- **Future Optimization**: If >10,000 todos per user, consider pagination or archival

---

## Summary

**Entities**: User, Todo
**Relationships**: User → Todos (one-to-many, cascade delete)
**Validation**: Frontend (UX) + Backend (security) + Database (integrity)
**Indexes**: Email (unique), User ID (FK), Created At (sort)
**Migrations**: Alembic with upgrade/downgrade scripts
**Authorization**: Service layer validates `todo.user_id == current_user_id`

**Data model supports all functional requirements (FR-AUTH, FR-TODO, FR-DATA) and enforces 100% data isolation per success criteria SC-003.**
