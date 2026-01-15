# Quick Start Guide: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-15
**Target Audience**: Developers implementing or testing the chatbot feature

## Overview

This guide provides step-by-step instructions to set up, develop, and test the Todo AI Chatbot feature. The chatbot uses natural language processing (Cohere AI) to manage todo tasks through conversational interactions.

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm installed (for frontend)
- **Git** installed
- **Neon PostgreSQL** database provisioned (connection string available)
- **Cohere API account** with API key
- **Better Auth** configured in the application
- **Existing Todo App** repository cloned

## Environment Setup

### 1. Install Backend Dependencies

Navigate to the backend directory and install required Python packages:

```bash
cd backend

# Install new dependencies for AI chatbot
pip install openai-agents-sdk>=1.0.0
pip install cohere>=5.0.0
pip install mcp-sdk>=1.0.0

# Or update requirements.txt and install all
pip install -r requirements.txt
```

**Update `backend/requirements.txt`**:
```txt
# Existing dependencies
fastapi==0.104.1
sqlmodel==0.0.14
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
psycopg2-binary==2.9.9
alembic==1.13.0
better-auth==1.0.0  # Or whatever version is used

# NEW: AI Chatbot dependencies
openai-agents-sdk==1.0.0
cohere==5.0.0
mcp-sdk==1.0.0
```

### 2. Configure Environment Variables

Create or update `.env` file in the project root:

```bash
# Database (existing)
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech/dbname?sslmode=require

# Better Auth (existing)
BETTER_AUTH_SECRET=your_existing_auth_secret

# NEW: AI Chatbot Configuration
COHERE_API_KEY=your_cohere_api_key_here
OPENAI_AGENTS_SDK_KEY=your_sdk_key_if_required  # May not be needed

# Optional: Chatbot Configuration
CHATBOT_MODEL=command-r  # Cohere model name
CHATBOT_MAX_TOKENS=500   # Max response length
CHATBOT_TEMPERATURE=0.7  # Response creativity (0.0-1.0)
```

**How to get Cohere API key**:
1. Go to https://dashboard.cohere.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Copy your API key
5. Paste into `.env` file

### 3. Verify Database Schema

The chatbot reuses the existing `todos` table. Verify it exists:

```bash
# Connect to your Neon database
psql $DATABASE_URL

# Check if todos table exists
\dt todos

# Verify schema
\d todos

# Expected output:
# Column      | Type          | Nullable | Default
# ------------|---------------|----------|--------
# id          | integer       | not null | nextval...
# user_id     | integer       | not null |
# title       | varchar(200)  | not null |
# description | varchar(1000) | nullable |
# status      | varchar(20)   | not null | 'pending'
# created_at  | timestamp     | nullable | now()
# updated_at  | timestamp     | nullable | now()
```

**If table is missing**, run migration:
```bash
cd backend
alembic upgrade head
```

### 4. Verify Frontend Dependencies

The existing ChatKit UI should already be set up. No new dependencies needed.

```bash
cd frontend
npm install  # Install existing dependencies
```

## Development Workflow

### Step 1: Implement MCP Server Tools

Create the MCP server module that exposes task management tools.

**File**: `backend/src/mcp/tools.py`

```python
from mcp_sdk import MCPServer, Tool, ToolInput, ToolOutput
from sqlmodel import Session, select
from ..models.todo import Todo, TodoCreate, TaskStatus
from ..config import get_session
from datetime import datetime
from typing import Optional

mcp_server = MCPServer(name="todo_mcp_server")

@mcp_server.tool(
    name="add_task",
    description="Creates a new todo task for the authenticated user"
)
async def add_task(
    user_id: int,
    title: str,
    description: Optional[str] = None
) -> dict:
    """Add a new task to the database"""
    # Validation
    if not title or len(title) < 1 or len(title) > 200:
        raise ValueError("Title must be between 1 and 200 characters")
    if description and len(description) > 1000:
        raise ValueError("Description must be under 1000 characters")

    # Create task
    with get_session() as session:
        new_todo = Todo(
            user_id=user_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING
        )
        session.add(new_todo)
        session.commit()
        session.refresh(new_todo)

        return {
            "success": True,
            "task_id": new_todo.id,
            "message": f"I've added '{title}' to your tasks!"
        }

@mcp_server.tool(
    name="list_tasks",
    description="Retrieves all todo tasks for the authenticated user"
)
async def list_tasks(
    user_id: int,
    status: Optional[str] = None
) -> dict:
    """List user's tasks, optionally filtered by status"""
    with get_session() as session:
        query = select(Todo).where(Todo.user_id == user_id)
        if status:
            query = query.where(Todo.status == status)
        query = query.order_by(Todo.created_at.desc())

        todos = session.exec(query).all()

        return {
            "tasks": [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                }
                for todo in todos
            ],
            "count": len(todos)
        }

# Implement complete_task, delete_task, update_task similarly...
```

### Step 2: Implement AI Agent

Create the chatbot agent that uses Cohere for intent recognition.

**File**: `backend/src/agent/chatbot.py`

