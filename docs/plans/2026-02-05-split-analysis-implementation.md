# Function Split Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement sequential analysis with LanguageTool (fast, free) and optional LLM optimization (costly, AI-powered) with learning recommendations

**Architecture:** Split the current 4-stage pipeline into two sequential phases:
- Phase 1: Preprocessing + LanguageTool (rules-only) - returns in 2-4 seconds
- Phase 2: Optional LLM optimization + learning insights - triggered by user, costs tokens

**Tech Stack:** Python 3.11+, FastAPI, LanguageTool, Zhipu AI GLM-4, PostgreSQL, SQLAlchemy

---

## Prerequisites

**Read these docs first:**
- `docs/plans/2026-02-05-function-split-design.md` - Complete design specification
- `backend/pipeline/analysis_pipeline.py` - Current pipeline implementation
- `backend/pipeline/rule_engine.py` - LanguageTool integration
- `backend/pipeline/llm_engine.py` - LLM integration

**Frontend is already complete:**
- `frontend/src/components/panels/RuleEnginePanel.vue` - Displays LT results
- `frontend/src/components/panels/LLMPanel.vue` - Displays LLM results
- `frontend/src/components/panels/AIOptimizeButton.vue` - Floating trigger button
- `frontend/src/stores/types.ts` - TypeScript interfaces defined
- `frontend/src/api/analysis.ts` - API client methods ready

---

## Task 1: Add New Type Definitions

**Files:**
- Create: `backend/models/types.py` (if not exists) or modify `backend/models/__init__.py`

**Step 1: Add new dataclass types**

```python
# backend/models/types.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class LTError:
    """LanguageTool error detail"""
    rule_id: str
    category: str  # GRAMMAR, TYPOS, PUNCTUATION, etc.
    severity: str  # ERROR, WARNING
    position_start: int
    position_end: int
    original_text: str
    replacements: List[str]
    message: str
    context: str

@dataclass
class RuleBasedStatistics:
    """Statistics from rule-based analysis"""
    total_errors: int
    by_category: Dict[str, int]

@dataclass
class RuleBasedResult:
    """Result from LanguageTool-only analysis"""
    analysis_id: str
    errors: List[LTError]
    corrected_text: str
    statistics: RuleBasedStatistics
    processing_time_ms: int
    estimated_llm_tokens: int

@dataclass
class ErrorPattern:
    """Error pattern for learning analysis"""
    pattern_name: str
    frequency: str  # "43%"
    examples: List[Dict[str, str]]
    severity: str  # high, medium, low

@dataclass
class LearningResource:
    """Learning resource recommendation"""
    type: str  # grammar_rule, practice_exercise
    title: str
    content: Optional[str] = None
    difficulty: Optional[str] = None

@dataclass
class LearningRecommendation:
    """Personalized learning recommendation"""
    priority: int
    topic: str
    description: str
    resources: List[LearningResource]
    estimated_study_time: str

@dataclass
class HistoricalTrend:
    """User's historical error trend"""
    comparison: str  # improving, stable, worsening
    since_last_week: str
    most_improved: str
    needs_attention: str

@dataclass
class LearningAnalysis:
    """Complete learning analysis from LLM"""
    error_patterns: List[ErrorPattern]
    ea_learning_recommendations: List[LearningRecommendation]
    personalized_tips: List[str]
    historical_trend: Optional[HistoricalTrend] = None

@dataclass
class LLMSuggestion:
    """Single LLM optimization suggestion"""
    type: str  # naturalness, style_variant, etc.
    sentence_index: int
    original: str
    suggestion: str
    explanation: str
    confidence: float

@dataclass
class ChineseCorrection:
    """Chinese-English mixing correction"""
    original: str
    corrected: str

@dataclass
class LLMResult:
    """Result from LLM optimization"""
    optimized_text: str
    suggestions: List[LLMSuggestion]
    chinese_corrections: List[ChineseCorrection]
    learning_analysis: LearningAnalysis
    token_usage: int
```

**Step 2: Run type check**

