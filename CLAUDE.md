# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**English Transfer Assistant** is an AI-powered English text correction and analysis tool designed for English learners. The project helps users improve their English writing through intelligent error detection, correction, and structured explanations.

### Current Status
- **Phase**: Feature Implementation - Split Analysis (LanguageTool + LLM Separation)
- **Backend**: ✅ Operational (core pipeline working), 🔄 Adding split analysis endpoints
- **Frontend**: ✅ UI Components Complete (RuleEnginePanel, LLMPanel, AIOptimizeButton)
- **Pipeline**: ✅ Operational (4-stage pipeline), 🔄 Refactoring for sequential analysis
- **LLM Multi-Provider**: ✅ Complete (Zhipu AI, OpenAI, Anthropic, Gemini support)
- **Documentation**: ✅ Complete design and implementation plan
- **Branch**: `feature/mvp_v1`

### Latest Work
- ✅ **Function split design completed** - LanguageTool and LLM separation architecture
- ✅ **UI components built** - RuleEnginePanel, LLMPanel, AIOptimizeButton (3 files)
- ✅ **Frontend types updated** - TypeScript interfaces for split analysis
- ✅ **API client updated** - New methods: analyzeRulesOnly, optimizeWithLLM
- ✅ **Pinia store updated** - New state: ruleResult, llmResult, isOptimizing
- ✅ **Implementation plan created** - 12 tasks, 35+ steps with complete code
- 🔄 **Backend implementation pending** - Ready to start development
- Branch: `feature/mvp_v1`

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
- In-memory caching (V1 MVP)
- Multi-LLM provider support (Zhipu AI, OpenAI, Anthropic, Google Gemini)

## Core Architecture

### 4-Stage Pipeline (Current)

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
- Supports in-memory caching (CacheService) for V1 MVP
- Graceful degradation if LLM fails

### New Split Analysis Architecture (Implementation In Progress)

**Sequential Analysis Flow** - User-controlled cost optimization:

**Phase 1: Rule-Based Analysis** (Fast, Free)
- **Method**: `AnalysisPipeline.analyze_rules_only(text, mode, user_id, session)`
- **Endpoint**: `POST /api/v1/analyze/rules-only`
- **Processing**: Preprocessing + LanguageTool only
- **Response Time**: 2-4 seconds
- **Returns**: `RuleBasedResult` with:
  - `analysis_id` - For optional LLM optimization later
  - `errors[]` - Full LanguageTool error details
  - `corrected_text` - LT-corrected text
  - `statistics` - Error counts by category
  - `estimated_llm_tokens` - Token estimate for Phase 2
- **Database Status**: `ea_analyses.status = 'rule_only'`

**Phase 2: LLM Optimization** (Optional, Costly)
- **Method**: `AnalysisPipeline.optimize_with_llm(analysis_id, user_id, session)`
- **Endpoint**: `POST /api/v1/analyze/optimize-llm`
- **Trigger**: User clicks "✨ AI 深度优化" button
- **Processing**: LLM optimization + learning insights generation
- **Response Time**: 3-5 seconds
- **Returns**: `LLMResult` with:
  - `optimized_text` - AI-optimized text
  - `suggestions[]` - Sentence-level improvements
  - `chinese_corrections[]` - Chinese-English mixing fixes
  - `learning_analysis` - Personalized learning recommendations
  - `token_usage` - Actual token consumption
- **Database Status**: `ea_analyses.status = 'completed'`

**Learning Analysis System** (New Feature)
- **Error Pattern Extraction**: Identifies user's common error types
- **Historical Trend Analysis**: Tracks improvement over 30 days
- **Personalized Recommendations**: Learning resources and exercises
- **Progress Tracking**: Compares current vs past performance

### Database Schema

**Table Naming Convention**: All tables use `ea_` prefix (English Assistant)

**SQLAlchemy Models** (in `backend/models/`):

**Base Classes:**
- `Base` - Declarative base for all models
- `TimestampMixin` - created_at, updated_at fields
- `SoftDeleteMixin` - deleted_at, is_deleted fields

**Core Models:**
- `User` (ea_users) - id, email, username, password_hash, tier (free/paid), credits
- `UserSettings` - dark_mode, correction_mode, notification preferences
- `APICredit` - user_id, credits_remaining, reset_date
- `Analysis` (ea_analyses) - id, user_id, original_text, corrected_text, mode, status, llm_tokens_used
  - **NEW fields**: `status` ('rule_only', 'completed', 'failed'), `llm_tokens_used`, `llm_cost_usd`
