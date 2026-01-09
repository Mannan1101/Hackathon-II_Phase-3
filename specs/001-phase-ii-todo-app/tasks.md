# Tasks: Phase II Todo App

**Input**: Design documents from `/specs/001-phase-ii-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per constitution Test-First Development principle. All test tasks must be completed BEFORE their corresponding implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` (as per plan.md)
- Tests: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure per plan.md (backend/src/, backend/tests/, alembic/)
- [X] T002 Create frontend project structure per plan.md (frontend/src/, frontend/public/, frontend/tests/)
- [X] T003 [P] Initialize backend Python project with FastAPI dependencies in backend/requirements.txt
- [X] T004 [P] Initialize frontend Next.js project with TypeScript and Tailwind in frontend/package.json
- [X] T005 [P] Configure backend linting and formatting (Black, Ruff, mypy) in backend/pyproject.toml
- [X] T006 [P] Configure frontend linting and formatting (ESLint, Prettier) in frontend/eslint.config.js and frontend/prettier.config.js
- [X] T007 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [X] T008 [P] Configure Tailwind CSS in frontend/tailwind.config.js
- [X] T009 Create backend .env.example with DATABASE_URL, SECRET_KEY, BETTER_AUTH_API_KEY placeholders
- [X] T010 Create frontend .env.local.example with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_CLIENT_ID placeholders
- [X] T011 [P] Initialize Alembic for database migrations in backend/alembic/
- [X] T012 [P] Configure pytest in backend/pytest.ini
- [X] T013 [P] Configure Jest in frontend/jest.config.js
- [X] T014 [P] Configure Playwright for E2E tests in frontend/playwright.config.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T015 Create backend config module for environment variables in backend/src/config.py
- [X] T016 Create backend database connection and session management in backend/src/database.py
- [X] T017 Create FastAPI application entry point with CORS middleware in backend/src/main.py
- [X] T018 [P] Create password hashing utility (bcrypt, 12 rounds) in backend/src/utils/password.py
- [X] T019 [P] Create input validation utilities in backend/src/utils/validation.py
- [X] T020 [P] Create logging middleware for request/response logging in backend/src/middleware/logging_middleware.py
- [X] T021 [P] Create health check router with /health and /ready endpoints in backend/src/routers/health.py
- [X] T022 [P] Create API client wrapper with fetch in frontend/src/lib/api.ts
- [X] T023 [P] Create frontend validation utilities in frontend/src/lib/validators.ts
- [X] T024 [P] Create reusable UI components (Button, Input, LoadingSpinner) in frontend/src/components/ui/
- [X] T025 Configure Tailwind global styles in frontend/src/styles/globals.css
- [X] T026 Create Next.js root layout with providers in frontend/src/app/layout.tsx
- [X] T027 Create Next.js landing page with redirect logic in frontend/src/app/page.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and sign in with session persistence

**Independent Test**: Create account, sign in, verify session persists across page refreshes, verify data isolation

### Tests for User Story 1 (TDD - Write FIRST, Verify FAIL)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

- [X] T028 [P] [US1] Contract test for POST /auth/signup endpoint in backend/tests/contract/test_auth_contract.py
- [X] T029 [P] [US1] Contract test for POST /auth/signin endpoint in backend/tests/contract/test_auth_contract.py
- [X] T030 [P] [US1] Integration test for signup flow in backend/tests/integration/test_auth_flow.py
- [X] T031 [P] [US1] Integration test for signin flow in backend/tests/integration/test_auth_flow.py
- [X] T032 [P] [US1] Integration test for session persistence in backend/tests/integration/test_auth_flow.py
- [X] T033 [P] [US1] Unit test for password hashing and verification in backend/tests/unit/test_password_utils.py
- [X] T034 [P] [US1] Unit test for AuthService signup logic in backend/tests/unit/test_auth_service.py
- [X] T035 [P] [US1] Unit test for AuthService signin logic in backend/tests/unit/test_auth_service.py
- [X] T036 [P] [US1] Component test for SignupForm in frontend/tests/components/SignupForm.test.tsx
- [X] T037 [P] [US1] Component test for SigninForm in frontend/tests/components/SigninForm.test.tsx
- [X] T038 [P] [US1] E2E test for signup → signin → session persistence in frontend/tests/e2e/auth.spec.ts