Run: `cd backend && poetry run mypy models/types.py`
Expected: No errors (may have unused import warnings, that's OK)

**Step 3: Commit**

```bash
git add backend/models/types.py
git commit -m "feat(types): add dataclasses for split analysis feature"
```

---

## Task 2: Update Database Models

**Files:**
- Modify: `backend/models/analysis.py` (or wherever Analysis model is defined)

**Step 1: Add status field to Analysis model**

Find the existing `Analysis` class and add:

```python
# backend/models/analysis.py

from sqlalchemy import Column, String, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB

class Analysis(Base):
    # ... existing fields ...

    # Add these new fields
    status = Column(String(20), default='rule_only')  # 'rule_only', 'completed', 'failed'
    llm_tokens_used = Column(Integer, default=0)
    llm_cost_usd = Column(DECIMAL(10, 4), default=0)
```

**Step 2: Create ErrorDetail model**

```python
# backend/models/error_detail.py

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class ErrorDetail(Base):
    __tablename__ = 'ea_error_details'

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('ea_analyses.id', ondelete='CASCADE'))
    rule_id = Column(String(100))  # LanguageTool rule_id
    category = Column(String(50))  # GRAMMAR, TYPOS, etc.
    severity = Column(String(20))  # ERROR, WARNING
    position_start = Column(Integer)
    position_end = Column(Integer)
    original_text = Column(Text)
    correction = Column(Text)
    message = Column(Text)
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    analysis = relationship("Analysis", back_populates="ea_error_details")
```

**Step 3: Create LearningRecommendation model**

```python
# backend/models/learning_recommendation.py

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, DECIMAL, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class LearningRecommendation(Base):
    __tablename__ = 'ea_learning_recommendations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ea_users.id', ondelete='CASCADE'))
    analysis_id = Column(Integer, ForeignKey('ea_analyses.id', ondelete='CASCADE'))
    pattern_name = Column(String(200))
    frequency = Column(DECIMAL(5, 2))  # Percentage as decimal
    severity = Column(String(20))  # high, medium, low
    recommendation = Column(Text)
    resources = Column(JSONB)  # Store as JSON
    priority = Column(Integer)
    estimated_study_time = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    analysis = relationship("Analysis")
```

**Step 4: Create UserErrorTrend model**

```python
# backend/models/user_error_trend.py

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class UserErrorTrend(Base):
    __tablename__ = 'ea_user_error_trends'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ea_users.id', ondelete='CASCADE'))
    pattern_name = Column(String(200))
    error_count = Column(Integer, default=0)
    trend_direction = Column(String(20))  # improving, stable, worsening
    last_calculated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('user_id', 'pattern_name', name='unique_user_pattern'),
    )
```

**Step 5: Update Analysis model relationships**

```python
# In backend/models/analysis.py, add to Analysis class:

from sqlalchemy.orm import relationship

class Analysis(Base):
    # ... existing fields ...

    # Add relationships
    ea_error_details = relationship("ErrorDetail", back_populates="analysis", cascade="all, delete-orphan")
    ea_learning_recommendations = relationship("LearningRecommendation", back_populates="analysis", cascade="all, delete-orphan")
```

**Step 6: Run type check**

Run: `cd backend && poetry run mypy models/`
Expected: No critical errors

**Step 7: Create migration**

Run: `cd backend && poetry run alembic revision --autogenerate -m "add split analysis fields and tables"`

**Step 8: Review generated migration**

Check: `backend/alembic/versions/<newest_file>.py`
Ensure it has: ALTER TABLE ea_analyses, CREATE TABLE ea_error_details, CREATE TABLE ea_learning_recommendations, CREATE TABLE ea_user_error_trends

**Step 9: Commit**

```bash
git add backend/models/ backend/alembic/versions/
git commit -m "feat(models): add status field and new tables for split analysis"
```

---

## Task 3: Implement analyze_rules_only in Pipeline

**Files:**
- Modify: `backend/pipeline/analysis_pipeline.py`

**Step 1: Add import for new types**

```python
# backend/pipeline/analysis_pipeline.py

from models.types import (
    RuleBasedResult,
    LTError,
    RuleBasedStatistics,
    LLMResult,
    LearningAnalysis
)
```

**Step 2: Add token estimation helper**

```python
# In AnalysisPipeline class

def _estimate_llm_tokens(self, text: str) -> int:
    """
    Estimate LLM token consumption

    Rule: ~1 token = 4 characters (English) + 500 tokens system prompt
    """
    char_count = len(text)
    base_tokens = char_count // 4
    system_tokens = 500
    return base_tokens + system_tokens
```

**Step 3: Add calculate_statistics helper**

```python
# In AnalysisPipeline class

def _calculate_statistics(self, errors: List[LTError]) -> RuleBasedStatistics:
    """Calculate error statistics by category"""
    by_category = {}
    for error in errors:
        category = error.category
        by_category[category] = by_category.get(category, 0) + 1

    return RuleBasedStatistics(
        total_errors=len(errors),
        by_category=by_category
    )
```

**Step 4: Add convert_lt_errors helper**

```python
# In AnalysisPipeline class

def _convert_lt_errors(self, lt_matches: List) -> List[LTError]:
    """Convert LanguageTool matches to LTError objects"""
    errors = []
    for match in lt_matches:
        errors.append(LTError(
            rule_id=match.ruleId,
            category=match.category,
            severity=match.ruleIssueType,
            position_start=match.offset,
            position_end=match.offset + match.errorLength,
            original_text=match.context[match.offset:match.offset + match.errorLength],
            replacements=match.replacements[:3],  # Top 3 suggestions
            message=match.message,
            context=match.context
        ))
    return errors
```

**Step 5: Implement analyze_rules_only method**

```python
# In AnalysisPipeline class, after the existing analyze method

async def analyze_rules_only(
    self,
    text: str,
    mode: CorrectionMode,
    user_id: Optional[int] = None,
    session: AsyncSession = None
) -> RuleBasedResult:
    """
    Fast analysis using LanguageTool only

    Returns RuleBasedResult with analysis_id for optional LLM optimization later
    """
    start_time = time.time()

    # Stage 1: Preprocessing
    preprocessed = await self.preprocessor.preprocess(text)

    # Stage 2: LanguageTool check
    rule_result = await self.rule_engine.check(preprocessed, mode)

    # Convert errors
    lt_errors = self._convert_lt_errors(rule_result.errors)

    # Calculate statistics
    statistics = self._calculate_statistics(lt_errors)

    # Save to database (status='rule_only')
    from sqlalchemy import select
    from models.analysis import Analysis

    analysis = Analysis(
        user_id=user_id,
        original_text=text,
        corrected_text=rule_result.corrected_text,
        mode=mode.value,
        status='rule_only',
        processing_time_ms=int((time.time() - start_time) * 1000)
    )

    session.add(analysis)
    await session.flush()  # Get the ID without committing

    # Save error details
    from models.error_detail import ErrorDetail

    for error in lt_errors:
        error_detail = ErrorDetail(
            analysis_id=analysis.id,
            rule_id=error.rule_id,
            category=error.category,
            severity=error.severity,
            position_start=error.position_start,
            position_end=error.position_end,
            original_text=error.original_text,
            correction=error.replacements[0] if error.replacements else None,
            message=error.message,
            context=error.context
        )
        session.add(error_detail)

    await session.commit()

    # Estimate LLM tokens
    estimated_tokens = self._estimate_llm_tokens(text)

    return RuleBasedResult(
        analysis_id=str(analysis.id),
        errors=lt_errors,
        corrected_text=rule_result.corrected_text,
        statistics=statistics,
        processing_time_ms=int((time.time() - start_time) * 1000),
        estimated_llm_tokens=estimated_tokens
    )
```

**Step 6: Run type check**

Run: `cd backend && poetry run mypy pipeline/analysis_pipeline.py`
Expected: No critical errors

**Step 7: Commit**

```bash
git add backend/pipeline/analysis_pipeline.py
git commit -m "feat(pipeline): add analyze_rules_only method"
```

---

## Task 4: Implement LLM Learning Analysis

**Files:**
- Modify: `backend/pipeline/llm_engine.py`

**Step 1: Add imports**

```python
# backend/pipeline/llm_engine.py

from models.types import (
    LearningAnalysis,
    ErrorPattern,
    LearningRecommendation,
    LearningResource,
    HistoricalTrend
)
```

**Step 2: Add error pattern extraction helper**

```python
# In LLMEngine class

def _extract_error_patterns(self, lt_errors: List) -> List[ErrorPattern]:
    """Extract error patterns from LanguageTool errors"""
    from collections import Counter

    # Group by rule_id
    rule_groups = {}
    for error in lt_errors:
        rule_id = error.rule_id
        if rule_id not in rule_groups:
            rule_groups[rule_id] = []
        rule_groups[rule_id].append(error)

    # Calculate frequencies
    total = len(lt_errors)
    patterns = []

    for rule_id, errors in rule_groups.items():
        frequency = f"{int((len(errors) / total) * 100)}%"

        # Determine severity based on frequency
        freq_percent = (len(errors) / total) * 100
        if freq_percent >= 40:
            severity = "high"
        elif freq_percent >= 20:
            severity = "medium"
        else:
            severity = "low"

        # Get examples (max 3)
        examples = [
            {
                "original": e.original_text,
                "corrected": e.replacements[0] if e.replacements else ""
            }
            for e in errors[:3]
        ]

        # Pattern name from rule_id or category
        pattern_name = f"{errors[0].category} Error ({rule_id})"

        patterns.append(ErrorPattern(
            pattern_name=pattern_name,
            frequency=frequency,
            examples=examples,
            severity=severity
        ))

    # Sort by frequency (high to low)
    patterns.sort(key=lambda p: int(p.frequency.rstrip('%')), reverse=True)

    return patterns[:5]  # Top 5 patterns
```

**Step 3: Add historical trend analysis helper**

```python
# In LLMEngine class

async def _analyze_historical_trends(
    self,
    session: AsyncSession,
    user_id: Optional[int],
    days: int = 30
) -> Optional[HistoricalTrend]:
    """Analyze user's error trends over time"""

    if not user_id:
        return None

    from sqlalchemy import select, func
    from models.error_detail import ErrorDetail
    from models.analysis import Analysis
    from datetime import timedelta, datetime

    # Get date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get old analyses (first week)
    old_start = start_date
    old_end = start_date + timedelta(days=days // 2)

    # Get recent analyses (last week)
    recent_start = end_date - timedelta(days=days // 2)
    recent_end = end_date

    # Query old error count
    old_query = select(func.count(ErrorDetail.id)).join(Analysis).where(
        Analysis.user_id == user_id,
        Analysis.created_at >= old_start,
        Analysis.created_at < old_end
    )
    old_result = await session.execute(old_query)
    old_count = old_result.scalar() or 0

    # Query recent error count
    recent_query = select(func.count(ErrorDetail.id)).join(Analysis).where(
        Analysis.user_id == user_id,
        Analysis.created_at >= recent_start,
        Analysis.created_at < recent_end
    )
    recent_result = await session.execute(recent_query)
    recent_count = recent_result.scalar() or 0

    # Calculate trend
    if old_count == 0:
        comparison = "stable"
        change_percent = "0%"
    else:
        change = ((recent_count - old_count) / old_count) * 100
        change_percent = f"{change:+.0f}%"

        if change < -10:
            comparison = "improving"
        elif change > 10:
            comparison = "worsening"
        else:
            comparison = "stable"

    # Find most improved and needs attention
    # (simplified - in production, group by category)
    return HistoricalTrend(
        comparison=comparison,
        since_last_week=change_percent,
        most_improved="Grammar" if comparison == "improving" else "N/A",
        needs_attention="Spelling" if comparison == "worsening" else "N/A"
    )
```

**Step 4: Implement generate_learning_insights method**

```python
# In LLMEngine class

async def generate_learning_insights(
    self,
    lt_errors: List,
    user_id: Optional[int] = None,
    session: AsyncSession = None
) -> LearningAnalysis:
    """
    Generate learning insights from LanguageTool errors

    Uses LLM to create personalized learning recommendations
    """
    # Extract error patterns
    error_patterns = self._extract_error_patterns(lt_errors)

    # Analyze historical trends
    historical_trend = await self._analyze_historical_trends(session, user_id) if session else None

    # Build LLM prompt
    patterns_text = "\n".join([
        f"- {p.pattern_name}: {p.frequency} (severity: {p.severity})"
        for p in error_patterns
    ])

    examples_text = "\n".join([
        f"{i+1}. {p.pattern_name}\n   Examples: {', '.join([e['original'] for e in p.examples[:2]])}"
        for i, p in enumerate(error_patterns[:3])
    ])

    prompt = f"""You are an expert English teacher. Analyze these student errors and provide personalized learning recommendations.

Error Patterns:
{patterns_text}

Specific Examples:
{examples_text}

Provide your analysis in JSON format:
{{
  "ea_learning_recommendations": [
    {{
      "priority": 1,
      "topic": "Specific grammar rule name",
      "description": "Clear explanation of what the student is struggling with",
      "resources": [
        {{
          "type": "grammar_rule",
          "title": "Rule name",
          "content": "Detailed explanation..."
        }},
        {{
          "type": "practice_exercise",
          "title": "Practice name",
          "difficulty": "intermediate"
        }}
      ],
      "estimated_study_time": "30 minutes"
    }}
  ],
  "personalized_tips": [
    "Specific actionable tip 1",
    "Specific actionable tip 2"
  ]
}}

Focus on the top 3 error patterns. Be specific and practical."""

    try:
        # Call LLM
        response = await self.client.generate(prompt)

        # Parse JSON response
        import json
        llm_data = json.loads(response)

        # Convert to dataclasses
        recommendations = []
        for rec in llm_data.get('ea_learning_recommendations', [])[:3]:
            resources = [
                LearningResource(**r) for r in rec.get('resources', [])
            ]
            recommendations.append(LearningRecommendation(
                priority=rec.get('priority', 1),
                topic=rec.get('topic', ''),
                description=rec.get('description', ''),
                resources=resources,
                estimated_study_time=rec.get('estimated_study_time', '30 minutes')
            ))

        tips = llm_data.get('personalized_tips', [])

        return LearningAnalysis(
            error_patterns=error_patterns,
            ea_learning_recommendations=recommendations,
            personalized_tips=tips,
            historical_trend=historical_trend
        )

    except Exception as e:
        # Fallback: return minimal analysis without LLM
        return LearningAnalysis(
            error_patterns=error_patterns,
            ea_learning_recommendations=[],
            personalized_tips=[
                f"Focus on {error_patterns[0].pattern_name if error_patterns else 'basic grammar'}"
            ],
            historical_trend=historical_trend
        )
```

**Step 5: Run type check**

Run: `cd backend && poetry run mypy pipeline/llm_engine.py`
Expected: No critical errors

**Step 6: Commit**

```bash
git add backend/pipeline/llm_engine.py
git commit -m "feat(llm): add learning insights generation"
```

---

## Task 5: Implement optimize_with_llm in Pipeline

**Files:**
- Modify: `backend/pipeline/analysis_pipeline.py`

**Step 1: Add import for LLM and Learning types**

```python
# backend/pipeline/analysis_pipeline.py

from models.types import (
    LLMResult,
    LLMSuggestion,
    ChineseCorrection,
    LearningAnalysis
)
```

**Step 2: Implement optimize_with_llm method**

```python
# In AnalysisPipeline class

async def optimize_with_llm(
    self,
    analysis_id: str,
    user_id: Optional[int] = None,
    session: AsyncSession = None
) -> LLMResult:
    """
    Run LLM optimization on existing analysis

    Requires valid analysis_id from analyze_rules_only
    """
    from sqlalchemy import select
    from models.analysis import Analysis

    # Load existing analysis
    query = select(Analysis).where(Analysis.id == int(analysis_id))
    result = await session.execute(query)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise ValueError(f"Analysis {analysis_id} not found")

    if analysis.status != 'rule_only':
        raise ValueError(f"Analysis {analysis_id} has already been optimized")

    # Check rate limits (implement based on your rate limiting logic)
    # await self.rate_limiter.check_llm_quota(user_id)

    start_time = time.time()

    # Stage 3: LLM Optimization
    llm_result = await self.llm_engine.optimize(
        original_text=analysis.original_text,
        rule_corrections=None,  # Already applied in corrected_text
        mode=CorrectionMode(analysis.mode)
    )

    # Generate learning insights
    from models.error_detail import ErrorDetail

    # Load error details for learning analysis
    error_query = select(ErrorDetail).where(ErrorDetail.analysis_id == analysis.id)
    error_result = await session.execute(error_query)
    ea_error_details = error_result.scalars().all()

    # Convert to LTError format
    lt_errors = [
        LTError(
            rule_id=e.rule_id,
            category=e.category,
            severity=e.severity,
            position_start=e.position_start,
            position_end=e.position_end,
            original_text=e.original_text,
            replacements=[e.correction] if e.correction else [],
            message=e.message,
            context=e.context
        )
        for e in ea_error_details
    ]

    learning_analysis = await self.llm_engine.generate_learning_insights(
        lt_errors=lt_errors,
        user_id=user_id,
        session=session
    )

    # Convert suggestions
    suggestions = [
        LLMSuggestion(
            type='naturalness',
            sentence_index=0,
            original=analysis.original_text,
            suggestion=llm_result.optimized_text,
            explanation="AI优化建议",
            confidence=0.9
        )
    ]

    # Update analysis
    analysis.status = 'completed'
    analysis.llm_tokens_used = llm_result.token_count
    analysis.llm_cost_usd = llm_result.token_count * 0.0001  # Adjust cost calculation
    analysis.processing_time_ms += int((time.time() - start_time) * 1000)

    # Save learning recommendations
    from models.learning_recommendation import LearningRecommendation as LR

    for rec in learning_analysis.ea_learning_recommendations:
        lr = LR(
            user_id=user_id,
            analysis_id=analysis.id,
            pattern_name=rec.topic,
            frequency=float(rec.priority) * 10.0,  # Simplified
            severity='high' if rec.priority == 1 else 'medium',
            recommendation=rec.description,
            resources=[r.__dict__ for r in rec.resources],
            priority=rec.priority,
            estimated_study_time=rec.estimated_study_time
        )
        session.add(lr)

    await session.commit()

    return LLMResult(
        optimized_text=llm_result.optimized_text,
        suggestions=suggestions,
        chinese_corrections=[],  # Extract from llm_result if available
        learning_analysis=learning_analysis,
        token_usage=llm_result.token_count
    )
```

**Step 3: Run type check**

Run: `cd backend && poetry run mypy pipeline/analysis_pipeline.py`
Expected: No critical errors

**Step 4: Commit**

```bash
git add backend/pipeline/analysis_pipeline.py
git commit -m "feat(pipeline): add optimize_with_llm method"
```

---

## Task 6: Add New API Endpoints

**Files:**
- Modify: `backend/api/v1/analysis.py`

**Step 1: Add new request/response models**

```python
# backend/api/v1/analysis.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RulesOnlyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    mode: CorrectionMode = Field(default='accuracy')
    language: str = Field(default='en-US')

class OptimizeLLMRequest(BaseModel):
    analysis_id: str = Field(...)

class LTErrorResponse(BaseModel):
    rule_id: str
    category: str
    severity: str
    position: Dict[str, int]
    original_text: str
    replacements: List[str]
    message: str
    context: str

class RuleBasedStatisticsResponse(BaseModel):
    total_errors: int
    by_category: Dict[str, int]

class RuleBasedResultResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

class LLMResultResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
```

**Step 2: Add /analyze/rules-only endpoint**

```python
# In backend/api/v1/analysis.py, after existing endpoints

@router.post("/analyze/rules-only", response_model=RuleBasedResultResponse)
async def analyze_rules_only(
    request: RulesOnlyRequest,
    current_user: Optional[User] = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_db)
):
    """
    Fast analysis using LanguageTool only

    Returns rule-based corrections + token estimate for optional LLM optimization
    """
    try:
        # Get user_id (anonymous users use None)
        user_id = current_user.id if current_user else None

        # Run pipeline
        result = await pipeline.analyze_rules_only(
            text=request.text,
            mode=request.mode,
            user_id=user_id,
            session=session
        )

        # Convert to response format
        return RuleBasedResultResponse(
            success=True,
            data={
                "analysis_id": result.analysis_id,
                "errors": [
                    {
                        "rule_id": e.rule_id,
                        "category": e.category,
                        "severity": e.severity,
                        "position": {
                            "start": e.position_start,
                            "end": e.position_end
                        },
                        "original_text": e.original_text,
                        "replacements": e.replacements,
                        "message": e.message,
                        "context": e.context
                    }
                    for e in result.errors
                ],
                "corrected_text": result.corrected_text,
                "statistics": {
                    "total_errors": result.statistics.total_errors,
                    "by_category": result.statistics.by_category
                },
                "processing_time_ms": result.processing_time_ms,
                "estimated_llm_tokens": result.estimated_llm_tokens
            }
        )

    except Exception as e:
        logger.error(f"Rules-only analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 3: Add /analyze/optimize-llm endpoint**

```python
# In backend/api/v1/analysis.py

@router.post("/analyze/optimize-llm", response_model=LLMResultResponse)
async def optimize_with_llm(
    request: OptimizeLLMRequest,
    current_user: Optional[User] = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_db)
):
    """
    Run LLM optimization on existing analysis

    Requires valid analysis_id from /analyze/rules-only
    Checks user credits/rate limits before running
    """
    try:
        user_id = current_user.id if current_user else None

        # Check rate limits for anonymous users
        if not current_user:
            # Implement anonymous rate limiting
            pass

        # Run pipeline
        result = await pipeline.optimize_with_llm(
            analysis_id=request.analysis_id,
            user_id=user_id,
            session=session
        )

        # Convert to response format
        return LLMResultResponse(
            success=True,
            data={
                "optimized_text": result.optimized_text,
                "suggestions": [
                    {
                        "type": s.type,
                        "sentence_index": s.sentence_index,
                        "original": s.original,
                        "suggestion": s.suggestion,
                        "explanation": s.explanation,
                        "confidence": s.confidence
                    }
                    for s in result.suggestions
                ],
                "chinese_corrections": [
                    {
                        "original": c.original,
                        "corrected": c.corrected
                    }
                    for c in result.chinese_corrections
                ],
                "learning_analysis": {
                    "error_patterns": [
                        {
                            "pattern_name": p.pattern_name,
                            "frequency": p.frequency,
                            "examples": p.examples,
                            "severity": p.severity
                        }
                        for p in result.learning_analysis.error_patterns
                    ],
                    "ea_learning_recommendations": [
                        {
                            "priority": r.priority,
                            "topic": r.topic,
                            "description": r.description,
                            "resources": [
                                {
                                    "type": res.type,
                                    "title": res.title,
                                    "content": res.content,
                                    "difficulty": res.difficulty
                                }
                                for res in r.resources
                            ],
                            "estimated_study_time": r.estimated_study_time
                        }
                        for r in result.learning_analysis.ea_learning_recommendations
                    ],
                    "personalized_tips": result.learning_analysis.personalized_tips,
                    "historical_trend": (
                        {
                            "comparison": result.learning_analysis.historical_trend.comparison,
                            "since_last_week": result.learning_analysis.historical_trend.since_last_week,
                            "most_improved": result.learning_analysis.historical_trend.most_improved,
                            "needs_attention": result.learning_analysis.historical_trend.needs_attention
                        }
                        if result.learning_analysis.historical_trend
                        else None
                    )
                },
                "token_usage": result.token_usage
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"LLM optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 4: Run type check**

Run: `cd backend && poetry run mypy api/v1/analysis.py`
Expected: No critical errors

**Step 5: Commit**

```bash
git add backend/api/v1/analysis.py
git commit -m "feat(api): add /analyze/rules-only and /analyze/optimize-llm endpoints"
```

---

## Task 7: Write Tests for Pipeline Methods

**Files:**
- Create: `backend/tests/test_pipeline_rules_only.py`
- Create: `backend/tests/test_pipeline_llm_optimize.py`

**Step 1: Write test for analyze_rules_only**

```python
# backend/tests/test_pipeline_rules_only.py

import pytest
from pipeline.analysis_pipeline import AnalysisPipeline
from models.types import CorrectionMode

@pytest.mark.asyncio
async def test_analyze_rules_only_simple_text(db_session):
    """Test rules-only analysis with simple text"""
    pipeline = AnalysisPipeline()

    text = "She dont like pizza"
    mode = CorrectionMode.ACCURACY

    result = await pipeline.analyze_rules_only(
        text=text,
        mode=mode,
        user_id=None,
        session=db_session
    )

    # Verify result structure
    assert result.analysis_id is not None
    assert len(result.errors) > 0
    assert result.corrected_text == "She doesn't like pizza"
    assert result.statistics.total_errors > 0
    assert result.processing_time_ms > 0
    assert result.estimated_llm_tokens > 0

    # Verify error details
    error = result.errors[0]
    assert error.category == "GRAMMAR"
    assert error.severity == "ERROR"
    assert "dont" in error.original_text.lower()

@pytest.mark.asyncio
async def test_analyze_rules_only_with_user(db_session, test_user):
    """Test rules-only analysis with authenticated user"""
    pipeline = AnalysisPipeline()

    text = "He go to school yesterday"
    mode = CorrectionMode.ACCURACY

    result = await pipeline.analyze_rules_only(
        text=text,
        mode=mode,
        user_id=test_user.id,
        session=db_session
    )

    # Verify analysis is saved to database
    from sqlalchemy import select
    from models.analysis import Analysis

    query = select(Analysis).where(Analysis.id == int(result.analysis_id))
    db_result = await db_session.execute(query)
    analysis = db_result.scalar_one()

    assert analysis.user_id == test_user.id
    assert analysis.status == 'rule_only'
    assert analysis.original_text == text

@pytest.mark.asyncio
async def test_analyze_rules_only_empty_text(db_session):
    """Test rules-only analysis with empty text"""
    pipeline = AnalysisPipeline()

    with pytest.raises(Exception):
        await pipeline.analyze_rules_only(
            text="",
            mode=CorrectionMode.ACCURACY,
            user_id=None,
            session=db_session
        )
```

**Step 2: Write test for optimize_with_llm**

```python
# backend/tests/test_pipeline_llm_optimize.py

import pytest
from pipeline.analysis_pipeline import AnalysisPipeline
from models.types import CorrectionMode

@pytest.mark.asyncio
async def test_optimize_with_llm_valid_analysis(db_session):
    """Test LLM optimization with valid analysis_id"""
    pipeline = AnalysisPipeline()

    # First create a rule-only analysis
    text = "She dont like pizza"
    rule_result = await pipeline.analyze_rules_only(
        text=text,
        mode=CorrectionMode.ACCURACY,
        user_id=None,
        session=db_session
    )

    # Then optimize with LLM
    llm_result = await pipeline.optimize_with_llm(
        analysis_id=rule_result.analysis_id,
        user_id=None,
        session=db_session
    )

    # Verify result
    assert llm_result.optimized_text is not None
    assert len(llm_result.suggestions) > 0
    assert llm_result.learning_analysis is not None
    assert llm_result.token_usage > 0

    # Verify learning analysis
    assert len(llm_result.learning_analysis.error_patterns) > 0
    assert len(llm_result.learning_analysis.personalized_tips) > 0

@pytest.mark.asyncio
async def test_optimize_with_llm_invalid_id(db_session):
    """Test LLM optimization with invalid analysis_id"""
    pipeline = AnalysisPipeline()

    with pytest.raises(ValueError, match="not found"):
        await pipeline.optimize_with_llm(
            analysis_id="999999",
            user_id=None,
            session=db_session
        )

@pytest.mark.asyncio
async def test_optimize_with_llm_already_optimized(db_session):
    """Test LLM optimization on already optimized analysis"""
    pipeline = AnalysisPipeline()

    # Create and optimize
    text = "Test text"
    rule_result = await pipeline.analyze_rules_only(
        text=text,
        mode=CorrectionMode.ACCURACY,
        user_id=None,
        session=db_session
    )

    await pipeline.optimize_with_llm(
        analysis_id=rule_result.analysis_id,
        user_id=None,
        session=db_session
    )

    # Try to optimize again
    with pytest.raises(ValueError, match="already been optimized"):
        await pipeline.optimize_with_llm(
            analysis_id=rule_result.analysis_id,
            user_id=None,
            session=db_session
        )
```

**Step 3: Run tests**

Run: `cd backend && poetry run pytest tests/test_pipeline_rules_only.py -v`
Expected: Some tests may fail if database/setup not ready

Run: `cd backend && poetry run pytest tests/test_pipeline_llm_optimize.py -v`
Expected: Same as above

**Step 4: Commit**

```bash
git add backend/tests/
git commit -m "test: add tests for split analysis pipeline methods"
```

---

## Task 8: Write Tests for API Endpoints

**Files:**
- Create: `backend/tests/test_api_split_analysis.py`

**Step 1: Write API tests**

```python
# backend/tests/test_api_split_analysis.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_analyze_rules_only_endpoint(db_session):
    """Test /analyze/rules-only endpoint"""
    response = client.post(
        "/api/v1/analyze/rules-only",
        json={
            "text": "She dont like pizza",
            "mode": "accuracy",
            "language": "en-US"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "analysis_id" in data["data"]
    assert "errors" in data["data"]
    assert "corrected_text" in data["data"]
    assert "estimated_llm_tokens" in data["data"]

    # Verify error structure
    errors = data["data"]["errors"]
    assert len(errors) > 0
    assert "rule_id" in errors[0]
    assert "category" in errors[0]

@pytest.mark.asyncio
async def test_optimize_with_llm_endpoint(db_session):
    """Test /analyze/optimize-llm endpoint"""
    # First create an analysis
    rule_response = client.post(
        "/api/v1/analyze/rules-only",
        json={
            "text": "She dont like pizza",
            "mode": "accuracy"
        }
    )

    analysis_id = rule_response.json()["data"]["analysis_id"]

    # Then optimize
    llm_response = client.post(
        "/api/v1/analyze/optimize-llm",
        json={"analysis_id": analysis_id}
    )

    assert llm_response.status_code == 200
    data = llm_response.json()

    assert data["success"] is True
    assert "optimized_text" in data["data"]
    assert "learning_analysis" in data["data"]
    assert "token_usage" in data["data"]

    # Verify learning analysis
    learning = data["data"]["learning_analysis"]
    assert "error_patterns" in learning
    assert "ea_learning_recommendations" in learning
    assert "personalized_tips" in learning

@pytest.mark.asyncio
async def test_analyze_rules_only_validation(db_session):
    """Test validation on /analyze/rules-only"""
    # Empty text
    response = client.post(
        "/api/v1/analyze/rules-only",
        json={"text": "", "mode": "accuracy"}
    )

    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_optimize_with_llm_not_found(db_session):
    """Test /analyze/optimize-llm with non-existent analysis"""
    response = client.post(
        "/api/v1/analyze/optimize-llm",
        json={"analysis_id": "999999"}
    )

    assert response.status_code == 404
```

**Step 2: Run tests**

Run: `cd backend && poetry run pytest tests/test_api_split_analysis.py -v`
Expected: Tests may fail if endpoints not implemented

**Step 3: Commit**

```bash
git add backend/tests/test_api_split_analysis.py
git commit -m "test: add API tests for split analysis endpoints"
```

---

## Task 9: Database Migration

**Files:**
- Modify: `backend/alembic/versions/<newest_migration>.py` (created in Task 2)

**Step 1: Review migration**

Open the migration file created in Task 2 and verify:
- ALTER TABLE ea_analyses ADD COLUMN status
- ALTER TABLE ea_analyses ADD COLUMN llm_tokens_used
- ALTER TABLE ea_analyses ADD COLUMN llm_cost_usd
- CREATE TABLE ea_error_details
- CREATE TABLE ea_learning_recommendations
- CREATE TABLE ea_user_error_trends

**Step 2: Run migration**

Run: `cd backend && poetry run alembic upgrade head`
Expected: "Running upgrade..." message

**Step 3: Verify database schema**

Run: `psql -U postgres -d english_assistant -c "\d analyses"`
Expected: Should show new columns (status, llm_tokens_used, llm_cost_usd)

Run: `psql -U postgres -d english_assistant -c "\d ea_error_details"`
Expected: Should show new table

**Step 4: Commit migration**

```bash
git add backend/alembic/versions/
git commit -m "migration: apply split analysis database changes"
```

---

## Task 10: Integration Test

**Files:**
- Create: `backend/tests/test_integration_split_analysis.py`

**Step 1: Write end-to-end integration test**

```python
# backend/tests/test_integration_split_analysis.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_split_analysis_workflow(db_session):
    """Test complete workflow: rules-only → optimize"""
    # Step 1: User submits text
    text = "She dont like pizza and he go to school"

    rule_response = client.post(
        "/api/v1/analyze/rules-only",
        json={"text": text, "mode": "accuracy"}
    )

    assert rule_response.status_code == 200
    rule_data = rule_response.json()
    analysis_id = rule_data["data"]["analysis_id"]

    # Verify LanguageTool results
    assert rule_data["data"]["statistics"]["total_errors"] >= 2

    # Step 2: User triggers LLM optimization
    llm_response = client.post(
        "/api/v1/analyze/optimize-llm",
        json={"analysis_id": analysis_id}
    )

    assert llm_response.status_code == 200
    llm_data = llm_response.json()

    # Verify LLM results
    assert llm_data["data"]["optimized_text"] is not None
    assert llm_data["data"]["token_usage"] > 0

    # Verify learning analysis
    learning = llm_data["data"]["learning_analysis"]
    assert len(learning["error_patterns"]) > 0
    assert len(learning["personalized_tips"]) > 0

    # Step 3: Verify database state
    from sqlalchemy import select
    from models.analysis import Analysis

    query = select(Analysis).where(Analysis.id == int(analysis_id))
    result = await db_session.execute(query)
    analysis = result.scalar_one()

    assert analysis.status == 'completed'
    assert analysis.llm_tokens_used > 0

@pytest.mark.asyncio
@pytest.mark.integration
async def test_rules_only_without_optimization(db_session):
    """Test using rules-only without LLM (cost-saving scenario)"""
    text = "Simple test text with no errors"

    rule_response = client.post(
        "/api/v1/analyze/rules-only",
        json={"text": text, "mode": "accuracy"}
    )

    assert rule_response.status_code == 200
    rule_data = rule_response.json()
    analysis_id = rule_data["data"]["analysis_id"]

    # User decides NOT to optimize (saves tokens)
    # Verify analysis remains in 'rule_only' state
    from sqlalchemy import select
    from models.analysis import Analysis

    query = select(Analysis).where(Analysis.id == int(analysis_id))
    result = await db_session.execute(query)
    analysis = result.scalar_one()

    assert analysis.status == 'rule_only'
    assert analysis.llm_tokens_used == 0
```

**Step 2: Run integration test**

Run: `cd backend && poetry run pytest tests/test_integration_split_analysis.py -v -m integration`
Expected: All tests pass if backend is running

**Step 3: Commit**

```bash
git add backend/tests/test_integration_split_analysis.py
git commit -m "test: add integration tests for split analysis workflow"
```

---

## Task 11: Documentation

**Files:**
- Update: `docs/04-technical-design/architecture.md`
- Update: `CLAUDE.md`
- Create: `docs/api-split-analysis.md`

**Step 1: Update architecture documentation**

Add to `docs/04-technical-design/architecture.md`:

```markdown
### Split Analysis Architecture (v1.1)

**Sequential Analysis Flow:**

The system now supports sequential analysis with cost optimization:

1. **Phase 1: Rule-Based Analysis** (Fast, Free)
   - Endpoint: `POST /api/v1/analyze/rules-only`
   - Processing: 2-4 seconds
   - Returns: LanguageTool errors + corrected text
   - Token cost: 0

2. **Phase 2: LLM Optimization** (Optional, Costly)
   - Endpoint: `POST /api/v1/analyze/optimize-llm`
   - Triggered by: User choice
   - Processing: 3-5 seconds
   - Returns: AI suggestions + learning insights
   - Token cost: ~15-50 tokens

**Database Schema Updates:**

- `analyses.status`: 'rule_only' → 'completed'
- `analyses.llm_tokens_used`: Token count
- `ea_error_details`: Full LT error details
- `ea_learning_recommendations`: Personalized learning suggestions
```

**Step 2: Update CLAUDE.md**

Add to `CLAUDE.md` under "Latest Work":

```markdown
- ✅ **Split analysis feature** - Sequential LT + optional LLM
- ✅ **Learning recommendations** - Personalized learning insights
- ✅ **Cost optimization** - User-controlled LLM usage
```

**Step 3: Create API documentation**

Create `docs/api-split-analysis.md`:

```markdown
# Split Analysis API Documentation

## POST /api/v1/analyze/rules-only

Fast analysis using LanguageTool only.

**Request:**
```json
{
  "text": "She dont like pizza",
  "mode": "accuracy",
  "language": "en-US"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "123",
    "errors": [...],
    "corrected_text": "She doesn't like pizza",
    "statistics": {...},
    "estimated_llm_tokens": 15
  }
}
```

## POST /api/v1/analyze/optimize-llm

Run LLM optimization on existing analysis.

**Request:**
```json
{
  "analysis_id": "123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "optimized_text": "...",
    "suggestions": [...],
    "learning_analysis": {...},
    "token_usage": 25
  }
}
```
```

