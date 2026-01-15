---
id: 002
title: Generate Todo AI Chatbot Implementation Plan
stage: plan
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: DELL
command: /sp.plan
labels: ["planning", "architecture", "mcp", "ai-agent", "cohere", "stateless"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-ai-chatbot/plan.md
  - specs/001-todo-ai-chatbot/research.md
  - specs/001-todo-ai-chatbot/data-model.md
  - specs/001-todo-ai-chatbot/quickstart.md
  - specs/001-todo-ai-chatbot/contracts/mcp-tools.json
  - specs/001-todo-ai-chatbot/contracts/chat-api.yaml
  - CLAUDE.md
tests:
  - N/A (planning phase - tests defined, not yet implemented)
---

## Prompt

```
/sp.plan

Generate a full implementation plan for the Todo AI Chatbot using the above specification.

The plan must include:
- Database schema design
- MCP server setup and tool definitions
- OpenAI Agent SDK configuration using Cohere
- Stateless chat flow implementation
- Conversation persistence strategy
- Authentication integration
- Error handling strategy
- Folder structure for frontend, backend, specs
- Deployment readiness (Neon + ChatKit)

Do NOT write code yet.
Explain the reasoning for each step.
```

## Response snapshot

Generated comprehensive implementation plan for Todo AI Chatbot across Phase 0 (Research) and Phase 1 (Design & Contracts):

**Artifacts Created**:

1. **plan.md** - Master implementation plan with:
   - Technical Context (Python 3.11+, FastAPI, OpenAI Agents SDK, Cohere, MCP SDK, SQLModel, Neon PostgreSQL)
   - Constitution Check (identified Phase III violations: AI frameworks prohibited in Phase II)
   - Project Structure (backend/src/mcp/, backend/src/agent/, backend/src/routers/chat.py)
   - Complexity Tracking (justified OpenAI Agents SDK, MCP Server, Cohere API violations)

2. **research.md** - Technical decisions for 10 areas:
   - OpenAI Agents SDK + Cohere for NLU (95% intent accuracy target)
   - MCP Server architecture (5 tools: add_task, list_tasks, complete_task, delete_task, update_task)
   - Stateless request/response flow (FR-003 enforcement)
   - Reuse existing todos table (no schema changes)
   - Better Auth middleware integration for user_id extraction
   - Minimal ChatKit UI changes (API endpoint update only)
   - Three-tier error handling (agent/tool/user levels)
   - Performance optimization (async, pooling, indexing for <3s target)
   - Single container deployment (MCP embedded in FastAPI)
   - Three-layer testing strategy (unit/integration/contract)

3. **data-model.md** - Database schema design:
   - Reuses existing users and todos tables (no migrations needed)
   - Chat messages ephemeral (not persisted per stateless requirement)
   - SQLModel entity definitions with validation rules
   - Query patterns for all 5 MCP tools
   - User isolation via user_id filtering (SC-008 compliance)
   - Performance: 3 indexes (PK, user_status composite, user_created composite)

4. **contracts/mcp-tools.json** - MCP tool contracts for 5 tools:
   - JSON Schema input/output definitions
   - Error codes and user-friendly messages
   - Security notes (user_id validation, task ownership checks)
   - Performance targets (<50ms per tool call)

5. **contracts/chat-api.yaml** - OpenAPI specification:
   - POST /api/chat endpoint
   - Request/response schemas
   - Error responses (400, 401, 429, 500, 503)
   - Security (Better Auth session cookie)
   - Examples for all 6 user story scenarios

6. **quickstart.md** - Developer setup guide:
   - Environment setup (Python packages, Cohere API key, .env config)
   - Database schema verification
   - Development workflow (implement MCP tools → agent → API endpoint → register router)
   - Running instructions (backend + frontend)
   - Testing checklist (manual + automated)
   - Troubleshooting common issues

7. **CLAUDE.md** - Updated agent context with new technologies

**Constitution Violations Identified**:
- Phase II prohibits AI frameworks, agents, and orchestration tools
- Required violations: OpenAI Agents SDK, MCP Server, Cohere API
- Justification: Core feature requirement (NLU for 95% intent accuracy) cannot be met with Phase II technologies
- Recommendation: Amend constitution to Phase III or defer feature

**Key Architectural Decisions**:
- Stateless architecture enforced: agent has no memory, MCP tools called per request
- User isolation: all queries filtered by user_id from Better Auth session
- Performance budget: <3s total (1500ms Cohere + 50ms DB + 1450ms overhead)
- Error handling: three tiers with user-friendly messages (no stack traces)
- Testing: unit (intent), integration (E2E flows), contract (MCP schemas)

## Outcome

- ✅ Impact: Complete implementation plan ready for task breakdown (/sp.tasks)
- 🧪 Tests: Test strategy defined (3 layers), acceptance tests for all 6 user stories
- 📁 Files: 7 files created (plan, research, data-model, quickstart, 2 contracts, agent context)
- 🔁 Next prompts: `/sp.tasks` (generate testable tasks from plan) or address constitution violation first
- 🧠 Reflection: Plan comprehensively addresses all user requirements with reasoning for each decision. Constitution violation documented with clear justification - requires stakeholder decision before proceeding to implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Constitution check identified Phase II/III conflict - AI frameworks required but prohibited
- Graders run and results (PASS/FAIL): Constitution check - CONDITIONAL PASS (violations justified in Complexity Tracking)
- Prompt variant (if applicable): N/A (standard /sp.plan workflow)
- Next experiment (smallest change to try): Implement task breakdown with /sp.tasks, or request constitution amendment approval from stakeholder