- `ErrorDetail` (ea_error_details) - **NEW TABLE**
  - analysis_id, rule_id, category, severity, position_start, position_end
  - original_text, correction, message, context
  - Stores complete LanguageTool error information
- `LearningRecommendation` (ea_learning_recommendations) - **NEW TABLE**
  - user_id, analysis_id, pattern_name, frequency, severity
  - recommendation (TEXT), resources (JSONB), priority
  - estimated_study_time, created_at
- `UserErrorTrend` (ea_user_error_trends) - **NEW TABLE**
  - user_id, pattern_name, error_count, trend_direction
  - last_calculated, UNIQUE(user_id, pattern_name)
- `Tag` - id, name, color
- `AnalysisTag` - analysis_id, tag_id (many-to-many)
- `AnalysisCache` - id, text_hash, result_json, expires_at
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

## Frontend Architecture (Updated)

### Data Flow Pattern
Component → Composable → Store → API

### Pinia Stores (`src/stores/`)
- `authStore` - User, tokens, isAuthenticated, login/register/logout
- `analysisStore` - **UPDATED** with split analysis support:
  - **New State**: `ruleResult`, `llmResult`, `isOptimizing`, `llmError`
  - **New Computed**: `hasRuleResult`, `hasLLMResult`, `canOptimize`
  - **New Actions**: `analyzeWithRules()`, `optimizeWithLLM()`
  - **Legacy**: `currentResult`, `isAnalyzing`, `analyzeText()` (kept for backward compatibility)
- `historyStore` - items, pagination, filters
- `uiStore` - toast notifications, dark mode, panel states, sidebar

### API Layer (`src/api/`)
- `index.ts` - Axios instance with interceptors (auto token refresh on 401)
- `analysis.ts` - **UPDATED** with new endpoints:
  - `analyzeRulesOnly({ text, mode, language })` - Phase 1: LanguageTool only
  - `optimizeWithLLM({ analysis_id })` - Phase 2: LLM optimization
  - `analyze({ text, mode })` - Legacy: Full analysis (kept for compatibility)
- `auth.ts`, `history.ts`, etc. - Typed API methods

### Component Structure (New Split Layout)
```
src/components/
├── layout/
│   ├── MainLayout.vue - **UPDATED**: 3-panel layout (30%, 35%, 35%)
│   └── LayoutControls.vue
├── panels/
│   ├── InputPanel.vue - Text input (30% width)
│   ├── RuleEnginePanel.vue - **NEW**: LanguageTool results (35% width)
│   ├── LLMPanel.vue - **NEW**: LLM optimization + learning (35% width)
│   ├── AIOptimizeButton.vue - **NEW**: Floating trigger button
│   ├── ComparePanel.vue - Legacy (kept for reference)
│   └── AnalysisPanel.vue - Legacy (kept for reference)
├── common/ - Toast, LoadingSpinner, ErrorDisplay
└── errors/ - ErrorCard, ErrorHighlight
```

### New UI Components Details

**1. RuleEnginePanel.vue**
- Displays LanguageTool analysis results
- Error categorization (grammar, spelling, tense, word choice, punctuation, casing)
- Expandable error cards with Rule ID and severity
- States: waiting → loading → results
- Custom scrollbar with blue accent

**2. LLMPanel.vue**
- Displays LLM optimization results
- Sentence-level improvements (original → LT → AI)
- Chinese-English mixing corrections
- **Learning Analysis System**:
  - 📊 Error pattern distribution (visual progress bars)
  - 🎯 Personalized learning recommendations (with priority)
  - 📈 Historical trend analysis (week-over-week)
  - 💬 Personalized learning tips
- States: waiting → ready → loading → completed

**3. AIOptimizeButton.vue**
- Floating button between RuleEnginePanel and LLMPanel
- 4 states with animations:
  - **Disabled** (gray): "等待规则检测完成"
  - **Enabled** (blue gradient): "✨ AI 深度优化 (~15 tokens)" with pulse glow
  - **Loading** (purple): Dual-ring spinner animation
  - **Completed** (green): "✓ 优化完成 (12 tokens)" with particle burst

