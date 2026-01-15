---
id: 003
title: Generate Todo AI Chatbot Implementation Tasks
stage: tasks
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: DELL
command: /sp.tasks
labels: ["tasks", "tdd", "user-stories", "mcp-tools", "agent", "implementation"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-ai-chatbot/tasks.md
tests:
  - TDD approach: All tests defined to be written before implementation per constitution
---

## Prompt

```
/sp.tasks

Break the plan into small, ordered implementation tasks.

Each task should:
- Be atomic and testable
- Clearly mention inputs and outputs
- Reference MCP tools or Agent behavior where relevant
- Include database interactions explicitly
- Avoid manual coding assumptions

Tasks must cover:
- MCP server
- Agent configuration
- Chat endpoint
- Database models
- Tool-calling logic
- Conversation persistence
- Error handling
```

## Response snapshot

Generated comprehensive implementation tasks organized by user story priority (6 stories, P1-P3):

**Task Breakdown** (102 total tasks):

1. **Phase 1: Setup** (6 tasks)
   - Install Python dependencies (openai-agents-sdk, cohere, mcp-sdk)
   - Configure environment (.env with COHERE_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET)
   - Verify database schema (todos table)
   - Create directory structures (backend/src/mcp/, backend/src/agent/, backend/tests/)

2. **Phase 2: Foundational** (6 tasks - BLOCKING)
   - Verify SQLModel Todo model with validation (200-char title, 1000-char description)
   - Verify Better Auth middleware (get_current_user)
   - Implement MCP tool schemas from contracts/mcp-tools.json
   - Create error handling utilities (user-friendly messages per FR-010)
   - Configure structured logging (no stack traces to users)
   - Setup database connection pooling (pool_size=10, max_overflow=20)

3. **Phase 3: User Story 1 - Add Todo via NL** (P1, 19 tasks) 🎯 MVP
   - Tests (4): Contract test for add_task, integration tests for E2E flows, unit test for validation
   - Implementation (15): add_task MCP tool, validation, error handling, MCP server init, chatbot with Cohere, intent extraction, response formatting, POST /api/chat endpoint, auth integration

4. **Phase 4: User Story 2 - List Todos via NL** (P1, 13 tasks) ✅ MVP Extension
   - Tests (4): Contract test for list_tasks, integration tests for various scenarios (empty list, filtering)
   - Implementation (9): list_tasks MCP tool, user isolation, status filtering, empty handling, intent detection, response formatting

5. **Phase 5: User Story 3 - Complete Todo via NL** (P2, 13 tasks)
   - Tests (4): Contract test, completion scenarios, error cases (not found, already completed)
   - Implementation (9): complete_task MCP tool, ownership validation, error handling, intent detection, task identifier extraction

6. **Phase 6: User Story 4 - Delete Todo via NL** (P2, 10 tasks)
   - Tests (3): Contract test, deletion scenarios, error cases
   - Implementation (7): delete_task MCP tool, ownership validation, error handling, intent detection

7. **Phase 7: User Story 5 - Update Todo via NL** (P3, 13 tasks)
   - Tests (4): Contract test, update scenarios (title, description, validation)
   - Implementation (9): update_task MCP tool, field validation, error handling, intent detection

8. **Phase 8: User Story 6 - Answer Questions** (P3, 8 tasks)
   - Tests (3): Analytical queries (count, oldest task, user info)
   - Implementation (5): Query intent detection, analytical response formatting, stats calculation

9. **Phase 9: Polish & Cross-Cutting** (14 tasks)
   - Stateless verification test (no context retention)
   - Performance test (<3s response time per SC-005)
   - User isolation test (SC-008 verification)
   - Rate limiting, intent accuracy logging, frontend integration
   - Ambiguous/multiple intent handling
   - Full test suite validation, code cleanup, documentation

**Task Format Compliance**:
- All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story] Description with file path`
- 35 tasks marked [P] for parallel execution
- 102 sequential task IDs (T001-T102)
- User story labels applied (US1-US6)
- File paths specified for all implementation tasks

**Dependencies & Execution Order**:
- Setup (Phase 1) → Foundational (Phase 2) → User Stories (Phase 3-8) in parallel or sequential → Polish (Phase 9)
- Foundational phase BLOCKS all user stories (critical infrastructure)
- Each user story independently testable after foundational phase
- MVP scope: US1 + US2 = 32 tasks (add + list tasks)

**Test-Driven Development**:
- Constitution requirement: Tests written FIRST, verified to FAIL before implementation
- 22 test tasks total across all user stories
- Tests organized: contract (MCP tool schemas), integration (E2E flows), unit (validation, errors)
- Test organization: backend/tests/contract/, backend/tests/integration/, backend/tests/unit/

**Key Architectural Decisions Reflected in Tasks**:
- Stateless architecture enforced: Agent never touches database (T017-T088 use MCP tools only)
- User isolation: All MCP tools filter by user_id (T037, T050, T062, T075)
- Error handling: User-friendly messages, no stack traces (T021, T029, T051, T063, T076)
- Performance: <3s target including Cohere API latency (T090)
- TDD: All tests before implementation (T013-T016 before T017-T031, etc.)

## Outcome

- ✅ Impact: Complete task breakdown ready for implementation (/sp.implement or manual execution)
- 🧪 Tests: 22 test tasks defined across 3 layers (contract, integration, unit); TDD enforced
- 📁 Files: 1 file created (tasks.md with 102 tasks)
- 🔁 Next prompts: `/sp.implement` (execute tasks automatically) or manual implementation following task order
- 🧠 Reflection: Tasks comprehensively cover all 6 user stories with clear dependencies, independent test criteria, and parallel opportunities. MVP scope (US1+US2) enables incremental delivery. Constitution TDD requirement enforced - all tests before implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation completed successfully
- Graders run and results (PASS/FAIL): Format validation - PASS (all 102 tasks follow checklist format with IDs, story labels, file paths)
- Prompt variant (if applicable): N/A (standard /sp.tasks workflow with TDD emphasis)
- Next experiment (smallest change to try): Begin implementation with Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1 MVP), or use /sp.implement for automated execution
