# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Following TDD approach per constitution requirements - tests written and verified to fail before implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/src/` (per plan.md)
- Tests: `backend/tests/contract/`, `backend/tests/integration/`, `backend/tests/unit/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [ ] T001 Install Python dependencies (openai-agents-sdk, cohere, mcp-sdk) in backend/requirements.txt
- [ ] T002 [P] Configure environment variables (.env) for COHERE_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET
- [ ] T003 [P] Verify database schema exists (todos table with user_id, title, description, status, timestamps)
- [ ] T004 [P] Create backend/src/mcp/ directory structure (server.py, tools.py, schemas.py)
- [ ] T005 [P] Create backend/src/agent/ directory structure (chatbot.py, intent.py, response.py)
- [ ] T006 [P] Create backend/tests/ directory structure (contract/, integration/, unit/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Verify SQLModel Todo model exists in backend/src/models/todo.py with validation (title ≤200 chars, description ≤1000 chars)
- [ ] T008 Verify Better Auth middleware provides get_current_user dependency in backend/src/services/auth_service.py
- [ ] T009 [P] Implement MCP tool input/output schemas in backend/src/mcp/schemas.py using JSON Schema from contracts/mcp-tools.json
- [ ] T010 [P] Create error handling utilities in backend/src/utils/errors.py (NotFoundError, ValidationError, user-friendly messages per FR-010)
- [ ] T011 [P] Configure logging infrastructure in backend/src/config.py (structured JSON logging, no stack traces to users)
- [ ] T012 [P] Setup database connection pooling in backend/src/config.py (pool_size=10, max_overflow=20 per research.md)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Todo via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Logged-in user sends "Add a task to buy groceries" → chatbot creates todo in database → responds "I've added 'buy groceries' to your tasks!"

**Independent Test**: Authenticate user → send natural language add request → verify task in database with user_id → verify friendly confirmation response

### Tests for User Story 1 (TDD - Write First, Ensure FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Contract test for add_task MCP tool in backend/tests/contract/test_mcp_tools.py (validate input schema: user_id, title, description; output schema: success, task_id, message)
- [ ] T014 [P] [US1] Integration test for "Add a task to buy groceries" in backend/tests/integration/test_chat_flows.py (E2E: auth → chat request → verify DB insert → verify response)
- [ ] T015 [P] [US1] Integration test for "Remind me to X with note: Y" in backend/tests/integration/test_chat_flows.py (verify title and description extraction)
- [ ] T016 [P] [US1] Unit test for title/description validation in backend/tests/unit/test_validation.py (200-char title limit, 1000-char description limit)

### Implementation for User Story 1

- [ ] T017 [US1] Implement add_task MCP tool in backend/src/mcp/tools.py (input: user_id, title, description; creates Todo via SQLModel; returns success, task_id, message)
- [ ] T018 [US1] Add title/description validation to add_task tool (enforce 200-char title, 1000-char description limits; raise ValidationError with user-friendly message)
- [ ] T019 [US1] Add user_id validation to add_task tool (verify user_id is valid integer ≥1; prevent SQL injection)
- [ ] T020 [US1] Implement database insertion in add_task (session.add, session.commit, session.refresh; handle database errors with user-friendly messages per FR-010)
- [ ] T021 [US1] Add error handling to add_task tool (catch ValidationError, DatabaseError; return user-friendly messages; log errors with context)
- [ ] T022 [US1] Initialize MCP server in backend/src/mcp/server.py (import add_task tool; register with MCP SDK; expose via HTTP/SSE)
- [ ] T023 [US1] Implement OpenAI Agents SDK chatbot in backend/src/agent/chatbot.py (initialize Cohere client; configure agent with MCP tools; system prompt: "You are a friendly todo assistant, stateless, call tools")
- [ ] T024 [US1] Implement intent extraction in backend/src/agent/intent.py (use Cohere to detect "add_task" intent; extract title and description from natural language)
- [ ] T025 [US1] Implement response formatting in backend/src/agent/response.py (convert tool results to friendly messages: "I've added 'X' to your tasks!")
- [ ] T026 [US1] Create chat API endpoint POST /api/chat in backend/src/routers/chat.py (depends on get_current_user; initialize chatbot with user_id; process message; return ChatResponse)
- [ ] T027 [US1] Add input validation to chat endpoint (validate request.text: 1-1000 chars; return 400 error with user-friendly message if invalid)
- [ ] T028 [US1] Add authentication to chat endpoint (use Depends(get_current_user); extract user_id from session; pass to chatbot)
- [ ] T029 [US1] Add error handling to chat endpoint (catch agent errors; return 500 with user-friendly message per FR-010; log errors with user_id context)
- [ ] T030 [US1] Register chat router in backend/src/main.py (app.include_router(chat.router))
- [ ] T031 [US1] Verify tests pass for US1 (run pytest backend/tests/contract/test_mcp_tools.py::test_add_task, backend/tests/integration/test_chat_flows.py::test_add_task_*)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks via natural language

---

## Phase 4: User Story 2 - List Todos via Natural Language (Priority: P1)

**Goal**: Logged-in user asks "What are my tasks?" → chatbot retrieves all user's tasks from database → responds with formatted list

**Independent Test**: Pre-populate user's tasks in database → authenticate user → send natural language list request → verify all tasks returned in response

### Tests for User Story 2 (TDD - Write First, Ensure FAIL)

- [ ] T032 [P] [US2] Contract test for list_tasks MCP tool in backend/tests/contract/test_mcp_tools.py (validate input schema: user_id, status filter; output schema: tasks array, count)
- [ ] T033 [P] [US2] Integration test for "What are my tasks?" in backend/tests/integration/test_chat_flows.py (pre-populate 3 tasks → verify all 3 returned)
- [ ] T034 [P] [US2] Integration test for empty task list in backend/tests/integration/test_chat_flows.py (no tasks → verify friendly message: "You don't have any tasks yet")
- [ ] T035 [P] [US2] Integration test for "Show me my incomplete tasks" in backend/tests/integration/test_chat_flows.py (mix of pending/completed → verify only pending returned)

### Implementation for User Story 2

- [ ] T036 [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py (input: user_id, status filter; query todos WHERE user_id=? AND status=?; ORDER BY created_at DESC; return tasks array, count)
- [ ] T037 [US2] Add user isolation to list_tasks (enforce WHERE user_id = ? in query; prevent cross-user data leakage per FR-008, SC-008)
- [ ] T038 [US2] Add status filtering to list_tasks (if status provided: filter by "pending" or "completed"; if null: return all tasks)
- [ ] T039 [US2] Add empty list handling to list_tasks (if count=0: return empty array with count=0; agent will format friendly message)
- [ ] T040 [US2] Register list_tasks tool with MCP server in backend/src/mcp/server.py
- [ ] T041 [US2] Update intent extraction to detect "list_tasks" intent in backend/src/agent/intent.py (recognize "what are my tasks", "show tasks", "list todos", etc.)
- [ ] T042 [US2] Update response formatting for list results in backend/src/agent/response.py (format tasks as numbered list: "1. Buy groceries (pending)\n2. Call mom (completed)")
- [ ] T043 [US2] Add empty list response formatting in backend/src/agent/response.py (if count=0: "You don't have any tasks yet. Would you like to add one?")
- [ ] T044 [US2] Verify tests pass for US2 (run pytest backend/tests/contract/test_mcp_tools.py::test_list_tasks, backend/tests/integration/test_chat_flows.py::test_list_tasks_*)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can add and list tasks

---

## Phase 5: User Story 3 - Complete Todo via Natural Language (Priority: P2)

**Goal**: Logged-in user says "Mark 'buy groceries' as done" → chatbot updates task status to completed → responds "Great! I've marked 'buy groceries' as completed."

**Independent Test**: Create pending task → authenticate → send completion request → verify task status=completed in database → verify confirmation response

### Tests for User Story 3 (TDD - Write First, Ensure FAIL)

- [ ] T045 [P] [US3] Contract test for complete_task MCP tool in backend/tests/contract/test_mcp_tools.py (validate input schema: user_id, task_id; output schema: success, message)
- [ ] T046 [P] [US3] Integration test for "Mark 'buy groceries' as done" in backend/tests/integration/test_chat_flows.py (create task → complete by title → verify status=completed)
- [ ] T047 [P] [US3] Integration test for completing non-existent task in backend/tests/integration/test_chat_flows.py (verify friendly error: "I couldn't find that task")
- [ ] T048 [P] [US3] Integration test for completing already-completed task in backend/tests/integration/test_chat_flows.py (verify message: "That task is already marked as complete!")

### Implementation for User Story 3

- [ ] T049 [US3] Implement complete_task MCP tool in backend/src/mcp/tools.py (input: user_id, task_id; fetch task WHERE id=? AND user_id=?; set status=completed; update updated_at; return success, message)
- [ ] T050 [US3] Add task ownership validation to complete_task (verify task.user_id == user_id; raise Forbidden if mismatch per FR-008)
- [ ] T051 [US3] Add not-found handling to complete_task (if task not found: raise NotFoundError with message: "I couldn't find that task. Would you like to see your current tasks?")
- [ ] T052 [US3] Add already-completed check to complete_task (if task.status == "completed": return message "That task is already marked as complete!" without error)
- [ ] T053 [US3] Register complete_task tool with MCP server in backend/src/mcp/server.py
- [ ] T054 [US3] Update intent extraction to detect "complete_task" intent in backend/src/agent/intent.py (recognize "mark X as done", "complete task", "finish X", etc.; extract task identifier)
- [ ] T055 [US3] Add task identifier extraction in backend/src/agent/intent.py (extract task title or index from natural language; call list_tasks first if needed to resolve)
- [ ] T056 [US3] Update response formatting for completion in backend/src/agent/response.py ("Great! I've marked 'X' as completed.")
- [ ] T057 [US3] Verify tests pass for US3 (run pytest backend/tests/contract/test_mcp_tools.py::test_complete_task, backend/tests/integration/test_chat_flows.py::test_complete_task_*)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can add, list, and complete tasks

---

## Phase 6: User Story 4 - Delete Todo via Natural Language (Priority: P2)

**Goal**: Logged-in user says "Delete my task about groceries" → chatbot removes task from database → responds "I've deleted the 'buy groceries' task."

**Independent Test**: Create task → authenticate → send delete request → verify task removed from database → verify confirmation response

### Tests for User Story 4 (TDD - Write First, Ensure FAIL)

- [ ] T058 [P] [US4] Contract test for delete_task MCP tool in backend/tests/contract/test_mcp_tools.py (validate input schema: user_id, task_id; output schema: success, message)
- [ ] T059 [P] [US4] Integration test for "Delete the groceries task" in backend/tests/integration/test_chat_flows.py (create task → delete by title → verify task removed from DB)
- [ ] T060 [P] [US4] Integration test for deleting non-existent task in backend/tests/integration/test_chat_flows.py (verify friendly error: "I couldn't find a task matching that")

### Implementation for User Story 4

- [ ] T061 [US4] Implement delete_task MCP tool in backend/src/mcp/tools.py (input: user_id, task_id; fetch task WHERE id=? AND user_id=?; session.delete(task); session.commit; return success, message)
- [ ] T062 [US4] Add task ownership validation to delete_task (verify task.user_id == user_id; raise Forbidden if mismatch per FR-008)
- [ ] T063 [US4] Add not-found handling to delete_task (if task not found: raise NotFoundError with message: "I couldn't find a task matching that. Your tasks are still intact.")
- [ ] T064 [US4] Register delete_task tool with MCP server in backend/src/mcp/server.py
- [ ] T065 [US4] Update intent extraction to detect "delete_task" intent in backend/src/agent/intent.py (recognize "delete X", "remove task", "get rid of X", etc.; extract task identifier)
- [ ] T066 [US4] Update response formatting for deletion in backend/src/agent/response.py ("I've deleted the 'X' task.")
- [ ] T067 [US4] Verify tests pass for US4 (run pytest backend/tests/contract/test_mcp_tools.py::test_delete_task, backend/tests/integration/test_chat_flows.py::test_delete_task_*)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - users can add, list, complete, and delete tasks

---

## Phase 7: User Story 5 - Update Todo via Natural Language (Priority: P3)

**Goal**: Logged-in user says "Change my groceries task to 'buy groceries and milk'" → chatbot updates task title → responds "I've updated your task to 'buy groceries and milk'."

**Independent Test**: Create task → authenticate → send update request → verify task title/description changed in database → verify confirmation response

### Tests for User Story 5 (TDD - Write First, Ensure FAIL)

- [ ] T068 [P] [US5] Contract test for update_task MCP tool in backend/tests/contract/test_mcp_tools.py (validate input schema: user_id, task_id, title?, description?; output schema: success, message)
- [ ] T069 [P] [US5] Integration test for "Change X to Y" in backend/tests/integration/test_chat_flows.py (create task → update title → verify new title in DB)
- [ ] T070 [P] [US5] Integration test for "Add note to X: Y" in backend/tests/integration/test_chat_flows.py (create task → update description → verify description in DB)
- [ ] T071 [P] [US5] Integration test for updating with no fields provided in backend/tests/integration/test_chat_flows.py (verify validation error: "At least one field must be provided")

### Implementation for User Story 5

- [ ] T072 [US5] Implement update_task MCP tool in backend/src/mcp/tools.py (input: user_id, task_id, title?, description?; fetch task WHERE id=? AND user_id=?; update fields; set updated_at; return success, message)
- [ ] T073 [US5] Add field validation to update_task (require at least one of title or description; raise ValidationError if both null)
- [ ] T074 [US5] Add title/description limits to update_task (enforce 200-char title, 1000-char description; raise ValidationError with user-friendly message)
- [ ] T075 [US5] Add task ownership validation to update_task (verify task.user_id == user_id; raise Forbidden if mismatch per FR-008)
- [ ] T076 [US5] Add not-found handling to update_task (if task not found: raise NotFoundError with message: "I couldn't find that task to update")
- [ ] T077 [US5] Register update_task tool with MCP server in backend/src/mcp/server.py
- [ ] T078 [US5] Update intent extraction to detect "update_task" intent in backend/src/agent/intent.py (recognize "change X to Y", "update task", "add note", etc.; extract task identifier and new values)
- [ ] T079 [US5] Update response formatting for updates in backend/src/agent/response.py ("I've updated your task to 'X'." or "I've added the note to your task.")
- [ ] T080 [US5] Verify tests pass for US5 (run pytest backend/tests/contract/test_mcp_tools.py::test_update_task, backend/tests/integration/test_chat_flows.py::test_update_task_*)

**Checkpoint**: At this point, User Stories 1-5 should all work independently - full CRUD via natural language

---

## Phase 8: User Story 6 - Answer Questions About User and Tasks (Priority: P3)

**Goal**: Logged-in user asks "How many tasks do I have?" → chatbot analyzes tasks → responds "You have 5 tasks total: 3 pending and 2 completed."

**Independent Test**: Pre-populate tasks with metadata → authenticate → ask analytical question → verify accurate response with counts/details

### Tests for User Story 6 (TDD - Write First, Ensure FAIL)

- [ ] T081 [P] [US6] Integration test for "How many tasks do I have?" in backend/tests/integration/test_chat_flows.py (pre-populate 5 tasks: 3 pending, 2 completed → verify response has correct counts)
- [ ] T082 [P] [US6] Integration test for "What's my oldest pending task?" in backend/tests/integration/test_chat_flows.py (pre-populate tasks with timestamps → verify correct task returned)
- [ ] T083 [P] [US6] Integration test for "Who am I?" in backend/tests/integration/test_chat_flows.py (verify response contains user email from auth context)

### Implementation for User Story 6

- [ ] T084 [US6] Update intent extraction to detect "query" intent in backend/src/agent/intent.py (recognize "how many", "show stats", "who am I", "oldest task", etc.)
- [ ] T085 [US6] Implement query handling in backend/src/agent/chatbot.py (for "how many": call list_tasks → count by status → format response; for "oldest": call list_tasks → sort by created_at → return first)
- [ ] T086 [US6] Add user info response in backend/src/agent/response.py (for "who am I": use current_user.email from auth context)
- [ ] T087 [US6] Add analytical response formatting in backend/src/agent/response.py ("You have X tasks total: Y pending and Z completed." or "Your oldest pending task is 'X' from [date].")
- [ ] T088 [US6] Verify tests pass for US6 (run pytest backend/tests/integration/test_chat_flows.py::test_query_*)

**Checkpoint**: All user stories should now be independently functional - chatbot has full NLU capabilities

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T089 [P] Add stateless verification test in backend/tests/integration/test_stateless.py (send 2 requests → verify agent doesn't retain context; verify no session storage)
- [ ] T090 [P] Add performance test in backend/tests/integration/test_performance.py (verify response time <3s for 95% of requests per SC-005)
- [ ] T091 [P] Add user isolation test in backend/tests/integration/test_security.py (create tasks for user1 → auth as user2 → verify cannot see user1's tasks per SC-008)
- [ ] T092 [P] Add rate limiting to chat endpoint in backend/src/routers/chat.py (prevent abuse; return 429 if exceeded)
- [ ] T093 [P] Add intent recognition accuracy logging in backend/src/agent/intent.py (log detected intent + confidence for SC-003 verification)
- [ ] T094 [P] Update frontend ChatKit API integration in frontend/src/services/chatService.ts (point to /api/chat endpoint; handle errors)
- [ ] T095 [P] Add error handling test in backend/tests/unit/test_errors.py (verify all error messages are user-friendly; no stack traces per FR-010)
- [ ] T096 [P] Add ambiguous intent handling in backend/src/agent/chatbot.py (if intent unclear: respond "I'm not sure what you want to do. You can add, list, complete, delete, or update tasks.")
- [ ] T097 [P] Add multiple intent detection in backend/src/agent/intent.py (if multiple intents: respond "Let's do one thing at a time. Would you like to [intent1] or [intent2]?")
- [ ] T098 Run full integration test suite (pytest backend/tests/integration/ -v; verify all user stories pass)
- [ ] T099 Run contract test suite (pytest backend/tests/contract/ -v; verify all MCP tool schemas valid)
- [ ] T100 Verify quickstart.md setup guide works (follow all steps; verify backend starts, chat endpoint responds)
- [ ] T101 [P] Code cleanup and refactoring (enforce max 50 lines per function; add type hints; run mypy validation)
- [ ] T102 [P] Documentation updates (update README with chatbot setup; document MCP tools; add architecture diagram)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories ✅ MVP
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories ✅ MVP Extension
- **User Story 3 (P2)**: Can start after Foundational - Independent (may reference US2 for task lookup)
- **User Story 4 (P2)**: Can start after Foundational - Independent (may reference US2 for task lookup)
- **User Story 5 (P3)**: Can start after Foundational - Independent (may reference US2 for task lookup)
- **User Story 6 (P3)**: Can start after Foundational - Independent (uses US2's list_tasks tool)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per constitution)
- Models/schemas before MCP tools
- MCP tools before agent integration
- Agent before API endpoint
- Endpoint before router registration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T006)
- All Foundational tasks marked [P] can run in parallel (T009-T012)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel (within each phase)
- Models/schemas marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T013 - Contract test for add_task MCP tool
Task: T014 - Integration test for "Add a task to buy groceries"
Task: T015 - Integration test for "Remind me to X with note: Y"
Task: T016 - Unit test for title/description validation

# After tests fail, can parallelize some implementation:
Task: T009 - MCP schemas (Foundational, but used by US1)
Task: T010 - Error utilities (Foundational, but used by US1)
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup → Install dependencies, configure environment
2. Complete Phase 2: Foundational (CRITICAL) → Database, auth, MCP infrastructure
3. Complete Phase 3: User Story 1 → Add tasks via natural language
4. Complete Phase 4: User Story 2 → List tasks via natural language
5. **STOP and VALIDATE**: Test US1+US2 independently (add + list is useful MVP)
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Can add tasks!)
3. Add User Story 2 → Test independently → Deploy/Demo (Can add + list tasks! MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo (Can mark complete!)
5. Add User Story 4 → Test independently → Deploy/Demo (Can delete!)
6. Add User Story 5 → Test independently → Deploy/Demo (Can update!)
7. Add User Story 6 → Test independently → Deploy/Demo (Can query stats!)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Add)
   - Developer B: User Story 2 (List)
   - Developer C: User Story 3 (Complete)
3. Stories complete and integrate independently
4. Continue with remaining stories (Delete, Update, Query)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution violation (Phase III technologies) acknowledged - proceed with implementation
- MCP tools enforce stateless architecture (FR-003, FR-005) - agent never touches database directly
- All error messages must be user-friendly (FR-010) - no stack traces, no technical jargon
- User isolation critical (FR-008, SC-008) - every query filtered by user_id
- Performance target: <3s response time (SC-005) - includes Cohere API latency

---

## Task Count Summary

- **Total Tasks**: 102
- **Setup (Phase 1)**: 6 tasks
- **Foundational (Phase 2)**: 6 tasks (BLOCKING)
- **User Story 1 (P1)**: 19 tasks (4 tests + 15 implementation)
- **User Story 2 (P1)**: 13 tasks (4 tests + 9 implementation)
- **User Story 3 (P2)**: 13 tasks (4 tests + 9 implementation)
- **User Story 4 (P2)**: 10 tasks (3 tests + 7 implementation)
- **User Story 5 (P3)**: 13 tasks (4 tests + 9 implementation)
- **User Story 6 (P3)**: 8 tasks (3 tests + 5 implementation)
- **Polish (Phase 9)**: 14 tasks (cross-cutting concerns)

**MVP Scope** (US1 + US2): 32 tasks (12 foundational + 19 US1 + 13 US2 - 12 overlap = 32 unique tasks)

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phase
