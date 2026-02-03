# MVP Completion Design - English Transfer Assistant

**Date:** 2026-02-03
**Status:** Approved
**Approach:** Critical Path First (Option A)
**Estimated Effort:** 40-60 hours

## Overview

This design completes the English Transfer Assistant MVP by implementing the critical path first: getting the core text analysis flow working end-to-end, then adding authentication and secondary features.

## Implementation Phases

### Phase 1: Database Setup & Migrations

**Goal:** Initialize Alembic and create database schema with `ea_` prefix

**Tasks:**
1. Update SQLAlchemy Models with Table Prefix
   - Add `__tablename__ = "ea_users"` to User model
   - Add `__tablename__ = "ea_analysis"` to Analysis model
   - Add `__tablename__ = "ea_error_details"` to ErrorDetail model
   - Add `__tablename__ = "ea_user_settings"` to UserSettings model
   - Add `__tablename__ = "ea_api_credits"` to APICredit model
   - Add `__tablename__ = "ea_tags"` to Tag model
   - Add `__tablename__ = "ea_analysis_tags"` to AnalysisTag model
   - Add `__tablename__ = "ea_analysis_cache"` to AnalysisCache model
   - Update foreign key references to use prefixed table names

2. Configure Alembic (`alembic.ini` + `alembic/env.py`)
   - Point to PostgreSQL connection string from environment variables
   - Import all models from `backend/models/`
   - Use async engine (SQLAlchemy 2.0 async pattern)

3. Create Initial Migration
   - Run `alembic revision --autogenerate -m "Initial schema with ea_ prefix"`
   - Review migration for correctness (foreign keys, indexes, constraints)
   - Verify all tables have `ea_` prefix

4. Add Performance-Critical Indexes
   - `ea_analysis.user_id` (for history queries)
   - `ea_analysis.created_at` (for sorting)
   - `ea_error_details.analysis_id` (for error lookups)
   - `ea_analysis_cache.text_hash` (for cache hits)
   - `ea_analysis_cache.expires_at` (for cleanup)

5. Apply Migration
   - Run `alembic upgrade head`
   - Verify with database client that all tables have `ea_` prefix

**Why First:** Database schema unblocks all API endpoints that need to save data.

---

### Phase 2: Core Analysis Flow

**Goal:** Implement POST /api/v1/analyze endpoint with full pipeline integration

**Endpoint:** `POST /api/v1/analyze`

**Request:**
```json
{
  "text": "I go to park yesterday.",
  "mode": "accuracy" | "naturalness"
}
```

**Implementation Flow:**

1. **Request Validation**
   - Text length: 5-5000 characters
   - Mode: must be "accuracy" or "naturalness"
   - Return 400 if invalid

2. **Rate Limiting Check**
   - Use `RateLimitService.check_rate_limit(user_id or ip_address)`
   - Tier limits: anonymous (5/hour), free (50/day), paid (500/day)
   - Return 429 if exceeded

3. **Cache Check** (Local In-Memory Cache)
   - Generate cache key: `sha256(f"{text}:{mode}")`
   - Check `CacheService.get(cache_key)` (uses in-memory LRU cache)
   - If hit: return cached result immediately
   - **Note:** Using local cache (not Redis) for MVP simplicity

4. **Run Pipeline**
   - Initialize `AnalysisPipeline()`
   - Call `result = await pipeline.analyze(text, mode)`
   - Pipeline handles:
     - Preprocessing (sentence split, speaker detection, Chinese detection)
     - Rule-based correction (LanguageTool)
     - LLM optimization (Zhipu AI with fallback)
     - Result merging
   - Graceful degradation if LLM fails

5. **Save to Database**
   - Create `Analysis` record:
     - user_id (optional for anonymous)
     - original_text, corrected_text
     - mode, status="completed"
   - Create `ErrorDetail` records (one per error)
   - Commit transaction

6. **Cache Result** (Local In-Memory Cache)
   - `CacheService.set(cache_key, result, ttl=86400)` (24 hours)
   - **Note:** Using in-memory LRU cache with automatic eviction

