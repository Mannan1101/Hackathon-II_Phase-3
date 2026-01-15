# Todo AI Chatbot Feature

**Feature ID**: 001-todo-ai-chatbot
**Status**: MVP Complete (User Stories 1 & 2)
**Version**: 1.1.0
**Date**: 2026-01-15

## Overview

Natural language interface for todo management powered by Cohere AI. Users can manage their tasks through conversational interactions instead of traditional CRUD operations.

## Features Implemented

### ✅ Phase 1-4: Core Functionality (MVP)

1. **Add Tasks** (US1, P1)
   - Natural language: "Add a task to buy groceries"
   - With description: "Remind me to call mom with note: discuss vacation plans"
   - Response: "I've added 'buy groceries' to your tasks!"

2. **List Tasks** (US2, P1)
   - Show all: "What are my tasks?"
   - Filter by status: "Show me my incomplete tasks"
   - Response: Formatted list with task numbers and statuses

3. **Complete Tasks** (US3, P2)
   - Mark done: "Mark 'buy groceries' as done"
   - Response: "Great! I've marked 'buy groceries' as completed."

4. **Delete Tasks** (US4, P2)
   - Remove: "Delete the groceries task"
   - Response: "I've deleted the 'buy groceries' task."

### 🚧 Pending Implementation

5. **Update Tasks** (US5, P3)
   - Change title: "Change my groceries task to 'buy groceries and milk'"
   - Add description: "Add note to X: Y"

6. **Answer Questions** (US6, P3)
   - Count tasks: "How many tasks do I have?"
   - Find oldest: "What's my oldest pending task?"
   - User info: "Who am I?"

7. **Polish** (Phase 9)
   - Rate limiting (T092)
   - Frontend integration (T094)
   - Performance optimization (T090)

## Architecture

### Stateless Design

Per FR-003, the chatbot is **completely stateless**:
- No conversation history retained
- Each request processed independently
- Agent does not maintain context between messages
- All state delegated to MCP tools + database

### Component Structure

```
backend/src/
├── agent/
│   ├── chatbot.py          # Main chatbot agent (Cohere integration)
│   └── __init__.py
├── mcp/
│   ├── tools.py            # 5 MCP tools (add, list, complete, delete, update)
│   ├── schemas.py          # Pydantic schemas for tool I/O
│   └── __init__.py
├── routers/
│   └── chat.py             # POST /api/chat endpoint
├── middleware/
│   └── auth.py             # get_current_user dependency
├── utils/
│   └── errors.py           # User-friendly error messages
└── models/
    └── todo.py             # Updated with description + status enum
```

### Technologies

- **Cohere AI** (command-r model): Intent recognition and NLU
- **FastAPI**: REST API framework
- **SQLModel**: ORM for database operations
- **Neon PostgreSQL**: Database (serverless)
- **Better Auth**: User authentication (session cookies)

## API Reference

### POST /api/chat

**Authentication**: Required (session cookie: `session_id`)

**Request**:
```json
{
  "text": "Add a task to buy groceries"
}
```

**Response**:
```json
{
  "message": "I've added 'buy groceries' to your tasks!",
  "metadata": {
    "intent": "add_task",
    "tool_called": "add_task",
    "success": true,
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Responses**:
- `400`: Invalid request (validation error)
- `401`: Unauthorized (missing/invalid session)
- `500`: Internal server error (Cohere API, database)
- `503`: Service unavailable (Cohere API down)

### GET /api/chat/health

Health check for chatbot service.

**Response**:
```json
{
  "status": "ok",
  "service": "todo-ai-chatbot",
  "model": "command-r"
}
```

## Setup Instructions

### 1. Environment Variables

Add to `.env` file:
```bash
# AI Chatbot Configuration
COHERE_API_KEY=your_cohere_api_key_here

# Optional: Model Configuration
CHATBOT_MODEL=command-r
CHATBOT_MAX_TOKENS=500
CHATBOT_TEMPERATURE=0.7
```

**Get Cohere API Key**:
1. Go to https://dashboard.cohere.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Copy your API key

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `cohere==5.11.0` - Cohere AI client

### 3. Run Database Migration

```bash
cd backend
alembic upgrade head
```

This adds:
- `description` column (VARCHAR 1000, nullable)
- `status` column (VARCHAR 20, default 'pending')

### 4. Start Backend

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 5. Test Chatbot

**Option A: cURL**
```bash
# Get session token by signing in first
curl -X POST http://localhost:8000/auth/signin \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}' \
     -c cookies.txt

# Test chatbot
curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -b cookies.txt \
     -d '{"text": "Add a task to buy groceries"}'
```

**Option B: API Docs**
1. Open http://localhost:8000/docs
2. Click "Authorize" and enter session token
3. Test POST /api/chat endpoint

**Option C: Frontend Integration** (if ChatKit UI is set up)
1. Update `frontend/src/services/chatService.ts` to use `/api/chat`
2. Test through chat interface

## Testing

### Manual Test Cases

1. **Add Task**
   - Input: "Add a task to buy groceries"
   - Expected: Success message with task title
   - Verify: Check database for new todo

2. **List Tasks**
   - Input: "What are my tasks?"
   - Expected: Formatted list of all tasks
   - Verify: Count matches database

3. **Complete Task**
   - Input: "Mark 'buy groceries' as done"
   - Expected: Success message
   - Verify: Task status = 'completed' in database

4. **Delete Task**
   - Input: "Delete the groceries task"
   - Expected: Success message
   - Verify: Task removed from database

5. **Error Handling**
   - Input: Empty message → 400 validation error
   - Input: "Complete nonexistent task" → Friendly error message
   - No auth → 401 unauthorized

### Automated Tests

**TDD Approach**: Tests should be written FIRST before implementation per constitution requirements.

Test structure:
```
backend/tests/
├── contract/           # MCP tool schema validation
│   └── test_mcp_tools.py
├── integration/        # End-to-end chatbot flows
│   ├── test_chat_flows.py
│   ├── test_stateless.py
│   └── test_mcp_integration.py
└── unit/              # Individual component tests
    ├── test_intent.py
    ├── test_validation.py
    └── test_errors.py
