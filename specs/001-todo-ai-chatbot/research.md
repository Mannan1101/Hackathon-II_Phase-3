# Research: Todo AI Chatbot Technical Decisions

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-01-15
**Phase**: Phase 0 - Research & Technical Decisions

## Overview

This document captures technical research and decisions for implementing a stateless AI chatbot that manages todo tasks through natural language conversations. The chatbot must integrate with existing infrastructure (FastAPI backend, ChatKit UI, Neon PostgreSQL) while introducing AI agent capabilities for intent recognition.

## Research Areas

### 1. OpenAI Agents SDK Integration with Cohere

**Decision**: Use OpenAI Agents SDK with Cohere model for natural language understanding

**Rationale**:
- OpenAI Agents SDK provides standardized agent framework with tool calling capabilities
- Cohere Command-R model offers strong intent classification and parameter extraction
- SDK handles conversation context management (even though our agent is stateless per request)
- Built-in support for function/tool calling aligns with MCP tool delegation pattern

**Alternatives Considered**:
1. **LangChain + Cohere** - More complex, overkill for stateless single-turn interactions
2. **Direct Cohere API** - Would require manual tool calling logic and prompt engineering
3. **Rasa NLU** - Open source but requires training data and self-hosting, not suitable for 95% accuracy target

**Implementation Notes**:
- Agent configuration: stateless mode, no conversation memory
- System prompt: "You are a todo task manager. Parse user intent and call appropriate tools. Never store state."
- Tool definitions: 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Response format: Friendly conversational tone, confirm actions

**Dependencies**:
```python
openai-agents-sdk>=1.0.0
cohere>=5.0.0
```

### 2. MCP Server Architecture

**Decision**: Use official MCP SDK to create dedicated MCP server exposing 5 task management tools

**Rationale**:
- MCP (Model Context Protocol) provides standard interface for AI agents to call external tools
- Clean separation: Agent (intent recognition) ↔ MCP Server (tool execution) ↔ Database (persistence)
- Enforces stateless architecture - agent has no direct database access
- Tools are reusable across multiple agents or interfaces
- Built-in schema validation for tool inputs/outputs

**Alternatives Considered**:
1. **Direct function calls in agent code** - Violates FR-005 (no internal state management), tight coupling
2. **Custom REST API for tools** - Reinvents wheel, MCP is standardized protocol
3. **FastAPI endpoints as tools** - Mixing concerns, complicates authentication flow

**MCP Server Design**:
- **Hosting**: Embedded in FastAPI backend process (same application, different module)
- **Transport**: HTTP/SSE (Server-Sent Events) for real-time tool execution
- **Authentication**: Inherit user_id from FastAPI session context
- **Tool Schema**: JSON Schema definitions for input validation

**Tool Definitions**:

1. **add_task**
   - Input: `user_id: int, title: str, description: str | None`
   - Output: `{success: bool, task_id: int, message: str}`
   - Validation: title ≤200 chars, description ≤1000 chars

2. **list_tasks**
   - Input: `user_id: int, status: "pending" | "completed" | None`
   - Output: `{tasks: List[Task], count: int}`
   - Sorting: created_at DESC

3. **complete_task**
   - Input: `user_id: int, task_id: int`
   - Output: `{success: bool, message: str}`
   - Validation: task exists, belongs to user, not already completed

4. **delete_task**
   - Input: `user_id: int, task_id: int`
   - Output: `{success: bool, message: str}`
   - Validation: task exists, belongs to user

5. **update_task**
   - Input: `user_id: int, task_id: int, title: str | None, description: str | None`
   - Output: `{success: bool, message: str}`
   - Validation: at least one field to update, title/description limits

**Dependencies**:
```python
mcp-sdk>=1.0.0  # Official MCP SDK
```

### 3. Stateless Chat Flow Architecture

**Decision**: POST /api/chat endpoint with request-scoped agent initialization

**Rationale**:
- FR-003 requires complete statelessness - no conversation history retention
- Each request: authenticate → extract user_id → initialize agent → process message → call tools → respond
- Agent instance destroyed after response (garbage collected)
- No session storage, no Redis, no in-memory cache

**Flow Diagram**:
```
User → ChatKit UI → POST /api/chat {message: "Add task X"}
                         ↓
                    FastAPI Middleware (Better Auth)
                         ↓ (user_id extracted)
                    ChatRouter.chat_endpoint()
                         ↓
                    Agent = OpenAIAgents(tools=mcp_tools, user_id)
                         ↓
                    Agent.process(message)  # Calls Cohere API
                         ↓
                    Agent determines: call add_task tool
                         ↓
                    MCP Server.add_task(user_id, "X")
                         ↓
                    SQLModel.insert(Task(user_id, "X"))
                         ↓
                    Return {success: true, task_id: 123}
                         ↓
                    Agent formats: "I've added 'X' to your tasks!"
                         ↓
                    Response → ChatKit UI
```

