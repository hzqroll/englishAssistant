# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**English Transfer Assistant** is an AI-powered English text correction and analysis tool designed for English learners. The project helps users improve their English writing through intelligent error detection, correction, and structured explanations.

### Current Status
- **Phase**: Planning & Design (Phase 2)
- **Implementation**: Not started (0%)
- **Documentation**: Complete (see `/docs` directory)

### Tech Stack (Planned)

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL for data storage
- Redis for rate limiting and caching
- LanguageTool for grammar checking
- Zhipu AI (GLM-4-Flash) for LLM-powered optimizations
- JWT authentication
- Poetry for dependency management

**Frontend:**
- Vue 3 with Composition API
- TypeScript
- Vite for building
- Pinia for state management
- Tailwind CSS for styling
- Vue Router for navigation

**Infrastructure:**
- Docker + Docker Compose
- Nginx as reverse proxy

## Core Architecture

### 4-Stage Pipeline (Backend)

The text correction system uses a **4-stage pipeline**:

1. **Preprocessing** (`pipeline/preprocessor.py`)
   - Sentence splitting
   - Speaker detection (for dialogues)
   - Chinese character detection
   - Output: `List[Message]` with metadata

2. **Rule-Based Correction** (`pipeline/rule_checker.py`)
   - LanguageTool integration for grammar, spelling, tense errors
   - Error classification (grammar, tense, word_choice, etc.)
   - Severity assessment
   - Output: Preliminary corrections + error list

3. **LLM Optimization** (`pipeline/llm_optimizer.py`)
   - Zhipu AI for naturalness improvement
   - Intent detection (text type, tone, speakers)
   - Chinese-English mixing correction
   - Output: Optimized text + suggestions

4. **Post-Processing** (`pipeline/postprocessor.py`)
   - Merge rule-based and LLM results
   - Generate structured error reports
   - Create learning tips based on error patterns
   - Output: Final `CorrectionResult` JSON

### Database Schema

**Core Tables:**
- `users` - User accounts, authentication, subscription tier
- `conversations` (to be renamed to `analyses`) - Text analysis records
- `error_details` - Individual error entries linked to analyses
- `request_logs` - API request tracking for rate limiting

**Key Relationships:**
- One user → many analyses
- One analysis → many error details

### Frontend Component Structure

```
App.vue
├── Navbar.vue
├── MainLayout.vue
│   ├── InputPanel.vue (text input, mode selection)
│   ├── ComparePanel.vue (side-by-side comparison view)
│   └── AnalysisPanel.vue (error cards with explanations)
├── LayoutControls.vue (quick layout presets)
└── Toast.vue (global notifications)
```

**Key State (Pinia Stores):**
- `analysisStore` - Current analysis state, view modes, panel states
- `historyStore` - User's analysis history
- `userStore` - Authentication and user settings

## Development Commands

### Backend (when implemented)
```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn backend.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black backend/
poetry run ruff check backend/

# Database migrations
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"
```

### Frontend (when implemented)
```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint and format
npm run lint
npm run format
```

