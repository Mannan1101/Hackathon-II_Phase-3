# Phase 0: Research & Technology Decisions

**Feature**: Phase II Todo App
**Date**: 2026-01-07
**Purpose**: Document technology evaluations, best practices research, and architectural decisions for Phase II implementation

## Overview

This document captures the research and decision-making process for technology choices in Phase II. All decisions must comply with the project constitution's Phase II technology matrix while selecting the most appropriate tools and patterns for the requirements.

---

## 1. Backend Framework Selection

### Requirement
Python REST API framework for todo CRUD operations, authentication integration, and JSON API responses.

### Options Considered

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **FastAPI** | - Native async support<br>- Automatic OpenAPI docs<br>- Pydantic validation built-in<br>- Excellent SQLModel integration<br>- Fast performance | - Newer ecosystem (fewer legacy examples)<br>- Async learning curve | ✅ **SELECTED** |
| Flask + Flask-RESTful | - Mature ecosystem<br>- Simple to learn<br>- Many examples | - No native async<br>- Manual validation setup<br>- No auto-docs | ❌ Rejected |
| Django REST Framework | - Batteries included<br>- Admin panel<br>- ORM included | - Heavy for simple API<br>- Opinionated structure<br>- Slower than FastAPI | ❌ Rejected |

### Decision: FastAPI

**Rationale**:
- **Async Support**: Native async/await enables high concurrency for 100+ concurrent users (success criteria SC-007)
- **Automatic Validation**: Pydantic models provide request/response validation out-of-the-box (FR-API-004)
- **OpenAPI Integration**: Auto-generated API documentation aids contract testing and frontend integration
- **SQLModel Compatibility**: FastAPI and SQLModel both use Pydantic, reducing boilerplate and ensuring type safety
- **Performance**: ASGI-based async architecture meets <200ms p95 latency requirement

**Best Practices**:
- Use dependency injection for database sessions and current user extraction
- Implement router-based modular structure (`routers/auth.py`, `routers/todos.py`)
- Use HTTPException for consistent error responses with status codes
- Enable CORS middleware with explicit allowed origins

**References**:
- FastAPI official docs: https://fastapi.tiangolo.com
- FastAPI + SQLModel tutorial: https://sqlmodel.tiangolo.com/tutorial/fastapi/

---

## 2. ORM Selection

### Requirement
Python ORM for Neon PostgreSQL integration with type safety, migrations, and async support.

### Options Considered

| ORM | Pros | Cons | Verdict |
|-----|------|------|---------|
| **SQLModel** | - Combines SQLAlchemy + Pydantic<br>- Type-safe queries<br>- Async support<br>- Minimal boilerplate | - Newer library (fewer examples)<br>- Less mature than SQLAlchemy | ✅ **SELECTED** |
| SQLAlchemy Core | - Mature and stable<br>- Async support (2.0+)<br>- Flexible query builder | - More boilerplate<br>- Manual Pydantic integration | ❌ Rejected |
| Tortoise ORM | - Django-like syntax<br>- Full async<br>- Good docs | - Less ecosystem support<br>- No Pydantic integration | ❌ Rejected |

### Decision: SQLModel

**Rationale**:
- **Type Safety**: SQLModel models are both SQLAlchemy tables AND Pydantic models, eliminating duplication
- **Validation**: Built-in Pydantic validation ensures data integrity at ORM level (FR-API-004)
- **Constitution Compliance**: Explicitly listed as "SQLModel or equivalent" in Phase II requirements
- **Developer Experience**: Single model definition serves database schema, API validation, and type hints
- **Async Support**: Native async session management for FastAPI compatibility

**Best Practices**:
- Define separate SQLModel classes for database (with `table=True`) and API schemas (without `table=True`)
- Use `relationship()` for foreign key navigation (User → Todos)
- Use `Field()` for validation constraints (max_length=200 for todo titles)
- Enable cascading deletes on User → Todos relationship (when user deleted, todos auto-deleted)

**Migration Strategy**:
- Use Alembic for schema migrations (SQLModel lacks built-in migrations)
- Generate migrations with `alembic revision --autogenerate`
- Always include `upgrade()` and `downgrade()` functions for rollback safety

**References**:
- SQLModel official docs: https://sqlmodel.tiangolo.com
- Alembic + SQLModel guide: https://alembic.sqlalchemy.org/en/latest/

---

## 3. Frontend Framework Configuration

### Requirement
Next.js (React + TypeScript) application with authentication, routing, and API integration.