**Error Handling**:
- Cohere API failure → "Sorry, I couldn't understand that. Please try again."
- Database error → "Something went wrong. Your request couldn't be completed."
- Task not found → "I couldn't find that task. Would you like to see your current tasks?"
- Validation error → "Task title must be under 200 characters."

**Alternatives Considered**:
1. **WebSocket persistent connection** - Violates stateless requirement, adds complexity
2. **Multi-turn conversation with context** - Violates FR-003, requires session storage
3. **Streaming responses** - Unnecessary for simple confirmations, adds latency

### 4. Database Schema Design

**Decision**: Reuse existing `todos` table with SQLModel, ensure user_id indexing

**Rationale**:
- Existing table already has: id, user_id, title, description, status, created_at, updated_at
- SQLModel ORM prevents SQL injection (parameterized queries)
- PostgreSQL indexing on (user_id, status) for fast filtering

**Schema Verification**:
```sql
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_todos_user_status ON todos(user_id, status);
CREATE INDEX idx_todos_user_created ON todos(user_id, created_at DESC);
```

**Migration Strategy**:
- No migration needed if table exists
- If table missing: Alembic migration to create schema
- Verify constraints: user_id foreign key, status enum, length limits

**Alternatives Considered**:
1. **Separate chatbot_tasks table** - Unnecessary duplication, violates DRY
2. **NoSQL (MongoDB)** - Overkill for simple relational data, Neon PostgreSQL already provisioned

### 5. Authentication Integration

**Decision**: Leverage existing Better Auth middleware to extract user_id from session

**Rationale**:
- Better Auth already handles: signup, signin, session management, JWT tokens
- FastAPI dependency injection: `current_user = Depends(get_current_user)`
- Chatbot endpoint inherits authentication: no unauthenticated access
- user_id passed to all MCP tools for data isolation (FR-008)

**Flow**:
```python
@router.post("/api/chat")
async def chat_endpoint(
    message: ChatRequest,
    current_user: User = Depends(get_current_user)  # Better Auth dependency
) -> ChatResponse:
    user_id = current_user.id
    # Initialize agent with user_id context
    agent = create_agent(user_id=user_id, mcp_tools=get_mcp_tools())
    response = await agent.process(message.text)
    return ChatResponse(message=response)
```

**Security Measures**:
- All MCP tools validate: `if task.user_id != user_id: raise Forbidden`
- Database queries filter: `WHERE user_id = ?`
- No cross-user data leakage (SC-008 verification)

**Alternatives Considered**:
1. **Separate chatbot authentication** - Redundant, violates DRY
2. **API key authentication** - Less secure than session-based auth

### 6. Frontend Integration (ChatKit UI)

**Decision**: Minimal changes to existing ChatKit UI, update API endpoint only

**Rationale**:
- ChatKit already provides: message input, message history display, send button
- Only change needed: Point ChatKit to new `/api/chat` endpoint
- Response format: `{message: string}` - already compatible

**Integration Points**:
```typescript
// frontend/src/services/chatService.ts
export const sendChatMessage = async (message: string): Promise<string> => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // Send session cookie for auth
    body: JSON.stringify({ text: message })
  });
  const data = await response.json();
  return data.message;
};
```

**Alternatives Considered**:
1. **Build custom chat UI** - Unnecessary, ChatKit already exists
2. **WebSocket real-time updates** - Overkill for request/response pattern

### 7. Error Handling Strategy

**Decision**: Three-tier error handling: agent-level, tool-level, user-facing

**Rationale**:
- FR-010 requires user-friendly error messages (no stack traces)
- Different error types need different responses
- Observability: log all errors with context

**Error Tiers**:

**Tier 1: Agent-Level (Intent Recognition)**
- Cohere API timeout → "I'm having trouble understanding right now. Please try again."
- Invalid API key → Log critical error, return generic message
- Rate limit → "Too many requests. Please wait a moment."

**Tier 2: Tool-Level (MCP Operations)**
- Task not found → "I couldn't find that task. Would you like to see your current tasks?"
- Validation error → "Task title must be under 200 characters. Please try a shorter title."
- Already completed → "That task is already marked as complete!"
- Database connection error → "Something went wrong. Please try again in a moment."

**Tier 3: User-Facing (Response Formatting)**
- Ambiguous intent → "I'm not sure what you want to do. You can add, list, complete, delete, or update tasks."
- Multiple intents detected → "Let's do one thing at a time. Would you like to [intent 1] or [intent 2]?"

**Logging Requirements**:
```python
logger.error(
    "MCP tool error",
    extra={
        "tool": "add_task",
        "user_id": user_id,
        "error": str(e),
        "input": {"title": title, "description": description}
    }
)
```

