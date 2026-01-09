# Implementation Plan: Phase II Todo App

**Branch**: `001-phase-ii-todo-app` | **Date**: 2026-01-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-phase-ii-todo-app/spec.md`

## Summary

Phase II implements a full-stack todo application with user authentication, CRUD operations, and persistent storage. The system uses a Python REST API backend with FastAPI, Neon Serverless PostgreSQL database with SQLModel ORM, and Next.js (React + TypeScript) frontend with Better Auth for authentication. Users can sign up, sign in, and manage personal todo lists with complete data isolation enforced at the API and database layers.

**Technical Approach**: Stateless REST API architecture with session-based authentication using HTTP-only cookies. Frontend communicates with backend via JSON APIs over HTTPS. Database schema enforces referential integrity between users and todos. Authorization middleware validates user ownership on all todo operations.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x with Next.js 14+ (frontend)
**Primary Dependencies**: FastAPI (backend framework), SQLModel (ORM), Neon PostgreSQL (database), Next.js (frontend framework), Better Auth (authentication library), React 18+ (UI library)
**Storage**: Neon Serverless PostgreSQL (cloud-hosted, managed service)
**Testing**: pytest + pytest-asyncio (backend), Jest + React Testing Library (frontend), Playwright (E2E integration tests)
**Target Platform**: Web application (cross-browser: Chrome, Firefox, Safari, Edge); server-side: Linux/Docker containers
**Project Type**: Web (frontend + backend architecture)
**Performance Goals**: <2s page load time, <200ms API response time (p95), support 100 concurrent users
**Constraints**: <200ms p95 latency for API requests, responsive UI 320px-1920px width, 7-day session persistence
**Scale/Scope**: 100 concurrent users, ~1000 todos per user, single-region deployment, basic hosting infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase II Technology Matrix Compliance

✅ **Backend: Python REST API**
- Using FastAPI framework (Python 3.11+)
- RESTful endpoint design with JSON request/response
- Complies with Phase II backend requirement

✅ **Database: Neon Serverless PostgreSQL**
- Using Neon cloud-hosted PostgreSQL service
- Serverless architecture with automatic scaling
- Complies with Phase II database requirement

✅ **ORM/Data Layer: SQLModel**
- Using SQLModel for Python-PostgreSQL integration
- Provides type-safe database operations with Pydantic validation
- Complies with Phase II ORM requirement

✅ **Frontend: Next.js (React, TypeScript)**
- Using Next.js 14+ with React 18+ and TypeScript 5.x
- App Router for page-level routing
- Complies with Phase II frontend requirement

✅ **Authentication: Better Auth**
- Using Better Auth library for signup/signin flows
- Session-based authentication with HTTP-only cookies
- Complies with Phase II authentication requirement

✅ **Architecture: Full-Stack Web Application**
- Frontend (Next.js) and Backend (FastAPI) as separate services
- RESTful API communication between layers
- Complies with Phase II architecture requirement

### Constraint Compliance

✅ **No AI or Agents**: No machine learning, AI frameworks, or agent-based features
✅ **No Advanced Cloud Infrastructure**: Single-region deployment, no CDN, no load balancing, no orchestration
✅ **No Real-Time Features**: No WebSockets, no Server-Sent Events, no real-time synchronization
✅ **No Background Jobs**: No queues, no scheduled tasks, no async workers
✅ **No Advanced Analytics**: No analytics dashboards, no reporting, no data visualization

### Test-First Development Compliance

✅ **TDD Cycle Defined**: Red-Green-Refactor workflow in tasks
✅ **Test Organization**: `tests/contract/`, `tests/integration/`, `tests/unit/`
✅ **Test Coverage**: Acceptance tests for all user stories, contract tests for all API endpoints, unit tests for business logic

### Code Quality Compliance

✅ **TypeScript Strict Mode**: Enabled in frontend tsconfig.json
✅ **Python Type Hints**: Required in all backend modules, validated with mypy
✅ **Linting**: ESLint + Prettier (frontend), Black + Ruff (backend)
✅ **Documentation**: JSDoc for frontend, docstrings for backend

### Security Compliance

✅ **Password Hashing**: bcrypt with minimum 12 rounds
✅ **Session Management**: HTTP-only cookies with CSRF protection
✅ **Input Validation**: All API inputs validated via Pydantic models
✅ **SQL Injection Prevention**: Parameterized queries via SQLModel ORM
✅ **HTTPS/TLS**: All data in transit encrypted

### Observability Compliance

✅ **Structured Logging**: JSON format for all logs
✅ **Health Checks**: `/health` and `/ready` endpoints
✅ **Performance Metrics**: Request duration, database query time tracking
✅ **Error Logging**: Stack traces, context, user ID (redacted passwords)

**GATE RESULT**: ✅ **PASS** - All constitution requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-ii-todo-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions and best practices)
├── data-model.md        # Phase 1 output (database schema and entity definitions)
├── quickstart.md        # Phase 1 output (local development setup guide)
├── contracts/           # Phase 1 output (API contract definitions)
│   ├── auth.yaml        # Authentication endpoints (signup, signin)
│   └── todos.yaml       # Todo CRUD endpoints
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management (env vars, settings)
│   ├── database.py             # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLModel (email, hashed_password, timestamps)
│   │   └── todo.py             # Todo SQLModel (title, is_complete, user_id FK, timestamps)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # Auth request/response Pydantic models
│   │   └── todo.py             # Todo request/response Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic (signup, signin, session validation)
│   │   └── todo_service.py     # Todo business logic (CRUD operations, ownership validation)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # Auth endpoints: POST /auth/signup, POST /auth/signin
│   │   ├── todos.py            # Todo endpoints: GET/POST/PATCH/DELETE /todos
│   │   └── health.py           # Health check endpoints: GET /health, GET /ready
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py  # Session validation and user extraction
│   │   └── logging_middleware.py  # Request/response logging
│   └── utils/
│       ├── __init__.py
│       ├── password.py         # Password hashing and verification (bcrypt)
│       └── validation.py       # Input validation utilities
├── tests/
│   ├── contract/
│   │   ├── test_auth_contract.py     # Auth API contract tests
│   │   └── test_todos_contract.py    # Todo API contract tests
│   ├── integration/
│   │   ├── test_auth_flow.py         # End-to-end auth flows
│   │   ├── test_todo_crud.py         # End-to-end todo CRUD flows
│   │   └── test_data_isolation.py    # Cross-user data isolation tests
│   └── unit/
│       ├── test_auth_service.py      # Auth service unit tests
│       ├── test_todo_service.py      # Todo service unit tests
│       └── test_password_utils.py    # Password utility unit tests
├── alembic/                          # Database migration scripts
│   ├── versions/
│   │   ├── 001_initial_schema.py     # Create users and todos tables
│   │   └── README
│   └── env.py
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Python project config (Black, Ruff, mypy)
├── pytest.ini                         # pytest configuration
└── README.md                          # Backend setup and API documentation

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                # Root layout (auth provider, global styles)
│   │   ├── page.tsx                  # Landing page (redirect to /signin or /todos)
│   │   ├── (auth)/
│   │   │   ├── signup/
│   │   │   │   └── page.tsx          # Signup page (email/password form)
│   │   │   └── signin/
│   │   │       └── page.tsx          # Signin page (email/password form)
│   │   └── (protected)/
│   │       └── todos/
│   │           └── page.tsx          # Todos page (list, add, edit, delete, toggle)
│   ├── components/
│   │   ├── auth/
│   │   │   ├── SignupForm.tsx        # Signup form component
│   │   │   └── SigninForm.tsx        # Signin form component
│   │   ├── todos/
│   │   │   ├── TodoList.tsx          # Todo list container
│   │   │   ├── TodoItem.tsx          # Individual todo item
│   │   │   ├── TodoForm.tsx          # Add/edit todo form
│   │   │   └── EmptyState.tsx        # Empty todos placeholder
│   │   └── ui/
│   │       ├── Button.tsx            # Reusable button component
│   │       ├── Input.tsx             # Reusable input component
│   │       └── LoadingSpinner.tsx    # Loading indicator
│   ├── lib/
│   │   ├── api.ts                    # API client (fetch wrapper with auth headers)
│   │   ├── auth.ts                   # Better Auth configuration
│   │   └── validators.ts             # Client-side validation utilities
│   ├── types/
│   │   ├── user.ts                   # User type definitions
│   │   └── todo.ts                   # Todo type definitions
│   └── styles/
│       └── globals.css               # Global styles and Tailwind imports
├── public/
│   └── favicon.ico
├── tests/
│   ├── components/
│   │   ├── SignupForm.test.tsx       # Signup form unit tests
│   │   ├── SigninForm.test.tsx       # Signin form unit tests
│   │   └── TodoList.test.tsx         # Todo list unit tests
│   └── e2e/
│       ├── auth.spec.ts              # E2E auth flow tests (Playwright)
│       └── todos.spec.ts             # E2E todo CRUD tests (Playwright)
├── package.json                       # Frontend dependencies
├── tsconfig.json                      # TypeScript config (strict mode)
├── next.config.js                     # Next.js configuration
├── tailwind.config.js                 # Tailwind CSS configuration
├── eslint.config.js                   # ESLint configuration
├── prettier.config.js                 # Prettier configuration
├── jest.config.js                     # Jest configuration
├── playwright.config.ts               # Playwright E2E test configuration
└── README.md                          # Frontend setup and component documentation

.env.example                           # Environment variable template
.gitignore
README.md                              # Root project README
```