7. **Return Response**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "original_text": "...",
    "corrected_text": "...",
    "errors": [
      {
        "error_type": "grammar",
        "severity": "high",
        "position": {"start": 5, "end": 7},
        "message": "Missing article",
        "original": "go to park",
        "suggestion": "go to the park"
      }
    ],
    "stats": {
      "total_errors": 2,
      "by_type": {"grammar": 1, "tense": 1}
    }
  }
}
```

**Error Handling:**
- Pipeline failure → status="failed", return partial results if available
- Database error → rollback transaction, return 500
- All errors logged with context

---

### Phase 3: Authentication Flow

**Goal:** Implement user registration, login, token management

**Endpoints:**

#### 1. POST /api/v1/auth/register

**Request:**
```json
{
  "email": "user@example.com",
  "username": "user123",
  "password": "SecurePass123"
}
```

**Implementation:**
- Validate email format, password strength (min 8 chars)
- Check username/email uniqueness
- Hash password using `password_service.hash_password()`
- Create `User` record (tier="free")
- Create `APICredit` record (credits=50)
- Generate JWT tokens (access + refresh)

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {"id": "uuid", "email": "...", "username": "...", "tier": "free"},
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

#### 2. POST /api/v1/auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Implementation:**
- Lookup user by email
- Verify password using `password_service.verify_password()`
- Generate JWT tokens (access=15min, refresh=7days)

**Response:** Same as register

#### 3. POST /api/v1/auth/refresh

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Implementation:**
- Verify refresh token signature and expiry
- Generate new access token
- Return new access token

#### 4. GET /api/v1/auth/me

**Headers:** `Authorization: Bearer <access_token>`

**Implementation:**
- Use `get_current_user()` dependency
- Decode JWT, validate, fetch user
- Return user profile + remaining credits

**JWT Configuration:**
- Secret: from `JWT_SECRET` env var
- Algorithm: HS256
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days

**MVP Simplifications:**
- No email verification
- No password reset flow
- No OAuth/social login

---

### Phase 4: Frontend-Backend Integration

**Goal:** Connect frontend components to working backend APIs

**Tasks:**

#### 1. Update analysisStore

Implement `analyzeText()` action:
```typescript
async analyzeText(text: string, mode: CorrectionMode) {
  this.isAnalyzing = true
  this.error = null

  try {
    const response = await analysisApi.analyze({ text, mode })

    this.currentResult = response.data
    this.originalText = text
    this.correctedText = response.data.corrected_text
    this.errors = response.data.errors

    historyStore.addItem(response.data)

  } catch (err) {
    this.error = err.message
    uiStore.showToast('Analysis failed', 'error')
  } finally {
    this.isAnalyzing = false
  }
}
```

#### 2. Fix Type Mismatches

- Ensure frontend types match backend response
- Backend uses snake_case: `error_type`, `corrected_text`
- Frontend may need camelCase conversion or type alignment

#### 3. Axios Error Interceptor

Handle specific error codes:
- 400 → Display validation errors
- 401 → Trigger token refresh flow
- 429 → Show "Rate limit exceeded" toast
- 500 → Show generic error message

#### 4. Loading States

Wire up UI indicators:
- Disable input during `isAnalyzing`
- Show progress spinner
- Display skeleton loaders in result panels

#### 5. Integration Test Checklist

Manual verification:
- [ ] Paste text → click "Analyze" → see results
- [ ] Loading state shows during processing
- [ ] Results appear in Input, Compare, Analysis panels
- [ ] Error highlighting works
- [ ] Click error card → scroll to highlighted text
- [ ] Copy corrected text button works
- [ ] Layout switching works (4 modes)
- [ ] View switching works (side-by-side, original, corrected)

---

### Phase 5: Secondary Features

**Goal:** Implement history, statistics, settings endpoints

#### 1. History Endpoints

**GET /api/v1/history**
- Query params: `page=1, limit=20, sort_by=created_at`
- Filter by user_id (from JWT)
- Return paginated Analysis records with error counts

**GET /api/v1/history/{id}**
- Return single Analysis with all ErrorDetails
- Verify ownership (user_id matches token)
- Return 404 if not found or 403 if not owned

**DELETE /api/v1/history/{id}**
- Soft delete: set `deleted_at`, `is_deleted=true`
- Verify ownership
- Return 204 on success

#### 2. Statistics Endpoint

**GET /api/v1/statistics/overview**
- Aggregate stats: total_analyses, total_errors
- Group by error_type and count
- Filter by user_id and optional date range
- Return error type distribution

**Response:**
```json
{
  "success": true,
  "data": {
    "total_analyses": 42,
    "total_errors": 156,
    "error_distribution": {
      "grammar": 45,
      "tense": 30,
      "word_choice": 25,
      "spelling": 20
    },
    "most_common_errors": [
      {"type": "grammar", "count": 45},
      {"type": "tense", "count": 30}
    ]
  }
}
```

#### 3. Settings Endpoints

**GET /api/v1/settings**
- Return UserSettings for current user
- Create default settings if none exist

**PUT /api/v1/settings**
- Update: dark_mode, correction_mode, notification preferences
- Validate input
- Return updated settings

#### 4. Export Endpoint (Optional)

**POST /api/v1/export**
- Accept: `{analysis_id, format: "json" | "markdown"}`
- Generate file content
- Return download response
- **Defer PDF to v2**

**Prioritization:**
- **Must-have:** History GET endpoints
- **Should-have:** Statistics, Settings
- **Can-defer:** Export, History DELETE

---

### Phase 6: Error Handling & Testing

**Goal:** Standardize error responses and add critical tests

#### 1. Unified Error Response Format

All errors return:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded your rate limit",
    "details": {"limit": 50, "reset_in": 3600}
  }
}
```

