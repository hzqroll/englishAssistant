# AGENTS.md - Development Guide for Coding Agents

This file provides guidance for agentic coding assistants working on the English Transfer Assistant codebase.

## Quick Commands

### Backend (Python/FastAPI)

```bash
cd backend

# Install dependencies
poetry install

# Run development server
poetry run uvicorn main:app --reload --port 8000

# Run all tests
poetry run pytest

# Run single test file
poetry run pytest tests/test_auth.py -v

# Run specific test function
poetry run pytest tests/test_auth.py::test_login -v

# Run with coverage
poetry run pytest --cov=backend --cov-report=term-missing

# Format code
poetry run black .

# Lint code (auto-fix available)
poetry run ruff check .
poetry run ruff check --fix .

# Type check
poetry run mypy .

# Database migration
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"
```

### Frontend (Vue 3/TypeScript)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check  # or: npx vue-tsc --noEmit

# Lint (if ESLint configured)
npm run lint
```

### Full Stack

```bash
# Start all services (Docker + backend + frontend)
./scripts/dev.sh

# Run all tests
./scripts/test.sh

# Run tests with linting
./scripts/test.sh --with-lint

# Backend only
./scripts/test.sh --backend-only

# Frontend only
./scripts/test.sh --frontend-only
```

## Code Style Guidelines

### Python (Backend)

**Imports:**
- Use isort-style ordering (enforced by ruff): stdlib → third-party → local
- Use `from module import name` for specific imports
- Use `import module` for modules with many attributes
- Group imports with blank lines between groups

**Formatting:**
- Line length: 100 characters (Black config)
- Use Black for auto-formatting
- Use Ruff for linting (enforces pycodestyle, pyflakes, isort, flake8-bugbear)
- Target Python version: 3.11+

**Type Hints:**
- ALL functions must have type hints (enforced by mypy `disallow_untyped_defs`)
- Use `typing` module for generic types: `List[str]`, `Dict[str, Any]`, `Optional[int]`
- Use `Optional[T]` instead of `T | None` for consistency
- Use `datetime` from `datetime` module for timestamps
- Import types under `TYPE_CHECKING` guard for circular dependencies:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from models import User
  ```

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `AnalysisService`, `UserSettings`)
- Functions/variables: `snake_case` (e.g., `get_user`, `user_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- Private methods: `_leading_underscore`
- Database models: Singular nouns (e.g., `User`, not `Users`)
- Pydantic schemas: PascalCase with descriptive names (e.g., `AnalyzeRequest`, `ErrorDetailResponse`)

**Error Handling:**
- Raise custom exceptions with descriptive messages (define in appropriate module)
- Use `HTTPException` from FastAPI for API errors with status codes:
  ```python
  raise HTTPException(status_code=404, detail="User not found")
  ```
- Use specific exception handling (`except SpecificError`, not bare `except`)
- Always re-raise with context if needed: `raise HTTPException(...) from e`
- Use `try/except/finally` pattern with explicit `db.rollback()` on errors
- Log errors using Python logging module (don't use print)

**Database (SQLAlchemy):**
- Use async patterns where appropriate (`async def`, `await`)
- Use `Session` from `models.session` via dependency injection
- Always close sessions (use context managers or fixtures in tests)
- Use `db.flush()` to get IDs before commit
- Use `db.commit()` after multiple operations
- Use soft deletes via `SoftDeleteMixin`, never hard delete
- Define relationships with proper `back_populates` and `cascade` options

**Testing (pytest):**
- Use fixtures defined in `tests/conftest.py`
- Mark tests: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Use descriptive test names: `test_login_with_valid_credentials_succeeds`
- Follow AAA pattern (Arrange, Act, Assert)
- Use test doubles/mocks for external services
- Test database uses in-memory SQLite (see `conftest.py`)

**Documentation:**
- Module-level docstrings at top of files
- Class docstrings describe purpose and key attributes
- Function docstrings with Args/Returns/Raises sections (Google style)
- Use `TODO:` comments for unimplemented features

**FastAPI Patterns:**
- Use Pydantic models for request/response validation
- Use `Depends()` for dependency injection
- Use `response_model=` for response validation
- Group routes in APIRouter files in `api/v1/`
- Use HTTPBearer for JWT authentication

### TypeScript/Vue (Frontend)

**Imports:**
- Use absolute imports with `@/` alias (configured in vite.config.ts)
- Order: external → internal → type imports
- Use `import type { T }` for type-only imports

**Formatting:**
- Follow Vue 3 Composition API style
- Use `<script setup lang="ts">` in single-file components
- Use Tailwind CSS classes for styling
- Keep components under 300 lines (split if larger)

**Type Definitions:**
- Define types in `src/stores/types.ts`
- Use `interface` for object shapes
- Use `type` for unions/literals (e.g., `CorrectionMode = 'accuracy' | 'naturalness'`)
- Use `Ref<T>` and `Computed<T>` for reactive refs and computed properties

**Naming Conventions:**
- Components: `PascalCase` (e.g., `InputPanel`, `ErrorCard`)
- Variables/functions: `camelCase` (e.g., `isLoading`, `fetchUser`)
- Stores: `useXxxStore` (e.g., `useAuthStore`, `useAnalysisStore`)
- Constants: `UPPER_SNAKE_CASE`
- Props: `camelCase` but use kebab-case in templates
- Events: `kebab-case` with `on` prefix (e.g., `@on-submit`)

**State Management (Pinia):**
- Use Composition API style (`defineStore('name', () => { ... })`)
- Store state in `ref()`
- Computed values with `computed()`
- Actions are plain functions
- Persist tokens in localStorage (access/refresh tokens)

**API Layer:**
- Centralized in `src/api/` with typed functions
- Use axios instance from `src/api/index.ts`
- Handle token refresh automatically in interceptors
- Return typed responses

**Testing (Vitest):**
- Use `@vue/test-utils` for component testing
- Mock API calls and store actions
- Test user interactions and state changes

## Architecture Patterns

**4-Stage Pipeline:** Preprocessing → Rule-Based (LanguageTool) → LLM (Zhipu AI) → Merging
**Data Flow:** Component → Composable → Store → API
**Error Handling:** Graceful degradation (LLM fails → LanguageTool-only)
**Caching:** Redis for LLM results (24-hour TTL)

## Important Notes

- Python version: 3.11+ (NOT 3.14 - tiktoken package incompatible)
- Always run `poetry run mypy` before committing
- Frontend: http://localhost:5173, Backend: http://localhost:8000
- Use `docker-compose up -d` for PostgreSQL + Redis
- Never commit secrets (.env files, credentials)
- Follow existing patterns when adding new features