### User Flow
```
1. User types text → InputPanel
2. Click "分析" → analyzeWithRules() called
3. RuleEnginePanel shows loading → displays LT results (2-4s)
4. AIOptimizeButton becomes enabled (blue pulsing)
5. User evaluates: Is LT correction enough?
   ├─ Yes → Done (saved tokens!)
   └─ No → Click "✨ AI 深度优化"
       → LLMPanel shows loading → displays AI results + learning (3-5s)
       → AIOptimizeButton turns green (shows actual token cost)
```

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
# Start PostgreSQL (Redis removed for V1 MVP)
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
- **Anonymous users**: 10 requests/day (in-memory tracking, no database records)
- **Free users**: 50 requests/day (database tracking with full audit trail)
- **Pro users**: 500 requests/day
- **Enterprise users**: 5000 requests/day

**Implementation Notes:**
- Anonymous users identified by "anon:IP_ADDRESS" format
- Anonymous user IDs converted to deterministic UUIDs via MD5 hash for consistency
- In-memory tracking prevents foreign key constraint issues

### LLM Fallback Strategy
- Zhipu AI fails → degrade to LanguageTool-only
- LanguageTool fails → try LLM-only
- Always return partial results, never complete failures

### V1 MVP Simplifications
- **In-memory caching** - Redis removed for V1 (see `CacheService`)
- **Focus on batch processing** - Real-time mode planned for V2.0
- **Single-instance deployment** - No distributed architecture needed

### Known Issues & Important Notes

**Working Features:**
- ✅ Analyze endpoint processes text successfully
- ✅ Anonymous users can use the service without authentication
- ✅ Rate limiting enforced (10 requests/day for anonymous users)
- ✅ Error detection and correction working via LanguageTool
- ✅ Results saved to database with caching
- ✅ LLM multi-provider system operational

**Known Limitations:**
- **tiktoken package disabled** - Python 3.14 incompatibility (requires 3.11-3.13)
- **LLM optimization not tested** - Zhipu AI integration needs API key configuration
- **Frontend-backend integration incomplete** - Vue components need to connect to live API

## API Structure (Updated)

**Base URL**: `/api/v1`

**Routers** (`backend/api/v1/`):
- `auth.py` - register, login, refresh, me
- `analysis.py` - **UPDATED** with split analysis endpoints:
  - `POST /analyze/rules-only` - **NEW**: LanguageTool-only analysis
  - `POST /analyze/optimize-llm` - **NEW**: LLM optimization on existing analysis
  - `POST /analyze` - Legacy: Full analysis (both LT + LLM)
- `history.py` - GET /history, GET /history/{id}, DELETE /history/{id}
- `statistics.py` - GET /overview, GET /tokens
- `export.py` - POST /export (JSON/Markdown/PDF)
- `settings.py` - GET /settings, PUT /settings
- `llm_config.py` - GET /llm/providers, GET /llm/config, PUT /llm/config, POST /llm/validate

**Response Format**:
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Codes**: INVALID_INPUT, UNAUTHORIZED, TOKEN_EXPIRED, RATE_LIMIT_EXCEEDED, ANALYSIS_FAILED, LLM_ERROR, GRAMMAR_TOOL_ERROR

## Documentation

**Design Documents:**
- `/docs/03-product-features/20260205-function-feature.md` - Original feature split concept
- `/docs/plans/2026-02-05-function-split-design.md` - Complete feature design (15 sections)
- `/docs/plans/2026-02-05-split-analysis-implementation.md` - **Implementation Plan** (12 tasks, 35+ steps)
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

### LLM Providers (Multi-Provider Architecture)

The system supports multiple LLM providers with per-user configuration:

**1. Zhipu AI (智谱 AI)** - Default Provider
- **SDK**: `zhipuai` Python package
- **Models**: GLM-4-Flash, GLM-4-FlashX, GLM-4-Air, GLM-4-AirX, GLM-4-Plus
- **Usage**: Intent detection, naturalness optimization, Chinese-English correction
- **Optimization**: Batch processing (10 sentences/call), 24-hour caching (in-memory for V1)
- **API Key**: Encrypted with Fernet, per-user override supported

**2. OpenAI**
- **SDK**: `openai` Python package (v2.16.0)
- **Models**: GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
- **Usage**: Alternative LLM provider
- **Configuration**: System-level or per-user API keys

**3. Anthropic**
- **SDK**: `anthropic` Python package (v0.77.0)
- **Models**: Claude-3-Opus, Claude-3-Sonnet
- **Usage**: Alternative LLM provider
- **Configuration**: System-level or per-user API keys

**Provider Management:**
- Per-user provider/model selection stored in `UserSettings`
- API keys encrypted using Fernet symmetric encryption
- Fallback to system default keys if user doesn't provide custom keys
- Provider validation endpoint: `POST /api/v1/llm/validate`