**Step 4: Commit**

```bash
git add docs/
git commit -m "docs: add split analysis architecture and API documentation"
```

---

## Task 12: Final Integration and Cleanup

**Files:**
- Various

**Step 1: Run full test suite**

Run: `cd backend && poetry run pytest -v`
Expected: All tests pass

**Step 2: Check for TODO comments**

Run: `grep -r "TODO" backend/ --include="*.py"`
Expected: No critical TODOs remaining

**Step 3: Run type checking**

Run: `cd backend && poetry run mypy .`
Expected: No critical errors

**Step 4: Format code**

Run: `cd backend && poetry run black .`
Run: `cd backend && poetry run ruff check . --fix`

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete split analysis implementation"
```

---

## Testing Checklist

Before considering this feature complete:

- [ ] All unit tests pass (`pytest tests/`)
- [ ] Integration tests pass (`pytest -m integration`)
- [ ] API endpoints return correct responses
- [ ] Database migration applied successfully
- [ ] LanguageTool errors saved correctly
- [ ] LLM optimization works end-to-end
- [ ] Learning recommendations generated
- [ ] Token estimation accurate
- [ ] Error handling works (invalid ID, already optimized, etc.)
- [ ] Frontend can call new endpoints
- [ ] Type checking passes (`mypy`)
- [ ] Code formatted (`black`, `ruff`)

---

## Rollback Plan

If critical issues arise:

1. **Frontend**: Revert to old API calls
   - Change `analyzeWithRules()` back to `analyzeText()`
   - Use old 3-panel layout

2. **Backend**: Feature-flag the endpoints
   - Add `ENABLE_SPLIT_ANALYSIS=False` to config
   - Return 503 for new endpoints if disabled

3. **Database**: Migration is reversible
   - `alembic downgrade -1` to remove new tables
   - Old columns remain untouched

---

## Success Metrics

- **Performance**: Rules-only < 5 seconds, LLM optimize < 10 seconds
- **Cost**: Average LLM usage < 30% (users optimize selectively)
- **Quality**: Learning recommendations helpful (user feedback > 4/5)
- **Reliability**: < 1% failure rate for both endpoints
