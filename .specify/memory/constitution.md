<!--
Sync Impact Report:
Version: 1.0.0 → 2.0.0 (MAJOR)
Rationale: Complete constitution creation with Phase-based Technology Matrix principle
Modified Principles: All principles created from template
Added Sections:
  - Technology Matrix (Phase I, II, III)
  - Test-First Development
  - Integration Testing
  - Observability
  - Code Quality
  - Deployment & Versioning
  - Security Requirements
  - Development Workflow
Templates Status:
  ✅ plan-template.md - Constitution Check section aligns
  ✅ spec-template.md - Requirements sections align
  ✅ tasks-template.md - Phase-based task structure aligns
Follow-up TODOs: None
-->

# Todo App Constitution

## Core Principles

### I. Technology Matrix (Phase-Based)

**Phase I: In-Memory Console Application ONLY**
- MUST remain purely in-memory (no databases, no persistence)
- MUST be console/CLI-based (no web interface, no GUI)
- MUST NOT include authentication or user management
- MUST NOT use external services or APIs
- Purpose: Validate core business logic in isolation

**Phase II: Full-Stack Web Application** (CURRENT PHASE)
- **Backend**: Python REST API
- **Database**: Neon Serverless PostgreSQL
- **ORM/Data Layer**: SQLModel or equivalent
- **Frontend**: Next.js (React, TypeScript)
- **Authentication**: Better Auth (signup/signin)
- **Architecture**: Full-stack web application
- Authentication IS ALLOWED starting Phase II
- Web frontend IS ALLOWED starting Phase II
- Neon PostgreSQL IS ALLOWED starting Phase II
- MUST NOT use AI frameworks, agents, or orchestration tools
- MUST NOT introduce cloud infrastructure beyond basic hosting

**Phase III and Beyond: Advanced Infrastructure**
- Advanced cloud infrastructure (multi-region, CDN, load balancing)
- AI and agent frameworks
- Orchestration and automation tools
- Microservices and event-driven architecture

**Enforcement**:
- All PRs MUST verify phase compliance in constitution check
- Technology choices outside current phase MUST be rejected
- Phase transitions require explicit constitution amendment
- Each phase MUST preserve prior phase functionality as regression tests

### II. Test-First Development (NON-NEGOTIABLE)

**TDD Cycle MUST be followed**:
1. Write acceptance tests that capture user requirements
2. Get user approval on test scenarios
3. Verify tests FAIL (Red)
4. Implement minimum code to pass tests (Green)
5. Refactor while keeping tests green (Refactor)

**Test Coverage Requirements**:
- All user stories MUST have acceptance tests
- All API endpoints MUST have contract tests
- All business logic MUST have unit tests
- Tests MUST be written BEFORE implementation code

**Test Organization**:
- `tests/contract/` - API contract and schema validation
- `tests/integration/` - End-to-end user journey tests
- `tests/unit/` - Component and business logic tests

### III. Integration Testing

**Integration tests REQUIRED for**:
- New API endpoints and contracts
- Database schema changes
- Authentication and authorization flows
- Frontend-backend integration points
- Third-party service integrations

**Integration Test Standards**:
- MUST test real HTTP requests (not mocks)
- MUST use test database instances (isolated from production)
- MUST validate error handling and edge cases
- MUST be idempotent and runnable in parallel

### IV. Observability

**Logging Standards**:
- Structured logging REQUIRED (JSON format preferred)
- ALL API requests MUST log: timestamp, endpoint, method, status, duration
- ALL database operations MUST log: query type, duration, rows affected
- ALL errors MUST log: stack trace, context, user ID (if applicable)
- Sensitive data (passwords, tokens) MUST be redacted

**Monitoring Requirements**:
- Health check endpoints REQUIRED (`/health`, `/ready`)
- Performance metrics REQUIRED (request duration, DB query time)
- Error rate tracking REQUIRED (by endpoint, by error type)
- Text I/O ensures debuggability (stdin/stdout/stderr protocol)

### V. Code Quality

