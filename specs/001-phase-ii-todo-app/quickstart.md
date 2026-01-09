# Quickstart: Phase II Todo App Local Development

**Feature**: Phase II Todo App
**Date**: 2026-01-07
**Purpose**: Step-by-step guide to set up local development environment and run the application

## Overview

This guide walks through setting up the Phase II Todo App on your local machine, including:
- Prerequisites installation
- Environment configuration
- Database setup with Neon PostgreSQL
- Backend API setup (FastAPI)
- Frontend setup (Next.js)
- Running tests
- Verifying the complete stack

**Estimated Setup Time**: 15-20 minutes

---

## Prerequisites

### Required Software

Install the following before proceeding:

1. **Python 3.11+**
   - Check version: `python --version` or `python3 --version`
   - Download: https://www.python.org/downloads/
   - Verify: `python3 --version` should output `Python 3.11.x` or higher

2. **Node.js 18+**
   - Check version: `node --version`
   - Download: https://nodejs.org/ (LTS version recommended)
   - Verify: `node --version` should output `v18.x.x` or higher

3. **npm or yarn** (comes with Node.js)
   - Check version: `npm --version`
   - Alternative: `yarn --version` (if you prefer yarn)

4. **Git**
   - Check version: `git --version`
   - Download: https://git-scm.com/downloads

5. **Neon Account** (for PostgreSQL database)
   - Sign up: https://neon.tech/
   - Free tier available
   - Create a new project and database

### Optional Tools

- **PostgreSQL Client** (for database inspection)
  - psql command-line tool: comes with PostgreSQL installation
  - GUI tools: pgAdmin, DBeaver, TablePlus
- **API Testing Tool**
  - Postman: https://www.postman.com/downloads/
  - HTTPie: https://httpie.io/
  - Or use FastAPI's built-in Swagger UI (http://localhost:8000/docs)

---

## Step 1: Clone Repository

```bash
# Clone the repository (replace with actual repo URL)
git clone https://github.com/your-org/todo-app.git
cd todo-app

# Checkout the feature branch (if not already on it)
git checkout 001-phase-ii-todo-app
```

**Verify**:
```bash
# You should see backend/ and frontend/ directories
ls -la
```

---

## Step 2: Environment Configuration

### Backend Environment Variables

1. Create `.env` file in the `backend/` directory:

```bash
cd backend
cp .env.example .env  # If .env.example exists
# Or create .env manually
```

2. Edit `backend/.env` with the following variables:

```env
# Database Configuration (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/database
# Example: postgresql+asyncpg://myuser:mypass@ep-cool-forest-123456.us-east-2.aws.neon.tech/mydb

# Application Security
SECRET_KEY=your-secret-key-minimum-32-characters-random-string
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# Better Auth Configuration
BETTER_AUTH_API_KEY=your-better-auth-api-key
# Obtain from Better Auth dashboard: https://www.better-auth.com/dashboard

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000
# Production: ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR

# Environment
ENVIRONMENT=development
# Options: development, staging, production
```

**Get Neon Database URL**:
1. Log in to https://console.neon.tech/
2. Select your project
3. Go to "Connection Details"
4. Copy the connection string (choose "asyncpg" driver)
5. Paste into `DATABASE_URL` in `.env`

**Generate SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend Environment Variables

1. Create `.env.local` file in the `frontend/` directory:

```bash
cd ../frontend
cp .env.local.example .env.local  # If example exists
# Or create .env.local manually
```

2. Edit `frontend/.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Client Configuration
NEXT_PUBLIC_BETTER_AUTH_CLIENT_ID=your-better-auth-client-id
# Obtain from Better Auth dashboard

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

**Security Note**: Never commit `.env` or `.env.local` files to Git. These files contain sensitive credentials.

---

## Step 3: Backend Setup

### Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify Installation**:
```bash
# Check installed packages
pip list | grep fastapi
pip list | grep sqlmodel
pip list | grep alembic
```

### Database Migrations

```bash
# Initialize Alembic (if not already initialized)
alembic init alembic  # Skip if alembic/ directory exists

# Run migrations to create tables
alembic upgrade head

# Verify current migration version
alembic current
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

**Verify Database Schema** (optional):
```bash
# Connect to Neon database with psql
psql "postgresql://user:password@host/database"

# List tables
\dt

# Expected tables:
# - users
# - todos
# - alembic_version

# Describe users table
\d users

# Exit psql
\q
```

---

## Step 4: Frontend Setup

### Install Node.js Dependencies

```bash
cd frontend

# Install dependencies with npm
npm install

# Or with yarn
yarn install
```

**Verify Installation**:
```bash
# Check installed packages
npm list next
npm list react
npm list typescript
```

---

## Step 5: Run the Application

### Start Backend API

```bash
cd backend

# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Run FastAPI development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
- Open browser: http://localhost:8000/health
- Expected response: `{"status": "healthy", "timestamp": "2026-01-07T12:00:00Z"}`
- API Documentation: http://localhost:8000/docs (FastAPI Swagger UI)

### Start Frontend (in new terminal)

```bash
cd frontend

# Run Next.js development server
npm run dev