```

Run tests:
```bash
cd backend
pytest tests/ -v
```

## Performance

### Response Time Targets (SC-005)

- **Target**: <3s for 95% of requests
- **Breakdown**:
  - Cohere API: ~1500ms
  - Database query: <50ms
  - Overhead: ~1450ms

### Optimization Strategies

1. **Database Connection Pooling** (Implemented)
   - `pool_size=10`
   - `max_overflow=20`
   - `pool_timeout=30s`

2. **Async Operations** (Implemented)
   - All endpoints use `async def`
   - Database operations use sessions

3. **Future Optimizations** (Phase 9)
   - Response caching for common queries
   - Cohere prompt optimization
   - Request batching

## Security

### User Isolation (FR-008, SC-008)

All MCP tools enforce user isolation:
```python
# Every query filters by user_id
query = db.query(Todo).filter(Todo.user_id == UUID(input_data.user_id))
```

Users **cannot**:
- View other users' tasks
- Modify other users' tasks
- Delete other users' tasks

### Error Handling (FR-010)

All errors return user-friendly messages with no technical details:
- ✅ "Title must be between 1 and 200 characters"
- ❌ "ValidationError: title length exceeds maximum"
- ✅ "Something went wrong. Please try again in a moment."
- ❌ "psycopg2.OperationalError: connection refused"

Stack traces logged for debugging but never exposed to users.

## Troubleshooting

### "COHERE_API_KEY not configured"

**Solution**: Add Cohere API key to `.env` file:
```bash
COHERE_API_KEY=your_key_here
```

### "Chatbot service not configured"

**Check**:
```bash
curl http://localhost:8000/api/chat/health
```

If fails, verify:
1. `.env` file exists in `backend/` directory
2. `COHERE_API_KEY` is set
3. Backend restarted after adding key

### "Invalid authentication credentials"

**Solution**: Ensure session cookie is included in request.

cURL example:
```bash
# Save session cookie during signin
curl -X POST .../auth/signin -c cookies.txt ...

# Include cookie in chat request
curl -X POST .../api/chat -b cookies.txt ...
```

### Response time > 3 seconds

**Debug**:
1. Check Cohere API latency (should be <1.5s)
2. Check database query time: `EXPLAIN ANALYZE SELECT ...`
3. Enable request timing logs in config
4. Consider caching frequent queries

### Task not found

**Common causes**:
- Task identifier doesn't match any task title
- Task belongs to different user (user isolation)

**Solution**: Use "What are my tasks?" to see all tasks first.

## Next Steps

### Immediate (Phase 5-8)

1. **Implement US5: Update Tasks** (13 tasks)
   - Change title/description
   - Field validation

2. **Implement US6: Answer Questions** (8 tasks)
   - Count tasks
   - Find oldest task
   - User info queries

### Polish (Phase 9)

1. **Rate Limiting** (T092)
   - Prevent abuse
   - Return 429 if exceeded

2. **Frontend Integration** (T094)
   - Update ChatKit API service
   - Handle errors gracefully

3. **Performance Testing** (T090)
   - Verify <3s target
   - Load testing (100 concurrent users)

4. **Intent Accuracy Logging** (T093)
   - Track intent detection accuracy
   - Monitor for SC-003 (95% accuracy)

## Architecture Decisions

See [specs/001-todo-ai-chatbot/plan.md](../specs/001-todo-ai-chatbot/plan.md) for detailed architectural decisions.

### Key Decisions

1. **Stateless Architecture** (FR-003)
   - Agent has no memory between requests
   - All state delegated to MCP tools + database

2. **MCP Tool Delegation** (FR-005)
   - Agent NEVER touches database directly
   - All operations via 5 MCP tools

3. **Cohere over OpenAI** (Research Decision 1)
   - Better pricing for production
   - Command-R model optimized for chat

4. **Simplified MCP Implementation**
   - Direct function calls instead of full MCP protocol
   - Faster implementation, same architecture benefits

## Resources

- **Spec**: [specs/001-todo-ai-chatbot/spec.md](../specs/001-todo-ai-chatbot/spec.md)
- **Plan**: [specs/001-todo-ai-chatbot/plan.md](../specs/001-todo-ai-chatbot/plan.md)
- **Tasks**: [specs/001-todo-ai-chatbot/tasks.md](../specs/001-todo-ai-chatbot/tasks.md)
- **Contracts**: [specs/001-todo-ai-chatbot/contracts/](../specs/001-todo-ai-chatbot/contracts/)
- **Quick Start**: [specs/001-todo-ai-chatbot/quickstart.md](../specs/001-todo-ai-chatbot/quickstart.md)
- **Cohere Docs**: https://docs.cohere.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Support

For questions or issues:
1. Check this README first
2. Review specification: `specs/001-todo-ai-chatbot/spec.md`
3. Check logs: `backend/logs/app.log` (if configured)
4. Create ADR for significant decisions: `/sp.adr`

---

**Last Updated**: 2026-01-15
**Maintained By**: Development Team
**Feature Branch**: `001-todo-ai-chatbot`
