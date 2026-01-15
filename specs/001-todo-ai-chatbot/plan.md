# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a stateless AI chatbot that manages todo tasks through natural language conversations. The chatbot integrates with existing ChatKit UI frontend, uses FastAPI backend with OpenAI Agents SDK (Cohere model) for intent recognition, delegates all state operations to MCP server tools, and persists data to Neon PostgreSQL via SQLModel. The architecture enforces complete statelessness - agent makes no decisions beyond routing user messages to appropriate MCP tools.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js (frontend - existing ChatKit)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, Better Auth, Cohere API
**Storage**: Neon Serverless PostgreSQL (SQLModel ORM)
**Testing**: pytest (backend integration + unit tests), Jest/React Testing Library (frontend if needed)
**Target Platform**: Web application (Linux server deployment)
**Project Type**: Web (existing Next.js frontend + Python FastAPI backend)
**Performance Goals**: <3s response time (p95), 100 concurrent users, 95% intent recognition accuracy
**Constraints**: Stateless per request, MCP tool delegation mandatory, 200-char task title / 1000-char description limits
**Scale/Scope**: 100+ concurrent users, 6 user stories (P1-P3), 5 MCP tools, 14 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Compliance

**Current Phase**: Phase II - Full-Stack Web Application

**Allowed Technologies (Phase II)**:
- ✅ Backend: Python REST API (FastAPI)
- ✅ Database: Neon Serverless PostgreSQL
- ✅ ORM/Data Layer: SQLModel
- ✅ Frontend: Next.js (React, TypeScript) - existing ChatKit UI
- ✅ Authentication: Better Auth (email-based)
- ✅ Architecture: Full-stack web application

**Phase II Restrictions**:
- ❌ MUST NOT use AI frameworks, agents, or orchestration tools
- ❌ MUST NOT introduce cloud infrastructure beyond basic hosting

**VIOLATION DETECTED**:
- **OpenAI Agents SDK**: This is an AI agent framework, which is PROHIBITED in Phase II per constitution
- **MCP Server**: This is an orchestration tool for AI agents, which is PROHIBITED in Phase II per constitution
- **Cohere API**: This is an AI model service, which is PROHIBITED in Phase II per constitution

**Status**: ❌ CONSTITUTION CHECK FAILED - Feature requires Phase III technologies

**Required Justification**: This feature fundamentally requires AI agent technology (OpenAI Agents SDK + Cohere) and MCP orchestration to achieve natural language understanding and intent recognition. Without these, the chatbot cannot interpret user messages like "Add a task to buy groceries" or "Show me my incomplete tasks."

**Options**:
1. **Amend Constitution**: Transition to Phase III to allow AI frameworks (requires constitution amendment and approval)
2. **Redesign Feature**: Replace AI agent with rule-based pattern matching (severely limited NLU, may not meet SC-003: 95% intent recognition)
3. **Defer Feature**: Wait for Phase III before implementing AI chatbot

**Recommendation**: Amend constitution to Phase III for this feature branch only, as the core requirement (natural language task management) cannot be achieved with Phase II technologies.

### Test-First Development

**Status**: ✅ PASS (Conditional on Phase Resolution)

- Acceptance tests will be written for all 6 user stories (P1-P3) before implementation
- API contract tests required for chatbot endpoint and MCP tools
- Integration tests required for stateless agent flow, MCP tool calls, database persistence
- Unit tests required for intent extraction, parameter parsing, error handling

**Test Organization**:
- `backend/tests/contract/` - MCP tool contracts, agent API schema
- `backend/tests/integration/` - End-to-end chat flows, database operations
- `backend/tests/unit/` - Intent parsing, validation logic, error handlers

### Security Requirements

**Status**: ✅ PASS

- ✅ Better Auth integration for user authentication (Phase II allowed)
- ✅ User isolation via user_id validation (FR-008)
- ✅ SQL injection prevention via SQLModel ORM parameterized queries
- ✅ Input validation (200-char title, 1000-char description limits)
- ✅ Error messages sanitized (FR-010: no stack traces to users)
- ✅ Authentication context provides user_id for all operations (FR-004)