**Structure Decision**: Selected **Option 2: Web application** with separate `backend/` and `frontend/` directories. This structure provides clear separation between frontend and backend codebases, enabling independent development, testing, and deployment. Backend uses FastAPI with layered architecture (routers → services → models). Frontend uses Next.js App Router with route groups for auth and protected pages.

## Complexity Tracking

> **No constitution violations detected** - All technology choices and architectural decisions comply with Phase II requirements.

---

## Phase 0: Research & Technology Decisions

See [research.md](research.md) for detailed technology evaluations and best practices.

### Key Decisions

1. **Backend Framework**: FastAPI (chosen over Flask, Django REST Framework)
2. **ORM**: SQLModel (chosen over SQLAlchemy Core, Tortoise ORM)
3. **Frontend Framework**: Next.js 14 with App Router (chosen over Pages Router)
4. **Authentication Strategy**: Session-based with HTTP-only cookies (chosen over JWT tokens)
5. **CSS Framework**: Tailwind CSS (chosen over CSS Modules, Styled Components)
6. **Database Migrations**: Alembic (integrated with SQLModel)
7. **Testing Frameworks**: pytest (backend), Jest + Playwright (frontend)

---

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](data-model.md) for complete entity definitions, relationships, and validation rules.

**Entities**:
- **User**: `id` (UUID), `email` (unique, indexed), `hashed_password` (bcrypt), `created_at`, `updated_at`
- **Todo**: `id` (UUID), `user_id` (FK to User), `title` (max 200 chars), `is_complete` (boolean), `created_at`, `updated_at`