### Options Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Next.js App Router** (v13+) | - Modern React patterns<br>- Built-in layouts<br>- Server components<br>- Route groups | - Newer API (less mature docs) | ✅ **SELECTED** |
| Next.js Pages Router | - Mature and stable<br>- More examples<br>- Simpler mental model | - Legacy approach<br>- Less flexible layouts | ❌ Rejected |

### Decision: Next.js App Router

**Rationale**:
- **Route Groups**: `(auth)` and `(protected)` groups enable clean separation of public vs. authenticated pages
- **Layouts**: Shared layouts reduce code duplication for auth pages and protected pages
- **Middleware**: Built-in middleware for authentication checks and redirects (FR-UI-010)
- **Modern Patterns**: Aligns with Next.js 14+ best practices and future direction
- **Server Components**: Potential for future optimization (not required in Phase II but enables future enhancements)

**Best Practices**:
- Use `middleware.ts` for authentication checks and redirects
- Organize routes with groups: `app/(auth)/signin`, `app/(protected)/todos`
- Use Server Actions for form submissions (if needed, or stick with client-side API calls)
- Enable TypeScript strict mode in `tsconfig.json`

**References**:
- Next.js App Router docs: https://nextjs.org/docs/app
- Route groups guide: https://nextjs.org/docs/app/building-your-application/routing/route-groups

---

## 4. Authentication Strategy

### Requirement
Better Auth integration for signup/signin with session persistence across page refreshes.

### Options Considered

| Strategy | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Session-Based (HTTP-only cookies)** | - XSS protection<br>- CSRF protection built-in<br>- Automatic browser handling | - Requires CORS configuration<br>- Server-side session storage | ✅ **SELECTED** |
| JWT Tokens (localStorage) | - Stateless<br>- Simple implementation | - Vulnerable to XSS<br>- No auto-refresh | ❌ Rejected |
| JWT Tokens (httpOnly cookies) | - Stateless<br>- XSS protection | - Requires refresh token rotation<br>- More complex | ❌ Rejected |

### Decision: Session-Based with HTTP-Only Cookies

**Rationale**:
- **Security**: HTTP-only cookies prevent JavaScript access, mitigating XSS attacks (Security Requirements)
- **CSRF Protection**: SameSite=Lax cookie attribute prevents cross-site request forgery
- **Session Persistence**: Cookies persisted by browser enable 7-day session duration (FR-AUTH-005)
- **Constitution Compliance**: Aligns with "Session management: secure HTTP-only cookies, CSRF protection"
- **Simplicity**: Browser automatically includes cookies in requests, no manual header management

**Better Auth Integration**:
- Better Auth provides session validation APIs and React hooks
- Backend: Validate session on every protected endpoint via middleware
- Frontend: Use Better Auth `useSession()` hook for authentication state
- Cookie Configuration: `SameSite=Lax`, `Secure=true`, `HttpOnly=true`, `Max-Age=604800` (7 days)

**Implementation Details**:
- Backend sets session cookie on successful signin: `Set-Cookie: session_id=xxx; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800`
- Auth middleware extracts `session_id` from cookie, validates with Better Auth API, extracts `user_id`
- Frontend Better Auth hooks automatically include cookies in API requests

**References**:
- Better Auth docs: https://www.better-auth.com/docs
- OWASP session management: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

---

## 5. CSS Framework Selection

### Requirement
Responsive UI (320px-1920px) with mobile and desktop support.

### Options Considered

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **Tailwind CSS** | - Utility-first rapid development<br>- Built-in responsive classes<br>- Small production bundle<br>- No naming conflicts | - Verbose HTML<br>- Learning curve for team | ✅ **SELECTED** |
| CSS Modules | - Scoped styles<br>- Traditional CSS | - More boilerplate<br>- Manual responsive design | ❌ Rejected |
| Styled Components | - CSS-in-JS<br>- Dynamic styling | - Runtime overhead<br>- Larger bundle size | ❌ Rejected |

### Decision: Tailwind CSS

**Rationale**:
- **Responsive Design**: Built-in breakpoints (`sm:`, `md:`, `lg:`, `xl:`) simplify mobile-first design (FR-UI-009)
- **Performance**: Purge unused styles in production, resulting in minimal CSS bundle
- **Developer Experience**: Utility classes enable rapid prototyping and iteration
- **Consistency**: Predefined spacing, colors, and typography ensure design consistency
- **Next.js Integration**: First-class Tailwind support in Next.js with zero configuration

**Best Practices**:
- Use Tailwind's default breakpoints: `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`
- Mobile-first approach: base styles for mobile, add `md:` and `lg:` for larger screens
- Use `@apply` directive sparingly (prefer utility classes for clarity)
- Configure custom colors in `tailwind.config.js` for brand consistency