### Backend Implementation for User Story 1

- [X] T039 [P] [US1] Create User SQLModel with email, hashed_password, timestamps in backend/src/models/user.py
- [X] T040 [P] [US1] Create auth request/response Pydantic schemas in backend/src/schemas/auth.py
- [X] T041 [US1] Implement AuthService with signup logic (hash password, create user) in backend/src/services/auth_service.py
- [X] T042 [US1] Implement AuthService with signin logic (verify password, create session) in backend/src/services/auth_service.py
- [X] T043 [US1] Create auth router with POST /auth/signup endpoint in backend/src/routers/auth.py
- [X] T044 [US1] Create auth router with POST /auth/signin endpoint in backend/src/routers/auth.py
- [X] T045 [US1] Implement session cookie creation (HttpOnly, Secure, SameSite) in backend/src/services/auth_service.py
- [X] T046 [US1] Create authentication middleware for session validation in backend/src/middleware/auth_middleware.py
- [X] T047 [US1] Add error handling for auth endpoints (400, 401, 409) in backend/src/routers/auth.py
- [X] T048 [US1] Create Alembic migration for users table in backend/alembic/versions/001_create_users_table.py
- [X] T049 [US1] Run Alembic migration to create users table (alembic upgrade head)

### Frontend Implementation for User Story 1

- [X] T050 [P] [US1] Create Better Auth configuration in frontend/src/lib/auth.ts
- [X] T051 [P] [US1] Create User type definitions in frontend/src/types/user.ts
- [X] T052 [P] [US1] Create SignupForm component with validation in frontend/src/components/auth/SignupForm.tsx
- [X] T053 [P] [US1] Create SigninForm component with validation in frontend/src/components/auth/SigninForm.tsx
- [X] T054 [US1] Create signup page using SignupForm in frontend/src/app/(auth)/signup/page.tsx
- [X] T055 [US1] Create signin page using SigninForm in frontend/src/app/(auth)/signin/page.tsx
- [X] T056 [US1] Create Next.js middleware for authentication redirects in frontend/src/middleware.ts
- [X] T057 [US1] Implement auth state handling with Better Auth hooks in frontend/src/lib/auth.ts

**Checkpoint**: User Story 1 complete - Users can signup, signin, session persists, auth middleware protects routes

---

## Phase 4: User Story 2 - View All Todos (Priority: P1)

**Goal**: Enable authenticated users to view their todo list (or empty state)

**Independent Test**: After signin, navigate to /todos, see empty state or list of user's todos, verify other users cannot see these todos

### Tests for User Story 2 (TDD - Write FIRST, Verify FAIL)