# Or with yarn
yarn dev
```

**Expected Output**:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

**Verify Frontend**:
- Open browser: http://localhost:3000
- You should see the landing page or redirect to signin page

---

## Step 6: Verify Complete Stack

### Manual Testing

1. **Sign Up**:
   - Navigate to: http://localhost:3000/signup
   - Enter email: `test@example.com`
   - Enter password: `TestPass123`
   - Click "Sign Up"
   - Expected: Redirect to todos page

2. **Create Todo**:
   - On todos page, click "Add Todo"
   - Enter title: "Test Todo"
   - Click "Save"
   - Expected: Todo appears in list

3. **Toggle Complete**:
   - Click checkbox next to "Test Todo"
   - Expected: Todo marked as complete (visual indication: strikethrough or different color)

4. **Update Todo**:
   - Click "Edit" on "Test Todo"
   - Change title to "Updated Test Todo"
   - Click "Save"
   - Expected: Todo title updated in list

5. **Delete Todo**:
   - Click "Delete" on "Updated Test Todo"
   - Confirm deletion
   - Expected: Todo removed from list

6. **Sign Out** (if implemented):
   - Click "Sign Out"
   - Expected: Redirect to signin page

### API Testing with Swagger UI

1. Open: http://localhost:8000/docs
2. Test `/auth/signup` endpoint:
   - Click "POST /auth/signup"
   - Click "Try it out"
   - Enter request body:
     ```json
     {
       "email": "swagger@example.com",
       "password": "SwaggerPass123"
     }
     ```
   - Click "Execute"
   - Expected response: 201 Created with user data

3. Test `/todos` endpoints:
   - Note: Swagger UI may not automatically include session cookie (manual testing preferred)
   - Alternatively, use Postman or HTTPie for authenticated requests

### API Testing with HTTPie (Alternative)

```bash
# Install HTTPie (if not installed)
pip install httpie

# Sign up
http POST http://localhost:8000/auth/signup email="httpie@example.com" password="HttpiePass123"

# Note the Set-Cookie header in response

# Sign in (to get fresh session)
http --session=./session.json POST http://localhost:8000/auth/signin email="httpie@example.com" password="HttpiePass123"

# Create todo (session automatically included)
http --session=./session.json POST http://localhost:8000/todos title="HTTPie Todo"

# Get todos
http --session=./session.json GET http://localhost:8000/todos

# Update todo (replace {todo_id} with actual ID from previous response)
http --session=./session.json PATCH http://localhost:8000/todos/{todo_id} is_complete:=true

# Delete todo
http --session=./session.json DELETE http://localhost:8000/todos/{todo_id}
```

---

## Step 7: Run Tests

### Backend Tests

```bash
cd backend

# Ensure virtual environment is activated
source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/         # Unit tests only
pytest tests/contract/     # Contract tests only
pytest tests/integration/  # Integration tests only

# Run with verbose output
pytest -v
```

**Expected Output**:
```
============================= test session starts ==============================
collected 45 items

tests/unit/test_auth_service.py ........                                 [ 17%]
tests/unit/test_todo_service.py ........                                 [ 35%]
tests/contract/test_auth_contract.py ......                              [ 48%]
tests/contract/test_todos_contract.py ..........                         [ 70%]
tests/integration/test_auth_flow.py .....                                [ 81%]
tests/integration/test_todo_crud.py .......                              [ 96%]
tests/integration/test_data_isolation.py ..                              [100%]

============================== 45 passed in 12.34s ==============================
```

### Frontend Tests

```bash
cd frontend

# Run Jest unit tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- tests/components/SignupForm.test.tsx

# Run E2E tests (Playwright)
npx playwright test

# Run E2E tests with UI
npx playwright test --ui
```

**Expected Output (Jest)**:
```
PASS  tests/components/SignupForm.test.tsx
PASS  tests/components/SigninForm.test.tsx
PASS  tests/components/TodoList.test.tsx

Test Suites: 3 passed, 3 total
Tests:       18 passed, 18 total
Snapshots:   0 total
Time:        5.234 s
```

**Expected Output (Playwright)**:
```
Running 8 tests using 4 workers
  8 passed (15s)

To open last HTML report run:
  npx playwright show-report
```

---

## Step 8: Development Workflow

### Hot Reload (Auto-Restart on Code Changes)

Both backend and frontend support hot reload during development:

- **Backend**: uvicorn `--reload` flag automatically restarts on Python file changes
- **Frontend**: Next.js automatically recompiles on TypeScript/React file changes

Simply edit files and save; the servers will auto-reload.

### Database Schema Changes

When modifying models:

1. Edit SQLModel classes in `backend/src/models/`
2. Generate migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of change"
   ```
3. Review generated migration in `alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```

### Viewing Logs

**Backend Logs**:
- Logs output to console (stdout/stderr)
- Structured JSON logs if LOG_LEVEL=DEBUG
- Example log entry:
  ```json
  {"timestamp": 1704636000, "level": "INFO", "message": "POST /todos 201 45ms", "user_id": "..."}
  ```