### 8. Performance Optimization

**Decision**: Focus on latency reduction, accept Cohere API overhead

**Rationale**:
- SC-005 target: <3s response time (p95)
- Cohere API typically: 500-1500ms
- Database queries: <50ms with indexing
- Total budget: 3000ms - 1500ms (Cohere) - 50ms (DB) = 1450ms overhead budget

**Optimization Strategies**:
1. **Database connection pooling**: SQLAlchemy pool_size=10, max_overflow=20
2. **Index optimization**: (user_id, status) and (user_id, created_at DESC)
3. **Async operations**: FastAPI async endpoints, async Cohere SDK calls
4. **Response streaming**: Optional for long responses (Phase 2 optimization)

**Monitoring**:
- Log request duration: `logger.info("Chat request", extra={"duration_ms": duration})`
- Track Cohere API latency separately
- Alert if p95 > 3000ms

**Alternatives Considered**:
1. **Caching Cohere responses** - Violates stateless requirement, low cache hit rate for varied inputs
2. **Self-hosted LLM** - Adds infrastructure complexity, may not meet 95% accuracy target

### 9. Deployment Considerations

**Decision**: Deploy as part of existing FastAPI backend, single container

**Rationale**:
- MCP server embedded in FastAPI process (no separate service)
- Agent code in same codebase (backend/src/agent/)
- Neon PostgreSQL already provisioned (serverless, no scaling needed)
- ChatKit UI already deployed (no frontend changes needed)

**Environment Variables**:
```bash
# .env
DATABASE_URL=postgresql://user:pass@neon.tech/dbname
COHERE_API_KEY=your_cohere_api_key
OPENAI_AGENTS_SDK_KEY=your_sdk_key  # If required
BETTER_AUTH_SECRET=your_auth_secret
```

**Health Checks**:
- `/health` - Existing endpoint, verify FastAPI is running
- `/health/database` - Verify Neon connection
- `/health/cohere` - Optional: verify Cohere API access

**Scaling**:
- Horizontal scaling: FastAPI stateless, scales with load balancer
- Database: Neon serverless auto-scales
- Cohere API: Rate limits per account, monitor quota

### 10. Testing Strategy

**Decision**: Three-layer testing: unit (intent), integration (E2E flows), contract (MCP tools)

**Rationale**:
- Constitution requires test-first development
- Each user story needs acceptance tests
- MCP tools need contract tests (input/output validation)

**Test Layers**:

**Unit Tests** (`backend/tests/unit/`):
- `test_intent.py`: Intent extraction accuracy (mocked Cohere)
- `test_validation.py`: Input validation (title/description limits)
- `test_errors.py`: Error message generation

**Integration Tests** (`backend/tests/integration/`):
- `test_chat_flows.py`: All 6 user stories end-to-end (real database, real Cohere)
- `test_stateless.py`: Verify no state retention across requests
- `test_mcp_integration.py`: Agent → MCP tool → Database flow

**Contract Tests** (`backend/tests/contract/`):
- `test_mcp_tools.py`: JSON schema validation for all 5 tools
- `test_chat_api.py`: /api/chat endpoint schema validation

**Test Data**:
- Fixture users: test_user_1 (id=999), test_user_2 (id=998)
- Fixture tasks: Pre-populated test tasks for list/complete/delete tests
- Database: Separate test database, reset between tests

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| AI Framework | OpenAI Agents SDK + Cohere | Standardized tool calling, strong NLU, meets 95% accuracy target |
| State Management | MCP Server with 5 tools | Clean separation, enforces statelessness, reusable tools |
| Architecture | Stateless request/response | FR-003 requirement, simplifies scaling and testing |
| Database | Existing todos table + SQLModel | Reuse infrastructure, prevent SQL injection, indexed queries |
| Authentication | Better Auth middleware | Leverage existing auth, user_id isolation, secure sessions |
| Frontend | Minimal ChatKit changes | API endpoint update only, no UI changes needed |
| Error Handling | Three-tier (agent/tool/user) | User-friendly messages, comprehensive logging, observability |
| Performance | Async + pooling + indexing | Meet <3s target despite Cohere API latency |
| Deployment | Embedded MCP in FastAPI | Single container, no new services, simple deployment |
| Testing | Unit + integration + contract | Constitution compliance, all user stories covered |

## Next Steps (Phase 1)

1. Generate `data-model.md` with database schema verification
2. Create MCP tool contracts in `contracts/mcp-tools.json`
3. Create chatbot API contract in `contracts/chat-api.yaml`
4. Generate `quickstart.md` with setup instructions
5. Update agent context with new technologies

## Open Questions

None - all technical decisions resolved. Constitution violation (Phase III technologies) documented in Complexity Tracking table with justification.