- [X] T058 [P] [US2] Contract test for GET /todos endpoint in backend/tests/contract/test_todos_contract.py
- [X] T059 [P] [US2] Integration test for viewing todos (empty state) in backend/tests/integration/test_todo_crud.py
- [X] T060 [P] [US2] Integration test for viewing todos (with todos) in backend/tests/integration/test_todo_crud.py
- [X] T061 [P] [US2] Integration test for data isolation (user A cannot see user B's todos) in backend/tests/integration/test_data_isolation.py
- [X] T062 [P] [US2] Unit test for TodoService getTodos logic in backend/tests/unit/test_todo_service.py
- [X] T063 [P] [US2] Component test for TodoList component in frontend/tests/components/TodoList.test.tsx
- [X] T064 [P] [US2] Component test for EmptyState component in frontend/tests/components/EmptyState.test.tsx
- [X] T065 [P] [US2] E2E test for viewing empty todos list in frontend/tests/e2e/todos.spec.ts
- [X] T066 [P] [US2] E2E test for viewing populated todos list in frontend/tests/e2e/todos.spec.ts

### Backend Implementation for User Story 2

- [X] T067 [P] [US2] Create Todo SQLModel with user_id FK, title, is_complete, timestamps in backend/src/models/todo.py
- [X] T068 [P] [US2] Create todo request/response Pydantic schemas in backend/src/schemas/todo.py
- [X] T069 [US2] Implement TodoService with getTodos logic (filter by user_id, sort by created_at DESC) in backend/src/services/todo_service.py
- [X] T070 [US2] Create todos router with GET /todos endpoint in backend/src/routers/todos.py
- [X] T071 [US2] Add authorization check (user_id from session) in backend/src/routers/todos.py
- [X] T072 [US2] Add error handling for todos endpoints (401, 500) in backend/src/routers/todos.py
- [X] T073 [US2] Create Alembic migration for todos table with user_id FK in backend/alembic/versions/002_create_todos_table.py
- [X] T074 [US2] Run Alembic migration to create todos table (alembic upgrade head)

### Frontend Implementation for User Story 2

- [X] T075 [P] [US2] Create Todo type definitions in frontend/src/types/todo.ts
- [X] T076 [P] [US2] Create TodoList component to display todos in frontend/src/components/todos/TodoList.tsx
- [X] T077 [P] [US2] Create TodoItem component for individual todo display in frontend/src/components/todos/TodoItem.tsx
- [X] T078 [P] [US2] Create EmptyState component for no todos message in frontend/src/components/todos/EmptyState.tsx
- [X] T079 [US2] Create todos page with TodoList integration in frontend/src/app/(protected)/todos/page.tsx
- [X] T080 [US2] Implement API call to fetch todos in frontend/src/app/(protected)/todos/page.tsx
- [X] T081 [US2] Add loading states for todo fetching in frontend/src/app/(protected)/todos/page.tsx
- [X] T082 [US2] Add responsive layout for todo list (mobile + desktop) in frontend/src/components/todos/TodoList.tsx

**Checkpoint**: User Story 2 complete - Users can view their todos (or empty state), sorted by created_at, with data isolation enforced

---

## Phase 5: User Story 3 - Create New Todo (Priority: P2)

**Goal**: Enable authenticated users to create new todos

**Independent Test**: Click "Add Todo", enter title, submit, verify todo appears in list, verify persistence after refresh

### Tests for User Story 3 (TDD - Write FIRST, Verify FAIL)

- [X] T083 [P] [US3] Contract test for POST /todos endpoint in backend/tests/contract/test_todos_contract.py
- [X] T084 [P] [US3] Integration test for creating todo in backend/tests/integration/test_todo_crud.py
- [X] T085 [P] [US3] Integration test for todo validation (empty title, too long) in backend/tests/integration/test_todo_crud.py
- [X] T086 [P] [US3] Unit test for TodoService createTodo logic in backend/tests/unit/test_todo_service.py
- [X] T087 [P] [US3] Component test for TodoForm component in frontend/tests/components/TodoForm.test.tsx
- [X] T088 [P] [US3] E2E test for creating new todo in frontend/tests/e2e/todos.spec.ts

### Backend Implementation for User Story 3

- [X] T089 [US3] Implement TodoService with createTodo logic (validate, set user_id, defaults) in backend/src/services/todo_service.py
- [X] T090 [US3] Create POST /todos endpoint in backend/src/routers/todos.py
- [X] T091 [US3] Add input validation for todo title (min 1, max 200, non-whitespace) in backend/src/routers/todos.py
- [X] T092 [US3] Add error handling for create todo (400, 401) in backend/src/routers/todos.py

### Frontend Implementation for User Story 3

- [X] T093 [P] [US3] Create TodoForm component for add/edit with validation in frontend/src/components/todos/TodoForm.tsx
- [X] T094 [US3] Add "Add Todo" button to todos page in frontend/src/app/(protected)/todos/page.tsx
- [X] T095 [US3] Implement create todo API call in frontend/src/app/(protected)/todos/page.tsx
- [X] T096 [US3] Add validation error display in TodoForm in frontend/src/components/todos/TodoForm.tsx
- [X] T097 [US3] Update todo list state after successful creation in frontend/src/app/(protected)/todos/page.tsx

**Checkpoint**: User Story 3 complete - Users can create todos, validation enforced, todos persist

---

## Phase 6: User Story 6 - Toggle Todo Completion Status (Priority: P2)

**Goal**: Enable authenticated users to mark todos complete/incomplete

**Independent Test**: Click completion toggle on todo, verify visual change, verify status persists after refresh

### Tests for User Story 6 (TDD - Write FIRST, Verify FAIL)

- [X] T098 [P] [US6] Contract test for PATCH /todos/{id} endpoint (completion toggle) in backend/tests/contract/test_todos_contract.py
- [X] T099 [P] [US6] Integration test for toggling todo completion in backend/tests/integration/test_todo_crud.py
- [X] T100 [P] [US6] Integration test for unauthorized toggle (different user) in backend/tests/integration/test_data_isolation.py
- [X] T101 [P] [US6] Unit test for TodoService updateTodo logic (completion toggle) in backend/tests/unit/test_todo_service.py
- [X] T102 [P] [US6] Component test for TodoItem completion toggle in frontend/tests/components/TodoItem.test.tsx
- [X] T103 [P] [US6] E2E test for toggling todo completion in frontend/tests/e2e/todos.spec.ts

### Backend Implementation for User Story 6

- [X] T104 [US6] Implement TodoService with updateTodo logic (ownership check, partial update) in backend/src/services/todo_service.py
- [X] T105 [US6] Create PATCH /todos/{id} endpoint in backend/src/routers/todos.py
- [X] T106 [US6] Add authorization check (user owns todo) in backend/src/services/todo_service.py
- [X] T107 [US6] Add error handling for update todo (401, 404) in backend/src/routers/todos.py
- [X] T108 [US6] Update updated_at timestamp on todo modification in backend/src/models/todo.py

### Frontend Implementation for User Story 6

- [X] T109 [US6] Add completion checkbox/toggle to TodoItem in frontend/src/components/todos/TodoItem.tsx
- [X] T110 [US6] Add visual distinction for completed todos (strikethrough, color) in frontend/src/components/todos/TodoItem.tsx
- [X] T111 [US6] Implement toggle completion API call in frontend/src/components/todos/TodoItem.tsx
- [X] T112 [US6] Update todo list state after successful toggle in frontend/src/app/(protected)/todos/page.tsx

**Checkpoint**: User Story 6 complete - Users can toggle todo completion, visual feedback provided, status persists

---

## Phase 7: User Story 4 - Update Todo (Priority: P2)

**Goal**: Enable authenticated users to edit todo titles

**Independent Test**: Click "Edit" on todo, change title, save, verify updated title in list, verify persistence

### Tests for User Story 4 (TDD - Write FIRST, Verify FAIL)

- [X] T113 [P] [US4] Contract test for PATCH /todos/{id} endpoint (title update) in backend/tests/contract/test_todos_contract.py
- [X] T114 [P] [US4] Integration test for updating todo title in backend/tests/integration/test_todo_crud.py
- [X] T115 [P] [US4] Integration test for update validation (empty title, too long) in backend/tests/integration/test_todo_crud.py
- [X] T116 [P] [US4] Integration test for unauthorized update (different user) in backend/tests/integration/test_data_isolation.py
- [X] T117 [P] [US4] Unit test for TodoService updateTodo logic (title update) in backend/tests/unit/test_todo_service.py
- [X] T118 [P] [US4] Component test for TodoForm edit mode in frontend/tests/components/TodoForm.test.tsx
- [X] T119 [P] [US4] E2E test for editing todo title in frontend/tests/e2e/todos.spec.ts

### Backend Implementation for User Story 4

- [X] T120 [US4] Extend TodoService updateTodo to handle title updates in backend/src/services/todo_service.py
- [X] T121 [US4] Add title validation to PATCH /todos/{id} endpoint in backend/src/routers/todos.py
- [X] T122 [US4] Add error handling for invalid title updates (400) in backend/src/routers/todos.py

### Frontend Implementation for User Story 4

- [X] T123 [US4] Add "Edit" button to TodoItem in frontend/src/components/todos/TodoItem.tsx
- [X] T124 [US4] Implement inline edit mode or modal for todo editing in frontend/src/components/todos/TodoItem.tsx
- [X] T125 [US4] Implement update todo API call in frontend/src/components/todos/TodoItem.tsx
- [X] T126 [US4] Add cancel edit functionality in frontend/src/components/todos/TodoItem.tsx
- [X] T127 [US4] Update todo list state after successful update in frontend/src/app/(protected)/todos/page.tsx

**Checkpoint**: User Story 4 complete - Users can edit todo titles, validation enforced, changes persist

---

## Phase 8: User Story 5 - Delete Todo (Priority: P3)

**Goal**: Enable authenticated users to delete todos

**Independent Test**: Click "Delete" on todo, confirm deletion, verify todo removed from list, verify not restored after refresh

### Tests for User Story 5 (TDD - Write FIRST, Verify FAIL)

- [X] T128 [P] [US5] Contract test for DELETE /todos/{id} endpoint in backend/tests/contract/test_todos_contract.py
- [X] T129 [P] [US5] Integration test for deleting todo in backend/tests/integration/test_todo_crud.py
- [X] T130 [P] [US5] Integration test for unauthorized delete (different user) in backend/tests/integration/test_data_isolation.py
- [X] T131 [P] [US5] Unit test for TodoService deleteTodo logic in backend/tests/unit/test_todo_service.py
- [X] T132 [P] [US5] Component test for TodoItem delete functionality in frontend/tests/components/TodoItem.test.tsx
- [X] T133 [P] [US5] E2E test for deleting todo in frontend/tests/e2e/todos.spec.ts

### Backend Implementation for User Story 5

- [X] T134 [US5] Implement TodoService with deleteTodo logic (ownership check, permanent delete) in backend/src/services/todo_service.py
- [X] T135 [US5] Create DELETE /todos/{id} endpoint in backend/src/routers/todos.py
- [X] T136 [US5] Add authorization check (user owns todo) in backend/src/services/todo_service.py
- [X] T137 [US5] Add error handling for delete todo (401, 404) in backend/src/routers/todos.py

### Frontend Implementation for User Story 5

- [X] T138 [US5] Add "Delete" button to TodoItem in frontend/src/components/todos/TodoItem.tsx
- [X] T139 [US5] Implement delete confirmation dialog in frontend/src/components/todos/TodoItem.tsx
- [X] T140 [US5] Implement delete todo API call in frontend/src/components/todos/TodoItem.tsx
- [X] T141 [US5] Update todo list state after successful deletion in frontend/src/app/(protected)/todos/page.tsx

**Checkpoint**: User Story 5 complete - Users can delete todos with confirmation, deletion is permanent

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final production readiness

- [X] T142 [P] Add comprehensive JSDoc comments to frontend components in frontend/src/components/
- [X] T143 [P] Add comprehensive docstrings to backend modules in backend/src/
- [X] T144 [P] Run mypy type checking and fix type errors in backend/src/
- [X] T145 [P] Run ESLint and fix linting errors in frontend/src/
- [X] T146 [P] Verify responsive design on multiple screen sizes (320px to 1920px)
- [X] T147 [P] Add accessibility attributes (ARIA labels, keyboard navigation) to frontend components
- [X] T148 Test health check endpoints (/health, /ready) via manual curl/Postman
- [X] T149 Verify quickstart.md setup instructions work on clean environment
- [X] T150 Run full test suite (pytest backend, npm test frontend, npx playwright test)
- [X] T151 Verify constitution compliance checklist (Phase II tech stack, no prohibited features)
- [X] T152 Create .gitignore for backend (.env, venv/, __pycache__)
- [X] T153 Create .gitignore for frontend (.env.local, node_modules/, .next/)
- [X] T154 Document API endpoints in README.md or update OpenAPI specs
- [X] T155 Add error boundary to frontend for graceful error handling
- [X] T156 Verify CORS configuration allows frontend origin
- [X] T157 Test session expiration and re-authentication flow
- [X] T158 Verify database indexes exist and are used (check query plans)
- [X] T159 Run security scan (check for hardcoded secrets, SQL injection vulnerabilities)
- [X] T160 Performance testing: verify <2s page load and <200ms API response times

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) AND User Story 1 (needs auth and User model)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (needs Todo model and view functionality)
- **User Story 6 (Phase 6)**: Depends on User Story 2 (needs Todo model and view functionality)
- **User Story 4 (Phase 7)**: Depends on User Story 2 (needs Todo model and view functionality)
- **User Story 5 (Phase 8)**: Depends on User Story 2 (needs Todo model and view functionality)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