**Relationships**:
- User → Todos (one-to-many, cascade delete)

### API Contracts

See `contracts/auth.yaml` and `contracts/todos.yaml` for OpenAPI specifications.

**Authentication Endpoints**:
- `POST /auth/signup` - Create new user account
- `POST /auth/signin` - Authenticate and create session

**Todo Endpoints**:
- `GET /todos` - Retrieve all user's todos
- `POST /todos` - Create new todo
- `PATCH /todos/{id}` - Update todo title or completion status
- `DELETE /todos/{id}` - Delete todo

**Health Endpoints**:
- `GET /health` - Service health status
- `GET /ready` - Readiness check (database connectivity)

### Local Development Setup

See [quickstart.md](quickstart.md) for step-by-step local development environment setup.

**Prerequisites**: Python 3.11+, Node.js 18+, PostgreSQL client (optional), Neon account
**Setup Steps**: Environment variables, database migrations, dependency installation, running dev servers
**Verification**: Health checks, test execution, API access, frontend access

---

## Architecture Overview

### Backend Architecture (FastAPI)

**Layered Architecture**:
1. **Routers Layer** (`routers/`): HTTP request handling, routing, input validation via Pydantic
2. **Services Layer** (`services/`): Business logic, authorization checks, orchestration
3. **Models Layer** (`models/`): SQLModel entities, database schema, relationships
4. **Middleware Layer** (`middleware/`): Cross-cutting concerns (auth, logging, error handling)

**Request Flow**:
1. HTTP request → Logging middleware (log request)
2. → Auth middleware (validate session, extract user)
3. → Router (parse request, validate input)
4. → Service (business logic, authorization, database operations)
5. → Response (JSON serialization)
6. → Logging middleware (log response)

**Authentication Flow**:
1. User submits credentials → Auth router validates input
2. → Auth service hashes password, queries database
3. → On success: create session, set HTTP-only cookie, return user data
4. → On failure: return 401 Unauthorized with error message

**Authorization Strategy**:
- Auth middleware extracts `user_id` from session cookie on every request
- Todo service validates `todo.user_id == current_user_id` before operations
- Database foreign key constraints enforce referential integrity

### Frontend Architecture (Next.js)

**Component Hierarchy**:
1. **Pages** (`app/`): Route-level components, data fetching, layout composition
2. **Feature Components** (`components/auth/`, `components/todos/`): Domain-specific components
3. **UI Components** (`components/ui/`): Reusable presentational components
4. **Utilities** (`lib/`): API client, auth helpers, validators