**Additional Security Measures**:
- All chatbot requests must validate authenticated user session
- MCP tools must validate user_id matches authenticated session
- Database queries must filter by user_id (never return other users' tasks)
- Rate limiting recommended for chatbot endpoint (prevent abuse)

### Code Quality

**Status**: ✅ PASS

- Python type hints required (mypy validation)
- Black + Ruff formatting enforced
- FastAPI automatic OpenAPI documentation
- Maximum function length: 50 lines (enforced in code review)
- Stateless architecture simplifies testing and debugging

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── spec.md              # Feature specification (created by /sp.specify)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (MCP tool definitions, API schemas)
│   ├── mcp-tools.json   # MCP server tool schemas
│   └── chat-api.yaml    # Chatbot API endpoint contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── todo.py           # SQLModel Todo entity
│   ├── services/
│   │   ├── auth_service.py   # Better Auth integration (existing)
│   │   └── todo_service.py   # CRUD operations (existing)
│   ├── mcp/
│   │   ├── server.py         # MCP server initialization
│   │   ├── tools.py          # MCP tool definitions (add_task, list_tasks, etc.)
│   │   └── schemas.py        # Tool input/output schemas
│   ├── agent/
│   │   ├── chatbot.py        # OpenAI Agents SDK + Cohere integration
│   │   ├── intent.py         # Intent extraction logic
│   │   └── response.py       # Response formatting
│   ├── routers/
│   │   ├── auth.py           # Auth endpoints (existing)
│   │   ├── todos.py          # Todo REST endpoints (existing)
│   │   └── chat.py           # NEW: Chatbot endpoint
│   ├── config.py             # Environment config, DB connection
│   └── main.py               # FastAPI app initialization
└── tests/
    ├── contract/
    │   ├── test_mcp_tools.py       # MCP tool contract tests
    │   └── test_chat_api.py        # Chat API schema tests
    ├── integration/
    │   ├── test_chat_flows.py      # End-to-end user stories
    │   ├── test_stateless.py       # Verify no state retention
    │   └── test_mcp_integration.py # Agent + MCP tool integration
    └── unit/
        ├── test_intent.py          # Intent extraction unit tests
        ├── test_validation.py      # Input validation tests
        └── test_errors.py          # Error handling tests

frontend/  # Existing ChatKit UI
├── src/
│   ├── components/
│   │   └── chat/
│   │       └── ChatInterface.tsx  # Existing ChatKit component
│   └── pages/
│       └── chat.tsx               # Chat page (may need API integration update)
└── tests/  # Frontend tests (if needed)

.env                    # Environment variables (Neon DB, Cohere API key)
alembic/                # Database migrations (existing)
pyproject.toml          # Python dependencies
package.json            # Frontend dependencies (existing)
```

**Structure Decision**: Web application structure selected (Option 2). Backend in `backend/` with new directories: `mcp/` for MCP server tools, `agent/` for AI agent logic, updated `routers/` for chat endpoint. Frontend in `frontend/` uses existing ChatKit UI with potential API integration updates.

## Complexity Tracking

> **Constitution Violations Requiring Justification**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **OpenAI Agents SDK** (AI framework) | Core requirement FR-002: identify user intent from natural language. Success criteria SC-003: 95% intent recognition accuracy cannot be achieved without AI/ML model. | Rule-based pattern matching (regex) would achieve <50% accuracy for varied natural language inputs like "remind me to X", "add task Y", "what are my todos", etc. Fails SC-003. |
| **MCP Server** (orchestration) | Architecture explicitly specified by user: "MCP Server: Official MCP SDK exposing task tools". Stateless architecture requirement (FR-003, FR-005) benefits from MCP's tool abstraction pattern. | Direct database calls in agent code violates FR-005 (no internal state management) and creates tight coupling. MCP provides clean separation between agent (intent) and persistence (tools). |
| **Cohere API** (AI model service) | Specified in requirements: "AI Framework: OpenAI Agents SDK (model: Cohere)". Natural language understanding requires LLM. | Pre-trained intent classifiers (e.g., sklearn) lack generalization for open-ended task descriptions and analytical questions (User Story 6). Cannot extract structured parameters from varied inputs. |

**Resolution**: Phase III technologies are **essential** for this feature's core value proposition (natural language task management). Recommend constitution amendment to allow AI frameworks for this specific feature branch, or defer feature until Phase III transition.