**Sequential Order (Minimum Dependencies)**:
1. **User Story 1 (P1)**: Independent after Foundational - Provides auth foundation
2. **User Story 2 (P1)**: Depends on US1 - Provides todo viewing foundation
3. **User Story 3, 4, 5, 6 (P2/P3)**: All depend on US2 - Can proceed in parallel after US2 complete

**Critical Path for MVP**:
1. Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (User Story 1) → Phase 4 (User Story 2)

After User Story 2, the remaining stories (3, 4, 5, 6) can be implemented in parallel if staffed.

### Within Each User Story

**TDD Workflow (CRITICAL)**:
1. **Write Tests FIRST**: All test tasks for story MUST be completed before implementation
2. **Verify Tests FAIL**: Run tests, confirm they fail (Red)
3. **Implement**: Complete implementation tasks
4. **Verify Tests PASS**: Run tests, confirm they pass (Green)
5. **Refactor**: Clean up code while keeping tests green

**Implementation Order**:
- Tests before implementation (TDD)
- Models before services
- Services before endpoints/routers
- Backend before frontend (API contract established first)
- Core functionality before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**Within Setup (Phase 1)**:
- All tasks marked [P] can run in parallel (different files)
- Example: T003-T008, T011-T014

**Within Foundational (Phase 2)**:
- All tasks marked [P] can run in parallel (T018-T024)