**State Management**:
- **Authentication State**: Better Auth React hooks (`useSession`, `useAuth`)
- **Todo State**: React `useState` + `useEffect` with API calls (no global state library needed for Phase II)
- **Form State**: Controlled components with local state

**Routing Strategy**:
- **Route Groups**: `(auth)` for public pages, `(protected)` for authenticated pages
- **Middleware**: Next.js middleware redirects unauthenticated users from `/todos` to `/signin`
- **Client-Side Navigation**: `next/navigation` router for SPA-like transitions

**API Communication**:
- Centralized API client (`lib/api.ts`) wraps `fetch` with:
  - Base URL configuration
  - Automatic JSON serialization/deserialization
  - Error handling and transformation
  - Session cookie automatic inclusion

### Database Architecture (Neon PostgreSQL)

**Schema Design**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    is_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

**Migration Strategy**:
- Alembic for schema versioning and migrations
- All migrations include `upgrade()` and `downgrade()` functions
- Migrations tested in local environment before production deployment

**Connection Management**:
- SQLModel async session management
- Connection pooling via SQLAlchemy engine
- Environment variable for Neon connection string

### Integration Points

**Frontend ↔ Backend Communication**:
- Protocol: HTTPS with JSON payloads
- Authentication: HTTP-only cookies (set by backend, sent automatically by browser)
- CORS: Backend configured to accept requests from frontend origin
- Error Handling: Frontend displays user-friendly messages from backend error responses

**Backend ↔ Database Communication**:
- Protocol: PostgreSQL wire protocol over TLS
- ORM: SQLModel async queries
- Connection String: `postgresql+asyncpg://user:pass@host/db` from environment variable
- Migration Execution: Alembic CLI commands during deployment

**Better Auth Integration**:
- Backend: Better Auth session validation via API
- Frontend: Better Auth React hooks for signup/signin forms and session management
- Session Storage: HTTP-only cookies with SameSite=Lax, Secure flags

---

## Error Handling Strategy

### Backend Error Handling

**Validation Errors** (400 Bad Request):
- Triggered by: Invalid input, missing required fields, format violations
- Response: `{"detail": [{"field": "title", "message": "Title required"}]}`

**Authentication Errors** (401 Unauthorized):
- Triggered by: Invalid credentials, missing session, expired session
- Response: `{"detail": "Invalid email or password"}`

**Authorization Errors** (403 Forbidden):
- Triggered by: Attempting to access another user's todo
- Response: `{"detail": "You do not have permission to access this resource"}`

**Not Found Errors** (404 Not Found):
- Triggered by: Todo ID does not exist, user does not exist
- Response: `{"detail": "Todo not found"}`

**Server Errors** (500 Internal Server Error):
- Triggered by: Database connection failure, unexpected exceptions
- Response: `{"detail": "An unexpected error occurred. Please try again later."}`
- Logging: Full stack trace logged with request context

### Frontend Error Handling

**API Errors**:
- Display inline error messages near form fields (validation errors)
- Display toast notifications for operation failures (delete failed, server error)
- Retry mechanism for transient network errors

**Client-Side Validation**:
- Validate inputs before API calls (email format, password length, title length)
- Show real-time validation feedback as user types
- Prevent form submission if validation fails

**Loading States**:
- Show loading spinners during API calls
- Disable submit buttons to prevent duplicate requests
- Show skeleton loaders for todo list while fetching

---

## Testing Strategy

### Backend Testing

**Contract Tests** (`tests/contract/`):
- Verify API endpoint schemas match OpenAPI contracts
- Test request/response JSON structure
- Validate HTTP status codes for all scenarios

**Integration Tests** (`tests/integration/`):
- Test complete user flows (signup → signin → create todo → delete todo)
- Test data isolation (user A cannot access user B's todos)
- Test database transactions (rollback on error)
- Use test database instance (separate from development)

**Unit Tests** (`tests/unit/`):
- Test service layer business logic in isolation
- Test password hashing and verification
- Test input validation utilities
- Mock database operations

### Frontend Testing

**Component Tests** (Jest + React Testing Library):
- Test form submission and validation
- Test user interactions (button clicks, input changes)
- Test conditional rendering (empty state, loading state, error state)
- Mock API calls

**E2E Tests** (Playwright):
- Test complete user journeys across pages
- Test authentication flows (signup, signin, session persistence)
- Test todo CRUD operations in browser
- Test responsive design on different viewport sizes

---

## Deployment Considerations

### Environment Variables

**Backend**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `SECRET_KEY`: Session encryption key (randomly generated, 32+ characters)
- `BETTER_AUTH_API_KEY`: Better Auth API credentials
- `ALLOWED_ORIGINS`: CORS allowed origins (frontend URL)
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, ERROR)