**Frontend Logs**:
- Browser console (F12 Developer Tools → Console tab)
- Next.js server logs in terminal

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```
- **Solution**: Verify `DATABASE_URL` in `backend/.env` is correct
- **Verify**: Try connecting with psql: `psql "postgresql://user:password@host/database"`

**2. Port Already in Use**:
```
ERROR: [Errno 48] Address already in use
```
- **Solution**: Kill process using port 8000 or 3000
  ```bash
  # macOS/Linux
  lsof -ti:8000 | xargs kill -9  # Backend
  lsof -ti:3000 | xargs kill -9  # Frontend

  # Windows
  netstat -ano | findstr :8000  # Find PID
  taskkill /PID <PID> /F         # Kill process
  ```

**3. Module Not Found (Python)**:
```
ModuleNotFoundError: No module named 'fastapi'
```
- **Solution**: Ensure virtual environment is activated and dependencies installed
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**4. Session Cookie Not Working (CORS)**:
```
Access to fetch at 'http://localhost:8000/todos' from origin 'http://localhost:3000' has been blocked by CORS policy
```
- **Solution**: Verify `ALLOWED_ORIGINS=http://localhost:3000` in `backend/.env`
- **Check**: Backend logs should show CORS middleware configured correctly

**5. Migration Already Applied**:
```
alembic.util.exc.CommandError: Target database is not up to date.
```
- **Solution**: Check current version: `alembic current`
- **Reset** (dangerous, only in local dev): `alembic downgrade base` then `alembic upgrade head`

**6. Better Auth Configuration Error**:
```
Better Auth API key invalid
```
- **Solution**: Verify `BETTER_AUTH_API_KEY` in `backend/.env` and `NEXT_PUBLIC_BETTER_AUTH_CLIENT_ID` in `frontend/.env.local`
- **Check**: Ensure credentials match Better Auth dashboard

---

## Verification Checklist

Use this checklist to confirm your environment is correctly set up:

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Git installed (`git --version`)
- [ ] Neon PostgreSQL account created and database provisioned
- [ ] Repository cloned and on correct branch (`001-phase-ii-todo-app`)
- [ ] Backend `.env` file created with DATABASE_URL, SECRET_KEY, BETTER_AUTH_API_KEY
- [ ] Frontend `.env.local` file created with NEXT_PUBLIC_API_URL
- [ ] Backend dependencies installed (`pip list | grep fastapi`)
- [ ] Frontend dependencies installed (`npm list next`)
- [ ] Database migrations applied (`alembic current` shows latest version)
- [ ] Backend running on http://localhost:8000 (health check passes)
- [ ] Frontend running on http://localhost:3000 (page loads)
- [ ] Can sign up new user via frontend
- [ ] Can create, update, delete, toggle todos via frontend
- [ ] Backend tests pass (`pytest`)
- [ ] Frontend tests pass (`npm test`)

**If all checkboxes are checked, your local development environment is ready!**

---

## Next Steps

1. **Familiarize with Codebase**:
   - Explore `backend/src/models/` for database entities
   - Review `backend/src/routers/` for API endpoints
   - Check `frontend/src/app/` for page routing
   - Read `frontend/src/components/` for UI components

2. **Review API Documentation**:
   - Open http://localhost:8000/docs for interactive API docs
   - Review `specs/001-phase-ii-todo-app/contracts/` for OpenAPI specs

3. **Run Task Workflow**:
   - Execute `/sp.tasks` to generate implementation task breakdown
   - Follow TDD workflow: write tests → verify they fail → implement → verify they pass

4. **Contribute**:
   - Create feature branches from `001-phase-ii-todo-app`
   - Follow conventional commit format: `feat(todos): add filtering by completion status`
   - Run tests before committing: `pytest && npm test`
   - Ensure constitution compliance (Phase II technology stack)

---

## Helpful Commands Reference

### Backend

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest
pytest --cov=src --cov-report=html

# Database migrations
alembic upgrade head          # Apply migrations
alembic current               # Show current version
alembic downgrade -1          # Rollback one version
alembic revision --autogenerate -m "message"  # Generate migration

# Format code
black src/
ruff check src/
mypy src/
```

### Frontend

```bash
# Run development server
npm run dev

# Run tests
npm test                      # Jest unit tests
npm test -- --coverage        # With coverage
npx playwright test           # E2E tests
npx playwright test --ui      # E2E tests with UI

# Build for production
npm run build
npm run start                 # Run production build

# Lint and format
npm run lint
npm run format
```

### Database

```bash
# Connect to Neon database
psql "postgresql://user:password@host/database"

# Common psql commands
\dt                # List tables
\d users           # Describe users table
\d todos           # Describe todos table
SELECT * FROM users LIMIT 5;  # Query users
\q                 # Quit psql
```

---

## Support

If you encounter issues not covered in this guide:

1. Check existing issues: https://github.com/your-org/todo-app/issues
2. Review specification: `specs/001-phase-ii-todo-app/spec.md`
3. Review architecture plan: `specs/001-phase-ii-todo-app/plan.md`
4. Consult constitution: `.specify/memory/constitution.md`
5. Open new issue with detailed error messages and environment info

**Happy Coding!** 🚀