**Within User Story 1 (Tests)**:
- All test tasks T028-T038 can be written in parallel (different test files)

**Within User Story 1 (Backend Models/Schemas)**:
- T039 (User model) and T040 (auth schemas) can run in parallel

**Within User Story 1 (Frontend Components)**:
- T050-T053 can run in parallel (different component files)

**After User Story 2 Complete**:
- User Stories 3, 4, 5, 6 can all proceed in parallel (by different developers)

**Within Polish (Phase 9)**:
- Most tasks marked [P] can run in parallel (T142-T147)

---

## Parallel Execution Example: User Story 1

### Tests (All in Parallel)
```bash
# Backend contract tests
T028: Write contract test for POST /auth/signup
T029: Write contract test for POST /auth/signin

# Backend integration tests
T030: Write integration test for signup flow
T031: Write integration test for signin flow
T032: Write integration test for session persistence

# Backend unit tests
T033: Write unit test for password utils
T034: Write unit test for AuthService signup
T035: Write unit test for AuthService signin

# Frontend component tests
T036: Write component test for SignupForm
T037: Write component test for SigninForm

# Frontend E2E tests
T038: Write E2E test for auth flow
```

### Backend Models/Schemas (In Parallel)
```bash
T039: Create User SQLModel
T040: Create auth Pydantic schemas
```