**Code Standards**:
- TypeScript REQUIRED for frontend (strict mode enabled)
- Python type hints REQUIRED for backend (mypy validation)
- ESLint + Prettier REQUIRED for frontend
- Black + Ruff REQUIRED for backend
- No unused imports, variables, or functions
- Maximum function length: 50 lines (extract helpers if exceeded)

**Documentation Requirements**:
- All public APIs MUST have JSDoc/docstring comments
- All complex business logic MUST have inline comments explaining "why"
- README MUST include setup instructions and architecture overview
- API contracts MUST be documented in `specs/<feature>/contracts/`

**Simplicity Principle (YAGNI)**:
- Start with simplest solution that works
- No premature optimization
- No speculative features
- Refactor when complexity is proven necessary, not anticipated

### VI. Deployment & Versioning

**Version Format**: MAJOR.MINOR.PATCH
- MAJOR: Breaking API changes, database schema incompatibility
- MINOR: New features, backward-compatible changes
- PATCH: Bug fixes, security patches

**Deployment Requirements**:
- All deployments MUST pass CI/CD pipeline
- Production deployments REQUIRE tagged release
- Database migrations MUST be reversible
- Feature flags REQUIRED for high-risk changes

**Rollback Strategy**:
- All deployments MUST be rollback-safe within 5 minutes
- Database migrations MUST include down scripts
- Feature flags enable instant disable without redeployment

## Security Requirements

**Authentication & Authorization (Phase II+)**:
- Better Auth integration REQUIRED for user management
- Password requirements: minimum 8 characters, complexity rules
- Session management: secure HTTP-only cookies, CSRF protection
- JWT tokens: short-lived (15 min), refresh token rotation

**Data Protection**:
- All user passwords MUST be hashed (bcrypt, minimum 12 rounds)
- All sensitive data in transit MUST use HTTPS/TLS
- Database connection strings MUST use environment variables
- API keys and secrets MUST NEVER be committed to repository

**Input Validation**:
- All user input MUST be validated and sanitized
- SQL injection prevention via parameterized queries (SQLModel ORM)
- XSS prevention via output encoding
- CSRF protection on all state-changing endpoints

**Security Auditing**:
- All authentication events MUST be logged
- Failed login attempts MUST be rate-limited
- Security-relevant changes MUST be reviewed by 2+ developers

## Development Workflow

**Branch Strategy**:
- Feature branches: `###-feature-name` (e.g., `001-user-authentication`)
- All work happens in feature branches
- PRs required for merging to main/master

**Commit Standards**:
- Conventional commits format: `type(scope): description`
- Types: feat, fix, docs, refactor, test, chore
- Commits MUST reference task IDs from tasks.md
- Atomic commits: one logical change per commit

**Code Review Requirements**:
- All PRs REQUIRE at least one approval
- Reviewers MUST verify:
  - Constitution compliance (phase, testing, security)
  - Test coverage (tests exist and pass)
  - Code quality (linting, formatting, complexity)
  - Documentation (comments, README updates)

**PR Description Template**:
- Summary: what changed and why
- Test plan: how to verify the change
- Constitution check: phase compliance verification
- Related tasks: links to spec.md and tasks.md

## Governance

**Amendment Process**:
1. Proposed amendment MUST be documented in PR description
2. Amendment MUST include version bump rationale (MAJOR/MINOR/PATCH)
3. Amendment MUST be approved by project maintainer
4. Amendment MUST update LAST_AMENDED_DATE
5. Dependent templates MUST be updated (plan, spec, tasks)

**Compliance Verification**:
- All PRs MUST include constitution check in PR description
- Constitution violations MUST be justified in plan.md Complexity Tracking table
- Unjustified violations result in PR rejection

**Migration Planning**:
- Phase transitions MUST include migration plan
- Breaking changes MUST include deprecation warnings
- Database schema changes MUST include migration scripts

**Version Management**:
- MAJOR bump: backward-incompatible changes, principle removal/redefinition
- MINOR bump: new principles, new sections, expanded guidance
- PATCH bump: clarifications, typos, wording improvements

**Runtime Development Guidance**:
- Use `CLAUDE.md` for agent-specific development instructions
- Constitution supersedes all other practices
- When in conflict, constitution takes precedence

**Version**: 2.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