### LanguageTool (Rule-Based Grammar Checker)
- **Package**: `language-tool-python`
- **Usage**: Grammar, spelling, tense, style checking (always runs, regardless of LLM)
- **Mapping**: Categories → UI error types (grammar, tense, word_choice, etc.)
- **Fallback**: If LLM fails, LanguageTool results are still returned

## Code Style and Development Standards

This project has strict code style standards. See `AGENTS.md` for comprehensive guidelines.

**Backend Standards:**
- Type hints required on ALL functions (enforced by mypy)
- Line length: 100 characters (Black config)
- Import order: stdlib → third-party → local (isort-style via ruff)
- Use `Optional[T]` instead of `T | None` for consistency
- Use Google-style docstrings with Args/Returns/Raises
- Database models use singular nouns (e.g., `User`, not `Users`)
- Always use soft deletes via `SoftDeleteMixin`

**Frontend Standards:**
- Use `<script setup lang="ts">` in single-file components
- Absolute imports with `@/` alias (configured in vite.config.ts)
- Keep components under 300 lines (split if larger)
- Use Composition API style for Pinia stores
- Define types in `src/stores/types.ts` or component-level

**Testing Standards:**
- Use fixtures from `tests/conftest.py`
- Mark tests: `@pytest.mark.unit`, `@pytest.mark.integration`
- Test database uses in-memory SQLite (not PostgreSQL)
- Follow AAA pattern (Arrange, Act, Assert)
- Descriptive test names: `test_login_with_valid_credentials_succeeds`

## Implementation Roadmap

### Current Sprint: Split Analysis Feature (In Progress)

**Status**: Design Complete, Frontend UI Complete, Backend Pending

**Completed** ✅:
1. ✅ Feature design document (15 sections)
2. ✅ Implementation plan (12 tasks, 35+ steps)
3. ✅ Frontend UI components (3 files: RuleEnginePanel, LLMPanel, AIOptimizeButton)
4. ✅ TypeScript types updated (RuleBasedResult, LLMResult, LearningAnalysis)
5. ✅ Pinia store updated (new state and actions)
6. ✅ API client updated (new methods)

**Pending** 🔄:
1. 🔄 Backend type definitions (LTError, RuleBasedResult, LLMResult, etc.)
2. 🔄 Database model updates (ea_error_details, ea_learning_recommendations, ea_user_error_trends)
3. 🔄 Pipeline refactoring (analyze_rules_only, optimize_with_llm methods)
4. 🔄 LLM learning insights generation
5. 🔄 API endpoints implementation (/analyze/rules-only, /analyze/optimize-llm)
6. 🔄 Database migration (Alembic)
7. 🔄 Testing (unit, integration, API tests)

**Next Steps**:
- Run `/init` to initialize development environment
- Execute implementation plan: `docs/plans/2026-02-05-split-analysis-implementation.md`
- Follow TDD approach: write tests → implement → verify → commit

## Project Status Summary

**Design Complete**: ✅
- Feature specification: 15 sections covering architecture, API, database, UI
- Implementation plan: 12 tasks, 35+ steps with complete code
- UI components: 4 Vue files created with TypeScript

**Implementation Status**: 🔄 In Progress
- Frontend: ✅ UI components complete (RuleEnginePanel, LLMPanel, AIOptimizeButton)
- Frontend: ✅ Types and store updated for split analysis
- Backend: 🔄 Ready to implement (plan available)
- Backend: 🔄 Database migration pending
- Testing: 🔄 Test suite to be written

**Branch**: `feature/mvp_v1` (commit: updates pending)
**Documentation**:
- Design: `docs/plans/2026-02-05-function-split-design.md`
- Implementation: `docs/plans/2026-02-05-split-analysis-implementation.md`
- Architecture: `docs/04-technical-design/architecture.md`

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
- PostgreSQL: localhost:5432

**Additional Documentation**:
- `AGENTS.md` - Comprehensive development guide and coding standards
- `scripts/README.md` - Detailed script usage and troubleshooting

## Testing the Analyze Endpoint

The main analyze endpoint is operational and can be tested:

```bash
# Test anonymous user analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "She dont like pizza.", "mode": "accuracy"}'

# Expected response includes:
# - analysis_id
# - original_text and corrected_text
# - errors array with detailed error information
# - statistics (total_errors, error_types, severity_distribution)
# - processing_time_ms and token_usage
```

**Test Results:**
- Processing time: ~12 seconds for initial request
- Subsequent requests cached (faster response)
- Errors correctly identified and classified
- Database records created automatically