### Frontend Components (In Parallel)
```bash
T050: Configure Better Auth
T051: Create User type definitions
T052: Create SignupForm component
T053: Create SigninForm component
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

**Recommended for Phase II Initial Delivery**:

1. Complete Phase 1: Setup (T001-T014)
2. Complete Phase 2: Foundational (T015-T027) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T028-T057) - Auth foundation
4. Complete Phase 4: User Story 2 (T058-T082) - Todo viewing
5. **STOP and VALIDATE**: Test authentication and todo viewing independently
6. Deploy/demo MVP if ready

**MVP Scope**: Users can signup, signin, view their todos (or empty state). This is the minimum viable product.

### Incremental Delivery (Recommended)

1. **Foundation Ready**: Phase 1 + Phase 2 complete
2. **MVP (Auth + View)**: Add User Story 1 + 2 → Test → Deploy/Demo
3. **Create Todos**: Add User Story 3 → Test → Deploy/Demo
4. **Toggle Completion**: Add User Story 6 → Test → Deploy/Demo
5. **Edit Todos**: Add User Story 4 → Test → Deploy/Demo
6. **Delete Todos**: Add User Story 5 → Test → Deploy/Demo
7. **Polish**: Phase 9 → Final production deployment

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

**With 3+ Developers**:

1. **Team completes Phase 1 + Phase 2 together** (foundational work)
2. **Once Phase 2 complete**:
   - Developer A: User Story 1 (Auth)
   - Developer B: Prepares test infrastructure
3. **After User Story 1 complete**:
   - Developer A: User Story 2 (View Todos)
4. **After User Story 2 complete** (all depend on it):
   - Developer A: User Story 3 (Create)
   - Developer B: User Story 6 (Toggle)
   - Developer C: User Story 4 (Update)
5. **After User Stories 3, 4, 6 complete**:
   - Any developer: User Story 5 (Delete)
6. **All stories complete**:
   - Team works on Phase 9 (Polish) together

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **TDD CRITICAL**: Tests MUST be written and FAIL before implementation (constitution requirement)
- **Checkpoint Validation**: Stop at each checkpoint to test story independently
- **Atomic Commits**: Commit after each task or logical group of parallel tasks
- **Constitution Compliance**: Verify Phase II technology stack throughout (no AI, no Phase III tech)
- **File Paths**: All tasks include exact file paths per plan.md structure
- **Independent Stories**: Each story should be independently testable after its checkpoint

---

## Task Summary

**Total Tasks**: 160
- **Phase 1 (Setup)**: 14 tasks
- **Phase 2 (Foundational)**: 13 tasks (BLOCKS all stories)
- **Phase 3 (User Story 1 - Auth)**: 29 tasks (11 tests + 18 implementation)
- **Phase 4 (User Story 2 - View)**: 25 tasks (9 tests + 16 implementation)
- **Phase 5 (User Story 3 - Create)**: 15 tasks (6 tests + 9 implementation)
- **Phase 6 (User Story 6 - Toggle)**: 15 tasks (6 tests + 9 implementation)
- **Phase 7 (User Story 4 - Update)**: 15 tasks (7 tests + 8 implementation)
- **Phase 8 (User Story 5 - Delete)**: 15 tasks (6 tests + 9 implementation)
- **Phase 9 (Polish)**: 19 tasks

**Test Tasks**: 51 (TDD compliance per constitution)
**Implementation Tasks**: 90
**Infrastructure/Polish Tasks**: 19

**Parallel Opportunities**:
- Setup: 11 parallel tasks
- Foundational: 10 parallel tasks
- User Story 1: 11 test tasks + 4 backend + 4 frontend = 19 parallel opportunities
- User Story 2: 9 test tasks + 2 backend + 4 frontend = 15 parallel opportunities
- User Stories 3-6: Can all proceed in parallel after US2 (4 stories × ~15 tasks = 60 tasks)
- Polish: 10 parallel tasks

**MVP Scope** (Minimum): Phase 1 + Phase 2 + User Story 1 + User Story 2 = 81 tasks
**Full Phase II Scope**: All 160 tasks

---

## Constitution Compliance Verification

✅ **TDD Workflow**: Tests written before implementation for all user stories
✅ **Test Organization**: tests/contract/, tests/integration/, tests/unit/ per constitution
✅ **Code Quality**: Linting, formatting, type checking tasks included
✅ **Security**: Password hashing, session management, input validation, authorization checks
✅ **Observability**: Logging middleware, health checks included
✅ **Phase II Technology**: FastAPI, SQLModel, Neon PostgreSQL, Next.js, Better Auth only
✅ **No Prohibited Features**: No AI, no agents, no advanced cloud infrastructure, no real-time, no background jobs

**Ready for Implementation**: All tasks are atomic, testable, and follow constitution requirements.