```python
from openai_agents_sdk import Agent, AgentConfig
import cohere
from typing import List, Dict
from ..mcp.tools import mcp_server
import os

class TodoChatbot:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cohere_client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Initialize OpenAI Agents SDK with MCP tools"""
        config = AgentConfig(
            model="command-r",  # Cohere model
            temperature=0.7,
            max_tokens=500,
            tools=mcp_server.get_tools(),  # Register MCP tools
            system_prompt=(
                "You are a friendly todo task manager assistant. "
                "Parse user intent from natural language and call appropriate tools. "
                "Always respond in a conversational, friendly tone. "
                "You are completely stateless - do not remember previous conversations. "
                "For all task operations, use the provided tools with the user_id context."
            )
        )
        return Agent(config=config)

    async def process_message(self, user_message: str) -> str:
        """Process user message and return response"""
        try:
            # Call agent with user message
            response = await self.agent.run(
                message=user_message,
                context={"user_id": self.user_id}  # Pass user_id to tools
            )
            return response.message
        except Exception as e:
            # Log error and return user-friendly message
            logger.error(f"Agent error: {e}", extra={"user_id": self.user_id})
            return "Sorry, I couldn't understand that. Please try again."
```

### Step 3: Implement Chat API Endpoint

Create the FastAPI endpoint for chat interactions.

**File**: `backend/src/routers/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..auth_service import get_current_user, User
from ..agent.chatbot import TodoChatbot
import logging

router = APIRouter(prefix="/api", tags=["chatbot"])
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    message: str
    metadata: dict = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """Handle chatbot messages"""
    try:
        # Create stateless chatbot instance for this request
        chatbot = TodoChatbot(user_id=current_user.id)

        # Process message
        response_message = await chatbot.process_message(request.text)

        return ChatResponse(
            message=response_message,
            metadata={"user_id": current_user.id}
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again in a moment."
        )
```

### Step 4: Register Chat Router

Update `backend/src/main.py` to include the chat router:

```python
from fastapi import FastAPI
from .routers import auth, todos, chat  # Add chat import

app = FastAPI(title="Todo App")

# Register routers
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(chat.router)  # NEW: Register chat router

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Step 5: Update Frontend (Optional)

If ChatKit needs to point to new endpoint, update the API service:

**File**: `frontend/src/services/chatService.ts`

```typescript
export const sendChatMessage = async (message: string): Promise<string> => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',  // Send auth cookie
    body: JSON.stringify({ text: message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to send message');
  }

  const data = await response.json();
  return data.message;
};
```

## Running the Application

### Start Backend Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

The server should start at `http://localhost:8000`. You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Start Frontend (if separate)

```bash
cd frontend
npm run dev
```

The frontend should start at `http://localhost:3000`.

### Test the Chatbot

1. **Open browser**: Navigate to `http://localhost:3000`
2. **Log in**: Use Better Auth to authenticate
3. **Open chat interface**: Navigate to chat page (ChatKit UI)
4. **Send test messages**:
   - "Add a task to buy groceries"
   - "What are my tasks?"
   - "Mark 'buy groceries' as done"
   - "Delete the groceries task"

## Testing

### Run Unit Tests

```bash
cd backend
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
# Requires test database setup
pytest tests/integration/ -v
```

### Run Contract Tests

```bash
pytest tests/contract/ -v
```

### Manual Testing Checklist

- [ ] User can add a task via natural language
- [ ] User can list tasks via natural language
- [ ] User can complete a task via natural language
- [ ] User can delete a task via natural language
- [ ] User can update a task via natural language
- [ ] User gets friendly error messages for invalid inputs
- [ ] User isolation works (cannot see other users' tasks)
- [ ] Response time is under 3 seconds
- [ ] Ambiguous messages get clarification prompts

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai_agents_sdk'"

**Solution**: Install the missing package:
```bash
pip install openai-agents-sdk
```

### Issue: "COHERE_API_KEY not found"

**Solution**: Ensure `.env` file has Cohere API key:
```bash
COHERE_API_KEY=your_key_here
```

### Issue: "Chatbot returns 'Something went wrong'"

**Check**:
1. Cohere API key is valid
2. Database connection is working (`/health/database`)
3. Check logs for specific error: `tail -f logs/app.log`

### Issue: "Response time > 3 seconds"

**Debug**:
1. Check Cohere API latency (should be <1.5s)
2. Check database query time (should be <50ms)
3. Enable request timing logs
4. Consider caching or optimization if needed

### Issue: "Tasks not persisting"

**Check**:
1. Database connection string correct
2. `todos` table exists
3. Alembic migrations applied
4. Check database logs for errors

## Next Steps

After setup is complete:

1. **Run acceptance tests** for all 6 user stories (P1-P3)
2. **Verify constitution compliance** (test-first development, security)
3. **Measure performance** (response time, intent accuracy)
4. **Deploy to staging** for user acceptance testing
5. **Monitor observability** (logs, metrics, errors)

## Resources

- **Spec**: [spec.md](./spec.md) - Feature requirements
- **Plan**: [plan.md](./plan.md) - Architecture decisions
- **Research**: [research.md](./research.md) - Technical decisions
- **Data Model**: [data-model.md](./data-model.md) - Database schema
- **Contracts**: [contracts/](./contracts/) - API and tool schemas

## Support

For questions or issues:
- Check existing documentation first
- Review logs: `backend/logs/app.log`
- Check constitution: `.specify/memory/constitution.md`
- Create ADR for significant decisions: `/sp.adr`
