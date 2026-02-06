"""
Text analysis service.

Handles text analysis, correction, and history management.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from models import Analysis, AnalysisCache, ErrorDetail, User
from pipeline import AnalysisPipeline
from schemas.analysis import AnalyzeRequest, AnalyzeResponse, ErrorDetailResponse
from schemas.split_analysis import (
    RulesOnlyRequest, RulesOnlyResponse, RulesOnlyData,
    OptimizeLLMRequest, OptimizeLLMResponse, OptimizeLLMData
)
from fastapi import HTTPException
import time
import uuid
from pipeline.llm_engine import LLMError

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Text analysis service.

    Coordinates the analysis pipeline and manages analysis records.

    Attributes:
        pipeline: Analysis pipeline instance
        cache_ttl_hours: Cache time-to-live in hours
    """

    def __init__(self, pipeline: AnalysisPipeline | None = None, cache_ttl_hours: int = 24):
        """
        Initialize the analysis service.

        Args:
            pipeline: Analysis pipeline instance
            cache_ttl_hours: Cache expiration time in hours
        """
        self.pipeline = pipeline or AnalysisPipeline()
        self.cache_ttl_hours = cache_ttl_hours

    async def analyze(
        self,
        request: AnalyzeRequest,
        user: Optional[User],
        db: Session
    ) -> AnalyzeResponse:
        """
        Analyze and correct text.

        Args:
            request: Analysis request
            user: User object (None for anonymous)
            db: Database session

        Returns:
            AnalyzeResponse with corrected text and errors

        Example:
            ```python
            service = AnalysisService()
            request = AnalyzeRequest(text="She don't like it.", mode="accuracy")
            response = await service.analyze(request, user, db)
            assert "doesn't" in response.corrected_text.lower()
            ```

        Raises:
            AnalysisServiceError: If analysis fails
        """
        # TODO: Implement analysis logic
        # 1. Check cache for existing results
        # 2. Run analysis pipeline
        # 3. Save analysis record
        # 4. Save error details
        # 5. Update API credit usage
        # 6. Return response

        # Check cache
        cache_key = self._generate_cache_key(request.text, request.mode)
        cached_result = self._get_from_cache(cache_key, db)

        if cached_result:
            return AnalyzeResponse(**cached_result)

        # Run pipeline
        user_id = str(user.id) if user else None
        pipeline_result = await self.pipeline.analyze(
            request.text,
            request.mode,
            user_id
        )

        # Log stage times for monitoring
        logger.info(f"[ANALYSIS] Stage times: {pipeline_result.stage_times}")

        # Create analysis record
        analysis = Analysis(
            user_id=user_id,
            original_text=request.text,
            corrected_text=pipeline_result.corrected_text,
            mode=request.mode,
            text_type="dialogue" if pipeline_result.preprocessed.is_dialogue else "unknown",
            statistics=pipeline_result.merged_result.statistics,
            processing_time_ms=pipeline_result.processing_time_ms,
            is_cached=False,
            token_usage=pipeline_result.llm_result.token_usage
        )
        db.add(analysis)
        db.flush()

        # Save error details
        error_responses = []
        for error_data in pipeline_result.merged_result.errors:
            error = ErrorDetail(
                analysis_id=analysis.id,
                error_type=error_data.get('error_type', 'grammar'),
                error_subtype=error_data.get('error_subtype'),
                original_span=error_data.get('original_span', ''),
                corrected_span=error_data.get('corrected_span', ''),
                start_index=error_data.get('start_index', 0),
                end_index=error_data.get('end_index', 0),
                explanation=error_data.get('explanation', ''),
                rule_description=error_data.get('rule_description', ''),
                severity=error_data.get('severity', 'medium')
            )
            db.add(error)

            error_responses.append(
                ErrorDetailResponse(
                    error_type=error.error_type,
                    error_subtype=error.error_subtype,
                    original_span=error.original_span,
                    corrected_span=error.corrected_span,
                    start_index=error.start_index,
                    end_index=error.end_index,
                    explanation=error.explanation,
                    rule_description=error.rule_description,
                    severity=error.severity
                )
            )

        db.commit()

        # Build response
        response = AnalyzeResponse(
            analysis_id=str(analysis.id),
            original_text=pipeline_result.original_text,
            corrected_text=pipeline_result.corrected_text,
            mode=request.mode,
            errors=error_responses,
            statistics=pipeline_result.merged_result.statistics,
            processing_time_ms=pipeline_result.processing_time_ms,
            stage_times=pipeline_result.stage_times,
            token_usage=pipeline_result.llm_result.token_usage,
            created_at=analysis.created_at
        )

        # Save to cache
        self._save_to_cache(cache_key, response.dict(), db)

        return response

    async def analyze_rules_only(
        self,
        request: RulesOnlyRequest,
        user: Optional[User],
        db: Session
    ) -> RulesOnlyResponse:
        """
        Phase 1: Rules-only analysis.
        """
        start_time = time.time()
        stage_times = {}

        # Stage 1: Preprocessing
        stage_start = time.time()
        preprocessed = self.pipeline.preprocessor.preprocess(request.text)
        stage_times["preprocessing"] = int((time.time() - stage_start) * 1000)

        # Stage 2: Rule-based checking
        stage_start = time.time()
        rule_errors = self.pipeline.rule_engine.check(request.text)
        stage_times["rule_engine"] = int((time.time() - stage_start) * 1000)

        # Apply corrections
        corrected_text = self.pipeline._apply_rule_corrections(request.text, rule_errors)
        
        # Estimate LLM tokens (Phase 2 preview)
        # Using simple estimation: 1.3 tokens per word
        word_count = len(request.text.split())
        estimated_tokens = int(word_count * 1.3 * 2)  # Input + Output
        
        total_time = int((time.time() - start_time) * 1000)
        
        # Create Analysis record
        user_id = user.id if user else None
        
        statistics = {
            "total_errors": len(rule_errors),
            "error_types": {},  # TODO: Aggregate types
            "estimated_llm_tokens": estimated_tokens
        }
        
        # Count error types
        for error in rule_errors:
            etype = error.metadata.get('category', 'grammar')
            statistics["error_types"][etype] = statistics["error_types"].get(etype, 0) + 1

        analysis = Analysis(
            user_id=user_id,
            original_text=request.text,
            corrected_text=corrected_text,
            mode=request.mode,
            text_type="dialogue" if preprocessed.is_dialogue else "unknown",
            statistics=statistics,
            processing_time_ms=total_time,
            is_cached=False,
            token_usage={"total_tokens": 0, "estimated_cost": 0.0},
            status="rule_only"
        )
        db.add(analysis)
        db.flush()

        # Save error details
        error_responses = []
        for error in rule_errors:
            ed = ErrorDetail(
                analysis_id=analysis.id,
                error_type=error.error_type.value, 
                error_subtype=error.error_subtype or "general",
                original_span=error.original_span,
                corrected_span=error.corrected_span,
                start_index=error.start_index,
                end_index=error.end_index,
                explanation=error.explanation,
                rule_description=error.rule_description,
                severity=error.severity.value,
                
                # New fields
                rule_id=error.metadata.get("rule_id"),
                category=error.metadata.get("category", "grammar"),
                message=error.explanation,
                context=error.metadata.get("context")
            )
            # Map specific types if needed
            if ed.error_type not in ['grammar', 'tense', 'word_choice', 'mixed_language', 'spelling', 'punctuation', 'style']:
                 ed.error_type = 'grammar' # Fallback
            
            db.add(ed)
            
            error_responses.append(
                ErrorDetailResponse(
                    error_type=ed.error_type,
                    error_subtype=ed.error_subtype,
                    original_span=ed.original_span,
                    corrected_span=ed.corrected_span,
                    start_index=ed.start_index,
                    end_index=ed.end_index,
                    explanation=ed.explanation,
                    rule_description=ed.rule_description,
                    severity=ed.severity
                )
            )
            
        db.commit()

        data = RulesOnlyData(
            analysis_id=str(analysis.id),
            original_text=request.text,
            corrected_text=corrected_text,
            mode=request.mode,
            status="rule_only",
            errors=error_responses,
            statistics=statistics,
            processing_time_ms=total_time,
            stage_times=stage_times,
            created_at=analysis.created_at
        )
        
        return RulesOnlyResponse(data=data)

    async def optimize_with_llm(
        self,
        request: OptimizeLLMRequest,
        user: User,
        db: Session
    ) -> OptimizeLLMResponse:
        """
        Phase 2: LLM optimization.
        """
        # 1. Ownership & Existence
        try:
            analysis_uuid = uuid.UUID(request.analysis_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid analysis ID format")

        analysis = db.query(Analysis).filter(Analysis.id == analysis_uuid).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to optimize this analysis")

        # 2. State Machine & Idempotency
        if analysis.status == "llm_running":
             raise HTTPException(status_code=409, detail="Optimization already in progress")
        if analysis.status == "llm_completed":
             raise HTTPException(status_code=409, detail="Optimization already completed")
        
        # Lock status
        analysis.status = "llm_running"
        db.commit()

        start_time = time.time()
        stage_times = {}
        
        try:
            # 3. Call LLM
            stage_start = time.time()
            # Use original text for LLM as per plan
            llm_result = await self.pipeline.llm_engine.optimize(
                analysis.original_text, 
                analysis.mode
            )
            stage_times["llm"] = int((time.time() - stage_start) * 1000)

            # 4. Update Analysis
            analysis.corrected_text = llm_result.optimized_text
            analysis.token_usage = llm_result.token_usage
            
            # Update statistics with learning analysis
            new_stats = dict(analysis.statistics)
            if "learning_analysis" in llm_result.metadata:
                new_stats["learning_analysis"] = llm_result.metadata["learning_analysis"]
            
            # Add stage times
            if "stage_times" not in new_stats:
                new_stats["stage_times"] = {}
            new_stats["stage_times"].update(stage_times)
            
            analysis.statistics = new_stats
            analysis.status = "llm_completed"
            analysis.processing_time_ms += int((time.time() - start_time) * 1000)
            
            db.commit()

            data = OptimizeLLMData(
                analysis_id=str(analysis.id),
                original_text=analysis.original_text,
                corrected_text=analysis.corrected_text,
                mode=analysis.mode,
                status="llm_completed",
                token_usage=analysis.token_usage,
                statistics=analysis.statistics,
                processing_time_ms=analysis.processing_time_ms,
                stage_times=stage_times,
                created_at=analysis.created_at
            )
            
            return OptimizeLLMResponse(data=data)

        except Exception as e:
            # Failed
            analysis.status = "failed"
            # Log error in statistics
            new_stats = dict(analysis.statistics)
            new_stats["llm_error"] = str(e)
            analysis.statistics = new_stats
            db.commit()
            
            # If it's an LLMError, we might want to return 500 or 422
            # Returning 500 for now as per plan
            logger.error(f"LLM optimization failed: {e}")
            raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

    def get_history(
        self,
        user: User,
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> dict[str, Any]:
        """
        Get user's analysis history.

        Args:
            user: User object
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Dictionary containing items, total count, page, and page_size
        """
        query = (
            db.query(Analysis)
            .filter(Analysis.user_id == user.id)
            .filter(Analysis.is_deleted == False)
        )

        total = query.count()

        analyses = (
            query
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        items = [
            {
                'id': str(analysis.id),
                'original_text': analysis.original_text[:100] + '...' if len(analysis.original_text) > 100 else analysis.original_text,
                'corrected_text': analysis.corrected_text[:100] + '...' if len(analysis.corrected_text) > 100 else analysis.corrected_text,
                'mode': analysis.mode,
                'created_at': analysis.created_at,
                'error_count': len(analysis.statistics.get('error_types', {})) if analysis.statistics else 0
            }
            for analysis in analyses
        ]

        return {
            "items": items,
            "total": total,
            "page": (skip // limit) + 1,
            "page_size": limit
        }

    def get_analysis(
        self,
        analysis_id: str,
        user: User,
        db: Session
    ) -> dict[str, Any] | None:
        """
        Get specific analysis details.

        Args:
            analysis_id: Analysis ID
            user: User object
            db: Database session

        Returns:
            Analysis details or None
        """
        # TODO: Implement analysis retrieval
        analysis = (
            db.query(Analysis)
            .filter(Analysis.id == analysis_id)
            .filter(Analysis.user_id == user.id)
            .filter(Analysis.is_deleted == False)
            .first()
        )

        if not analysis:
            return None

        return {
            'id': str(analysis.id),
            'original_text': analysis.original_text,
            'corrected_text': analysis.corrected_text,
            'mode': analysis.mode,
            'statistics': analysis.statistics,
            'processing_time_ms': analysis.processing_time_ms,
            'created_at': analysis.created_at
        }

    def delete_analysis(self, analysis_id: str, user: User, db: Session) -> bool:
        """
        Soft delete an analysis.

        Args:
            analysis_id: Analysis ID
            user: User object
            db: Database session

        Returns:
            True if deleted, False otherwise
        """
        # TODO: Implement soft delete
        analysis = (
            db.query(Analysis)
            .filter(Analysis.id == analysis_id)
            .filter(Analysis.user_id == user.id)
            .first()
        )

        if not analysis:
            return False

        analysis.soft_delete()
        db.commit()

        return True

    def _generate_cache_key(self, text: str, mode: str) -> str:
        """
        Generate cache key for analysis result.

        Args:
            text: Input text
            mode: Correction mode

        Returns:
            Cache key (SHA-256 hash)
        """
        # TODO: Implement cache key generation
        import hashlib
        content = f"{text}:{mode}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_from_cache(
        self,
        cache_key: str,
        db: Session
    ) -> dict[str, Any] | None:
        """
        Get analysis result from cache.

        Args:
            cache_key: Cache key
            db: Database session

        Returns:
            Cached result or None
        """
        # TODO: Implement cache retrieval
        cache_entry = (
            db.query(AnalysisCache)
            .filter(AnalysisCache.content_hash == cache_key)
            .first()
        )

        if cache_entry and cache_entry.is_valid:
            return cache_entry.cached_result

        return None

    def _save_to_cache(
        self,
        cache_key: str,
        result: dict[str, Any],
        db: Session
    ) -> None:
        """
        Save analysis result to cache.

        Args:
            cache_key: Cache key
            result: Result to cache
            db: Database session
        """
        import json
        from datetime import timedelta

        # Convert datetime objects to ISO strings for JSON serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        # Serialize result to JSON with datetime handling
        json_result = json.loads(json.dumps(result, default=serialize_datetime))

        expires_at = datetime.utcnow() + timedelta(hours=self.cache_ttl_hours)

        cache_entry = AnalysisCache(
            content_hash=cache_key,
            cached_result=json_result,
            expires_at=expires_at
        )
        db.merge(cache_entry)
        db.commit()


class AnalysisServiceError(Exception):
    """Exception raised for analysis service errors."""

    pass
