# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**English Transfer Assistant** is an AI-powered English text correction and analysis tool designed for English learners. The project helps users improve their English writing through intelligent error detection, correction, and structured explanations.

### Current Status
- **Phase**: Implementation (Phase 3) - Framework Complete (10%)
- **Framework**: ✅ Complete (backend + frontend + Docker + dev tools)
- **Implementation**: ⏳ In Progress (skeleton code created, business logic pending)
- **Documentation**: Complete (see `/docs` directory)

### Latest Commit
- `c3201f1` - feat: 搭建项目代码框架 (126 files, 18,241 lines added)
- Branch: `feature/202601_gemini`

### Tech Stack

**Backend:**
- Python 3.11+ with Poetry
- FastAPI 0.115.0
- SQLAlchemy 2.0.36 (async-ready)
- Alembic 1.14.0 (migrations)
- PostgreSQL 16 (data storage)
- Redis 7 (rate limiting + caching)
- LanguageTool 2.8.3 (grammar checking)
- Zhipu AI GLM-4-Flash (LLM optimization)
- JWT authentication (python-jose)
- Pydantic v2 (validation)

**Frontend:**
- Vue 3.5.13 with Composition API
- TypeScript 5.7.3 (strict mode)
- Vite 6.0.7 (build tool)
- Pinia 2.2.8 (state management)
- Vue Router 4.5.0
- Tailwind CSS 3.4.17
- Axios 1.7.9 (HTTP client)

**Infrastructure:**
- Docker + Docker Compose
- Poetry (Python deps)
- NPM (frontend deps)

## Core Architecture

### 4-Stage Pipeline (Backend)

The text correction system uses a **4-stage pipeline** orchestrated by `AnalysisPipeline`:

1. **Preprocessing** (`pipeline/preprocessor.py`)
   - `Preprocessor.preprocess()` - Sentence splitting, speaker detection, Chinese char detection
   - Output: `PreprocessedText` dataclass with `Message` list

2. **Rule-Based Correction** (`pipeline/rule_engine.py`)
   - `RuleEngine.check()` - LanguageTool integration
   - Error classification (grammar, tense, word_choice, etc.)
   - Output: `list[GrammarError]` with severity levels

3. **LLM Optimization** (`pipeline/llm_engine.py`)
   - `LLMEngine.optimize()` - Zhipu AI GLM-4-Flash
   - Intent detection (text type, tone, speakers)
   - Chinese-English mixing correction
   - Output: `LLMResult` dataclass
   - Raises `LLMError` on failure

4. **Merging** (`pipeline/merger.py`)
   - `Merger.merge()` - Combine rule-based and LLM results
   - Handle overlapping corrections with conflict resolution
   - Output: `MergedResult` dataclass

**Main Controller**: `AnalysisPipeline.analyze(text, mode)` -> `PipelineResult`
- Each stage is timed independently
- Supports caching (Redis)
- Graceful degradation if LLM fails

### Database Schema

**SQLAlchemy Models** (in `backend/models/`):

**Base Classes:**
- `Base` - Declarative base for all models
- `TimestampMixin` - created_at, updated_at fields
- `SoftDeleteMixin` - deleted_at, is_deleted fields

**Core Models:**
- `User` - id, email, username, password_hash, tier (free/paid), credits
- `UserSettings` - dark_mode, correction_mode, notification preferences
- `APICredit` - user_id, credits_remaining, reset_date
- `Analysis` - id, user_id, original_text, corrected_text, mode, status
- `ErrorDetail` - id, analysis_id, error_type, severity, position, message
- `Tag` - id, name, color
- `AnalysisTag` - analysis_id, tag_id (many-to-many)
- `AnalysisCache` - id, text_hash, result_json, expires_at

**Session Management** (`models/session.py`):
- `engine` - SQLAlchemy async engine
- `SessionLocal` - Session factory
- `get_db()` - Dependency injection for FastAPI

### Frontend Architecture

**Data Flow Pattern**: Component → Composable → Store → API

**Pinia Stores** (`src/stores/`):
- `authStore` - User, tokens, isAuthenticated, login/register/logout
- `analysisStore` - currentResult, isAnalyzing, mode, viewMode, progress
- `historyStore` - items, pagination, filters
- `uiStore` - toast notifications, dark mode, panel states, sidebar

**API Layer** (`src/api/`):
- `index.ts` - Axios instance with interceptors (auto token refresh on 401)
- `auth.ts`, `analysis.ts`, `history.ts`, etc. - Typed API methods

**Component Structure**:
- `views/` - Page-level components (Home, Auth, History, Statistics, Settings)
- `components/layout/` - Navbar, MainLayout, LayoutControls
- `components/panels/` - InputPanel, ComparePanel, AnalysisPanel
- `components/errors/` - ErrorCard, ErrorHighlight
- `components/common/` - Toast, LoadingSpinner, ErrorDisplay

**Router** (`src/router/`):
- Route guards for protected routes
- Auto-redirect based on auth state

## Development Commands

### Quick Start (Recommended)

```bash
# One-click startup (Docker + backend + frontend)
./scripts/dev.sh

# Verify environment
./scripts/verify.sh

# Run tests
./scripts/test.sh
```