### Docker (when implemented)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up -d --build backend
```

## Key Design Decisions

### MVP: Batch Processing, Not Real-Time
The v1.0 focuses on batch text correction (not real-time) because:
1. **Better Learning Value**: Detailed error analysis with explanations
2. **Technical Feasibility**: No need for <1s response times or WebSockets
3. **Cost Control**: Can optimize API calls, implement caching
4. **Market Fit**: 4 of 5 core use cases are batch scenarios

### Two Correction Modes
- **Accuracy First**: Fix only grammatical errors, preserve original style
- **Naturalness First**: Rewrite to sound more natural (may change structure)

### Rate Limiting Strategy (Tiers)
- Anonymous: 5 requests/hour
- Free users: 50 requests/day
- Paid users: 500 requests/day

### LLM Fallback Strategy
- If Zhipu AI fails → degrade to LanguageTool-only results
- If LanguageTool fails → try LLM-only processing
- Always return partial results rather than complete failures

## API Design (Planned)

**Base URL:** `/api/v1`

**Core Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT)
- `POST /auth/refresh` - Refresh access token
- `POST /analyze` - Analyze and correct text (main endpoint)
- `GET /history` - Get user's analysis history (paginated)
- `GET /history/{id}` - Get specific analysis details
- `DELETE /history/{id}` - Delete analysis record
- `GET /statistics/overview` - Get error statistics and trends
- `POST /export` - Export analysis results (JSON/Markdown/PDF)
- `GET /settings` - Get user settings
- `PUT /settings` - Update user settings

**Response Format:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Codes:**
- `400 INVALID_INPUT` - Invalid request data
- `401 UNAUTHORIZED` - Missing or invalid token
- `401 TOKEN_EXPIRED` - JWT token expired
- `429 RATE_LIMIT_EXCEEDED` - Rate limit hit
- `500 ANALYSIS_FAILED` - Pipeline processing failed
- `500 LLM_ERROR` - Zhipu AI service error
- `500 GRAMMAR_TOOL_ERROR` - LanguageTool error

## Important File Locations

**Design Documents:**
- `/docs/04-technical-design/architecture.md` - System architecture, database schema, pipeline design
- `/docs/04-technical-design/technical-implementation-plan.md` - API endpoints, component structure, state management
- `/docs/03-product-features/product-capabilities.md` - Product capabilities and features
- `/docs/03-product-features/functional-requirements.md` - Detailed functional requirements with use cases

**Task Tracking:**
- `/docs/05-tasks/implementation-checklist.md` - Complete implementation task list (100+ items)

**UI Design:**
- `/docs/02-ui-design/ui-final.html` - Interactive HTML prototype

## External Services Integration

### Zhipu AI (智谱 AI)
- **SDK**: `zhipuai` Python package
- **Model**: GLM-4-Flash (faster, cheaper)
- **Usage**: Intent detection, naturalness optimization, Chinese-English correction
- **Cost Optimization**:
  - Use Flash model (10x cheaper than standard)
  - Batch processing (10 sentences per call)
  - 24-hour caching for identical inputs
  - Graceful degradation to rule-based engine

### LanguageTool
- **Python Package**: `language-tool-python`
- **Usage**: Grammar, spelling, tense, style checking
- **Error Mapping**: Maps LanguageTool categories to UI error types (grammar, tense, word_choice, etc.)

## Development Priorities

### P0 (MVP - Blocking)
1. Backend pipeline basic flow
2. Core API endpoints (analyze, history)
3. Frontend three-panel layout
4. Analysis result display
5. Integration: Zhipu AI + LanguageTool

### P1 (Important but Non-Blocking)
1. Authentication module
2. Statistics module
3. History management
4. Panel collapse functionality
5. Layout switching

### P2 (Enhancement)
1. Export module
2. View switching (original-only/corrected-only)
3. Search and filter
4. Learning tips display
5. Card expansion animations

## Testing Strategy (When Implementing)

**Backend:**
- Unit tests for each pipeline stage
- Mock external services (Zhipu AI, LanguageTool)
- Integration tests for API endpoints
- Rate limiting tests

**Frontend:**
- Component unit tests (Vitest)
- Store unit tests
- API client tests
- E2E tests (Playwright)

**Performance:**
- Pipeline processing time by text length
- API concurrent request handling
- Frontend rendering with large error lists

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Zhipu AI instability | High | Fallback to LanguageTool-only results |
| LanguageTool performance | Medium | Async processing + caching |
| Pipeline processing time | High | Streaming results + progress indicators |
| Cost overruns | High | Strict rate limits + Flash model + caching |
| Complex frontend state | Medium | Use Pinia, simplify state flow |

## Product Roadmap

**v1.0 (MVP)** - Batch correction tool
- Paste any English text
- 4-stage deep correction pipeline
- Side-by-side comparison view
- Error highlights with explanations
- Export learning notes
- History (last 10 records)

**v1.5** - Enhanced batch experience
- Import files (TXT, JSON, Markdown)
- Error statistics and trends
- Personal learning space
- PDF export

**v2.0** - Real-time mode
- Real-time conversation correction
- Fast response mode
- Mobile support

## Documentation Notes

- All technical design is in `/docs/04-technical-design/`
- Product planning is in `/docs/01-product-research/` and `/docs/03-product-features/`
- Implementation checklist has 100+ detailed tasks
- UI prototype is available as interactive HTML
- Project uses Chinese for documentation (English for code)

## Next Steps for Implementation

1. **Phase 3.1**: Initialize backend (FastAPI + Poetry) and frontend (Vue 3 + Vite) projects
2. **Phase 3.2**: Implement 4-stage pipeline core logic
3. **Phase 3.3**: Build main API endpoints and Vue components
4. **Phase 3.4**: Add comprehensive testing
5. **Phase 3.5**: Docker deployment setup

See `/docs/05-tasks/implementation-checklist.md` for complete task breakdown.