**References**:
- Tailwind CSS docs: https://tailwindcss.com/docs
- Tailwind + Next.js guide: https://tailwindcss.com/docs/guides/nextjs

---

## 6. Database Schema Design

### Requirement
User and Todo entities with one-to-many relationship, enforcing data isolation.

### Schema Decisions

**Users Table**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Design Rationale**:
- **UUID Primary Key**: Prevents enumeration attacks, globally unique identifiers
- **Email Unique Constraint**: Enforces FR-AUTH-003 (no duplicate accounts)
- **Indexed Email**: Speeds up login queries (frequent lookups by email)
- **Hashed Password**: Never store plaintext passwords (Security Requirements)
- **Timestamps**: Audit trail for account creation and updates

**Todos Table**:
```sql
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    is_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Design Rationale**:
- **Foreign Key Constraint**: Enforces referential integrity (FR-DATA-001)
- **ON DELETE CASCADE**: When user deleted, todos automatically deleted (data cleanup)
- **Indexed user_id**: Speeds up queries filtering by user (every todo query)
- **Title Max Length**: 200 characters enforced at database and application levels (FR-TODO-002)
- **Boolean is_complete**: Simple flag for completion status (FR-TODO-006)
- **Indexed created_at**: Enables fast sorting by creation date descending (FR-TODO-007)

**Indexes**:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

**Index Rationale**:
- `idx_users_email`: Login queries filter by email (frequent operation)
- `idx_todos_user_id`: Every todo query filters by user_id (data isolation enforcement)
- `idx_todos_created_at`: Sorting todos by creation date (FR-TODO-007)

**References**:
- PostgreSQL UUID best practices: https://www.postgresql.org/docs/current/datatype-uuid.html
- Database indexing strategies: https://use-the-index-luke.com

---

## 7. Testing Framework Selection

### Requirement
Test-first development with contract tests, integration tests, and unit tests.

### Backend Testing

**Framework**: pytest + pytest-asyncio

**Rationale**:
- **Async Support**: pytest-asyncio enables testing FastAPI async endpoints
- **Fixtures**: pytest fixtures provide clean test setup/teardown for database sessions
- **Parametrization**: `@pytest.mark.parametrize` enables data-driven tests
- **Coverage**: pytest-cov measures code coverage (target: 80%+ for business logic)

**Test Organization**:
- `tests/contract/`: API contract tests (validate request/response schemas against OpenAPI spec)
- `tests/integration/`: End-to-end tests (database + API + authentication flows)
- `tests/unit/`: Isolated business logic tests (services, utilities)

**Best Practices**:
- Use separate test database (avoid polluting development data)
- Use database transactions with rollback for test isolation
- Mock external services (Better Auth API) in unit tests
- Use real HTTP requests in integration tests (via `httpx.AsyncClient`)

### Frontend Testing

**Frameworks**: Jest + React Testing Library (unit/component) + Playwright (E2E)

**Rationale**:
- **Jest**: Standard React testing framework, built-in Next.js support
- **React Testing Library**: User-centric testing (test behavior, not implementation)
- **Playwright**: Cross-browser E2E testing (Chrome, Firefox, Safari)

**Test Organization**:
- `tests/components/`: Component unit tests (forms, todo items, UI components)
- `tests/e2e/`: End-to-end user journey tests (signup → signin → create todo)

**Best Practices**:
- Mock API calls in component tests (use MSW or jest.mock)
- Test user interactions (button clicks, form submissions)
- Use Playwright for full browser automation (real auth flows, session persistence)
- Test responsive design at different viewport sizes

**References**:
- pytest docs: https://docs.pytest.org
- React Testing Library: https://testing-library.com/react
- Playwright docs: https://playwright.dev

---

## 8. Error Handling Patterns

### Backend Error Handling

**HTTPException Strategy**:
- Use FastAPI's `HTTPException` for all expected errors
- Provide descriptive `detail` messages for client consumption
- Use standard HTTP status codes (400, 401, 403, 404, 500)

**Global Exception Handler**:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )
```

**Validation Error Format**:
```json
{
  "detail": [
    {"field": "title", "message": "Title is required"},
    {"field": "title", "message": "Title must be 200 characters or fewer"}
  ]
}
```

### Frontend Error Handling

**API Client Error Handling**:
- Parse backend error responses and extract `detail` field
- Display inline validation errors near form fields
- Show toast notifications for operation failures
- Retry transient network errors (503, timeout)