### Backend

```bash
cd backend

# Install dependencies (first time only)
poetry install

# Run development server
poetry run uvicorn main:app --reload --port 8000

# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_auth.py -v

# Format code
poetry run black .
poetry run ruff check .

# Type check
poetry run mypy .

# Database migration (when implemented)
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"
```

### Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check

# Lint
npm run lint
```

### Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart postgres
```

## Key Design Decisions

### Batch Processing, Not Real-Time
- v1.0 focuses on batch text correction (not real-time)
- Better learning value with detailed error analysis
- No <1s response time requirement
- Cost optimization through caching and batch processing
- 4 of 5 core use cases are batch scenarios

### Two Correction Modes
- **Accuracy First**: Fix grammatical errors only, preserve style
- **Naturalness First**: Rewrite for naturalness (may change structure)

### Rate Limiting (Tiers)
- Anonymous: 5 requests/hour
- Free users: 50 requests/day
- Paid users: 500 requests/day

### LLM Fallback Strategy
- Zhipu AI fails → degrade to LanguageTool-only
- LanguageTool fails → try LLM-only
- Always return partial results, never complete failures

### Known Issues
- **tiktoken package disabled** - Python 3.14 incompatibility (requires 3.11-3.13)
- Tests currently fail - skeleton code missing imports (will be fixed during implementation)

## API Structure

**Base URL**: `/api/v1`

**Routers** (`backend/api/v1/`):
- `auth.py` - register, login, refresh, me
- `analysis.py` - POST /analyze (main endpoint)
- `history.py` - GET /history, GET /history/{id}, DELETE /history/{id}
- `statistics.py` - GET /overview, GET /tokens
- `export.py` - POST /export (JSON/Markdown/PDF)
- `settings.py` - GET /settings, PUT /settings

**Response Format**:
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Codes**: INVALID_INPUT, UNAUTHORIZED, TOKEN_EXPIRED, RATE_LIMIT_EXCEEDED, ANALYSIS_FAILED, LLM_ERROR, GRAMMAR_TOOL_ERROR

## Important File Locations

**Documentation:**
- `/docs/FRAMEWORK_SETUP.md` - Complete framework setup documentation (just created)
- `/docs/04-technical-design/architecture.md` - System architecture, database schema, pipeline design
- `/docs/05-tasks/implementation-checklist.md` - 100+ implementation tasks
- `/docs/02-ui-design/ui-final.html` - Interactive UI prototype

**Configuration:**
- `backend/pyproject.toml` - Poetry dependencies (75 packages installed)
- `backend/.env.example` - Backend environment template
- `frontend/package.json` - NPM dependencies (277 packages installed)
- `docker-compose.yml` - PostgreSQL 16 + Redis 7

**Development:**
- `scripts/dev.sh` - One-click startup
- `scripts/verify.sh` - Environment validation
- `scripts/test.sh` - Test runner

## External Services

### Zhipu AI (智谱 AI)
- **SDK**: `zhipuai` Python package
- **Model**: GLM-4-Flash (10x cheaper than standard)
- **Usage**: Intent detection, naturalness optimization, Chinese-English correction
- **Optimization**: Batch processing (10 sentences/call), 24-hour caching
- **Fallback**: Graceful degradation to LanguageTool-only

### LanguageTool
- **Package**: `language-tool-python`
- **Usage**: Grammar, spelling, tense, style checking
- **Mapping**: Categories → UI error types (grammar, tense, word_choice, etc.)

## Next Implementation Steps

### Immediate (Current Focus)
1. **Fix skeleton imports** - Add missing imports to backend models (DateTime, etc.)
2. **Database setup** - Configure Alembic, create initial migrations
3. **Authentication** - Implement JWT generation/validation, password hashing
4. **Pipeline implementation** - Connect LanguageTool and Zhipu AI

### Short-term
5. **API endpoints** - Implement analyze, history, auth endpoints
6. **Frontend integration** - Connect stores to backend API
7. **Error handling** - Complete error handling in all services
8. **Testing** - Write comprehensive unit and integration tests

See `/docs/05-tasks/implementation-checklist.md` for full task list.

## Project Status Summary

**Framework Complete**: ✅
- 126 files created (18,241 lines)
- Backend: 50+ Python files with complete module structure
- Frontend: 40+ Vue/TS files with all components
- Docker: PostgreSQL 16 + Redis 7 configured
- Scripts: dev.sh, verify.sh, test.sh all working

**Next Milestone**: Database & Authentication
- Configure Alembic migrations
- Implement JWT authentication
- Fix skeleton code imports
- Get tests passing

**Branch**: `feature/202601_gemini` (commit: `c3201f1`)
**Ready to Push**: Yes - all framework code committed

---

## Quick Reference

| What | Command |
|------|---------|
| Start all | `./scripts/dev.sh` |
| Verify setup | `./scripts/verify.sh` |
| Run tests | `./scripts/test.sh` |
| Backend server | `cd backend && poetry run uvicorn main:app --reload` |
| Frontend server | `cd frontend && npm run dev` |
| Docker services | `docker-compose up -d` |
| Stop services | `docker-compose down` |

**Service URLs**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