**Error Codes:**
- `INVALID_INPUT` - Validation errors
- `UNAUTHORIZED` - Missing/invalid token
- `TOKEN_EXPIRED` - JWT expired
- `RATE_LIMIT_EXCEEDED` - Rate limit hit
- `ANALYSIS_FAILED` - Pipeline error
- `LLM_ERROR` - Zhipu AI failure
- `GRAMMAR_TOOL_ERROR` - LanguageTool failure
- `NOT_FOUND` - Resource not found
- `FORBIDDEN` - Insufficient permissions

#### 2. Global Exception Handler

Add to `main.py`:
- Catch all unhandled exceptions
- Log with full traceback
- Return 500 with safe message (no internal leakage)
- Special handling for ValidationError, HTTPException

#### 3. Pipeline Error Handling

Ensure graceful degradation:
- LLM fails → use LanguageTool only
- LanguageTool fails → try LLM only
- Both fail → return 500 with partial preprocessing results
- Log which stage failed

#### 4. Testing Strategy

**Phase 1 - Critical Path Tests:**
- `test_analyze_endpoint.py` - Full analysis flow
- `test_pipeline_integration.py` - Pipeline with real LanguageTool (mock Zhipu)
- `test_auth_flow.py` - Register, login, refresh

**Phase 2 - Unit Tests:**
- Pipeline stages individually
- Rate limiting logic
- Cache service
- Password hashing

**Phase 3 - Frontend Tests (Optional for MVP):**
- Defer to v2

**Coverage Target:**
- Backend: 60%+ (critical paths)
- Frontend: v2

**Testing Tools:**
- pytest with fixtures from `conftest.py`
- Mock Zhipu AI for most tests
- In-memory SQLite for test database
- Focus on happy path + critical error cases

---

## Implementation Order Summary

1. **Database Setup** (Day 1)
   - Configure Alembic
   - Create and apply initial migration
   - Verify schema

2. **Core Analysis** (Days 2-3)
   - Implement `/api/v1/analyze` endpoint
   - Integrate pipeline
   - Add rate limiting and caching
   - Test with real LanguageTool and Zhipu AI

3. **Authentication** (Days 4-5)
   - Implement 4 auth endpoints
   - Add JWT middleware
   - Test auth flow

4. **Frontend Integration** (Days 6-7)
   - Connect stores to APIs
   - Fix type mismatches
   - Test end-to-end flow
   - Verify all UI interactions

5. **Secondary Features** (Days 8-9)
   - History endpoints
   - Statistics endpoint
   - Settings endpoints
   - Test each feature

6. **Error Handling & Testing** (Days 10-12)
   - Standardize error responses
   - Write critical path tests
   - Fix bugs found during testing
   - Achieve 60% backend coverage

## Success Criteria

**MVP Complete When:**
- [ ] User can register and login
- [ ] User can paste text and see corrections
- [ ] All 3 panels work (Input, Compare, Analysis)
- [ ] Error highlighting and click-to-scroll works
- [ ] History page shows past analyses
- [ ] Statistics page shows error distribution
- [ ] Settings can be updated
- [ ] Rate limiting enforces tier limits
- [ ] Critical path tests pass
- [ ] No major bugs in core flow

## Technical Decisions

### Database Table Naming
- **Prefix:** All tables use `ea_` prefix (English Assistant)
- **Rationale:** Namespace isolation, prevents conflicts in shared databases
- **Tables:** ea_users, ea_analysis, ea_error_details, ea_user_settings, ea_api_credits, ea_tags, ea_analysis_tags, ea_analysis_cache

### Caching Strategy
- **MVP:** Local in-memory LRU cache (via CacheService)
- **Rationale:** Simpler deployment, no Redis dependency for single-instance MVP
- **TTL:** 24 hours for analysis results
- **Eviction:** Automatic LRU when memory limit reached
- **V2:** Consider Redis for multi-instance deployments

---

## Out of Scope (v2)

- Email verification
- Password reset
- OAuth/social login
- PDF export
- Real-time editing mode
- Advanced statistics (charts, trends)
- User profile customization
- Admin dashboard
- Distributed Redis caching (multi-instance scaling)

---

**Design Approved:** 2026-02-03
**Ready for Implementation:** Yes