**Frontend**:
- `NEXT_PUBLIC_API_URL`: Backend API base URL
- `NEXT_PUBLIC_BETTER_AUTH_CLIENT_ID`: Better Auth client ID

### Migration Workflow

1. Review migration script (`alembic/versions/*.py`)
2. Test migration in staging environment
3. Backup production database
4. Run `alembic upgrade head` in production
5. Verify schema changes with `alembic current`
6. Monitor application logs for errors
7. If errors: `alembic downgrade -1` to rollback

### Health Checks

**Backend Health Endpoint** (`GET /health`):
- Returns 200 OK if service is running
- Response: `{"status": "healthy", "timestamp": "2026-01-07T12:00:00Z"}`

**Backend Readiness Endpoint** (`GET /ready`):
- Returns 200 OK if database is accessible
- Returns 503 Service Unavailable if database is down
- Response: `{"status": "ready", "database": "connected"}`

---

## Security Considerations

### Password Security
- Bcrypt hashing with 12+ rounds (configurable via environment variable)
- Passwords never logged or returned in API responses
- Minimum 8 characters enforced at frontend and backend

### Session Security
- HTTP-only cookies prevent XSS access to session tokens
- SameSite=Lax prevents CSRF attacks
- Secure flag ensures cookies only sent over HTTPS
- 7-day session expiration with sliding window renewal

### Input Validation
- Pydantic models validate all API inputs
- SQLModel prevents SQL injection via parameterized queries
- Frontend validates inputs before submission
- Maximum lengths enforced (email 255 chars, title 200 chars)

### CORS Configuration
- Backend explicitly lists allowed frontend origins
- Credentials (cookies) allowed only from trusted origins
- Pre-flight requests handled correctly for PATCH/DELETE

### Rate Limiting
- Basic rate limiting via hosting infrastructure (not implemented in Phase II per constitution)
- Future enhancement: custom rate limiting middleware

---

## Performance Optimization

### Backend Performance
- Database connection pooling (10 connections default)
- Async request handling via FastAPI + asyncio
- Database indexes on frequently queried fields (user.email, todo.user_id, todo.created_at)
- Pagination for todo lists (if >100 todos per user in future)

### Frontend Performance
- Next.js automatic code splitting per route
- Image optimization via Next.js `<Image>` component (if images added)
- CSS optimization via Tailwind purge
- API response caching for GET requests (if needed)

### Database Performance
- Neon auto-scaling handles load spikes
- Indexes on foreign keys and frequently filtered columns
- Query optimization via SQLModel eager loading (avoid N+1 queries)

---

## Open Questions & Risks

### Risks Identified in Specification

1. **Better Auth Integration Complexity**:
   - Mitigation: Allocate dedicated research time in Phase 0 to evaluate Better Auth documentation and examples
   - Fallback: If Better Auth proves overly complex, consider simpler session-based auth with custom implementation (requires constitution amendment approval)

2. **CORS Configuration**:
   - Mitigation: Document CORS settings in quickstart.md, test thoroughly in local development
   - Verification: Include CORS tests in integration test suite

3. **Data Isolation Enforcement**:
   - Mitigation: Implement authorization middleware at API layer, add comprehensive integration tests for cross-user access attempts
   - Verification: Dedicated test suite in `tests/integration/test_data_isolation.py`

### Additional Technical Risks

4. **Neon PostgreSQL Cold Starts**:
   - Risk: Serverless database may have latency spikes on cold starts
   - Mitigation: Monitor `/ready` endpoint latency, consider connection pooling optimizations

5. **Session Cookie Compatibility**:
   - Risk: Browser compatibility issues with SameSite=Lax or Secure flags
   - Mitigation: Test across target browsers (Chrome, Firefox, Safari, Edge), document browser requirements

6. **Frontend Build Size**:
   - Risk: Next.js bundle size may exceed performance budgets
   - Mitigation: Monitor bundle size with Next.js built-in analyzer, use dynamic imports if needed

---

## Next Steps

1. ✅ **Phase 0 Complete**: Generate `research.md` with technology evaluations
2. ✅ **Phase 1 Complete**: Generate `data-model.md`, `contracts/*.yaml`, `quickstart.md`
3. 🔄 **Phase 2**: Run `/sp.tasks` to generate task breakdown from this plan
4. 🔄 **Implementation**: Execute tasks in dependency order (setup → tests → implementation)
5. 🔄 **Validation**: Run all tests, verify constitution compliance, deploy to staging

**Plan Status**: ✅ **Complete** - Ready for task generation (`/sp.tasks`)