**User-Friendly Messages**:
- 400: "Please check your input and try again."
- 401: "Invalid email or password."
- 403: "You don't have permission to do that."
- 404: "Todo not found."
- 500: "Something went wrong. Please try again later."

---

## 9. Logging and Observability

### Backend Logging

**Structured Logging** (JSON format):
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": record.created,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "user_id": getattr(record, "user_id", None),
        })
```

**Logging Middleware**:
- Log every API request: `{"method": "POST", "path": "/todos", "status": 201, "duration_ms": 45}`
- Log database queries: `{"query": "INSERT INTO todos", "duration_ms": 12, "rows_affected": 1}`
- Log errors with stack traces: `{"level": "ERROR", "message": "...", "stack_trace": "..."}`

**Log Redaction**:
- Never log passwords, session tokens, or API keys
- Redact sensitive fields in structured logs

### Health Checks

**`/health` Endpoint**:
- Returns 200 OK if service is running
- No dependencies checked (fast response)

**`/ready` Endpoint**:
- Returns 200 OK if database is accessible
- Returns 503 Service Unavailable if database down
- Used by load balancers for readiness checks

---

## 10. Development Environment

### Local Development Requirements

**Prerequisites**:
- Python 3.11+ (backend runtime)
- Node.js 18+ (frontend runtime, Next.js requirement)
- PostgreSQL client tools (optional, for database inspection)
- Neon account (for cloud database)

**Environment Setup**:
1. Clone repository
2. Copy `.env.example` to `.env` and configure:
   - `DATABASE_URL`: Neon PostgreSQL connection string
   - `SECRET_KEY`: Random 32+ character string for session encryption
   - `BETTER_AUTH_API_KEY`: Better Auth credentials
3. Backend: `cd backend && pip install -r requirements.txt`
4. Frontend: `cd frontend && npm install`
5. Run migrations: `cd backend && alembic upgrade head`
6. Start backend: `cd backend && uvicorn src.main:app --reload`
7. Start frontend: `cd frontend && npm run dev`

**Verification**:
- Backend health: `curl http://localhost:8000/health`
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs` (FastAPI auto-generated)

---

## 11. CORS Configuration

### Requirement
Frontend (localhost:3000) must communicate with backend (localhost:8000) during development.

### CORS Strategy

**Backend Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],  # GET, POST, PATCH, DELETE
    allow_headers=["*"],  # Accept, Content-Type, etc.
)
```

**Production Configuration**:
- Replace `http://localhost:3000` with production frontend domain
- Use environment variable for allowed origins: `ALLOWED_ORIGINS=https://app.example.com`

**Security Considerations**:
- Never use `allow_origins=["*"]` with `allow_credentials=True` (security risk)
- Explicitly list trusted origins
- Test CORS configuration in local development before production deployment

---

## 12. Password Security

### Requirement
Bcrypt hashing with minimum 12 rounds (Constitution Security Requirements).

### Implementation

**Backend Password Utility**:
```python
import bcrypt

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

**Best Practices**:
- Use bcrypt (not SHA256 or MD5)
- Minimum 12 rounds (configurable via environment variable for future cost increases)
- Constant-time comparison prevents timing attacks
- Never store or log plain passwords

---

## Summary of Key Decisions

| Decision Area | Selected Technology | Rationale |
|---------------|---------------------|-----------|
| Backend Framework | FastAPI | Async support, auto-validation, OpenAPI docs, SQLModel compatibility |
| ORM | SQLModel | Type safety, Pydantic integration, constitution compliance |
| Frontend Framework | Next.js 14 App Router | Route groups, modern patterns, built-in middleware |
| Authentication | Session-based (HTTP-only cookies) | XSS protection, CSRF protection, security compliance |
| CSS Framework | Tailwind CSS | Responsive utilities, small bundle, rapid development |
| Backend Testing | pytest + pytest-asyncio | Async support, fixtures, parametrization |
| Frontend Testing | Jest + React Testing Library + Playwright | Component tests, E2E tests, cross-browser |
| Database Migrations | Alembic | Industry standard for SQLAlchemy/SQLModel migrations |
| Logging | JSON structured logging | Observability, machine-readable, constitution compliance |
| Password Hashing | Bcrypt (12 rounds) | Constitution requirement, industry standard |

**All decisions comply with Phase II constitution requirements and technology matrix.**

---

## Next Steps

1. ✅ Research complete
2. → Generate data-model.md with SQLModel entity definitions
3. → Generate API contracts (OpenAPI specs) in `contracts/`
4. → Generate quickstart.md for local development setup
5. → Generate tasks.md with implementation task breakdown
