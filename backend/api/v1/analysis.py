"""
Analysis API routes.

Handles text analysis and correction endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from models import get_db, User
from schemas.analysis import AnalyzeRequest, AnalyzeResponse
from services.analysis_service import AnalysisService, AnalysisServiceError
from services.rate_limit_service import RateLimitService, QuotaExceededError
from core.security import get_optional_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazy load services to avoid import-time issues with zhipuai on Python 3.14
def get_analysis_service() -> AnalysisService:
    """Get or create the analysis service instance."""
    return AnalysisService()

def get_rate_limit_service() -> RateLimitService:
    """Get or create the rate limit service instance."""
    return RateLimitService()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    http_request: Request,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> AnalyzeResponse:
    """
    Analyze and correct English text.

    Args:
        request: Analysis request with text and mode
        user: User object (None for anonymous users)
        db: Database session

    Returns:
        AnalyzeResponse with corrected text and error details

    Raises:
        400: If request validation fails
        429: If rate limit exceeded
        500: If analysis fails
    """
    try:
        # Check rate limits
        rate_limit_service = get_rate_limit_service()

        # Determine user tier and ID
        user_tier = user.tier if user else "anonymous"
        user_id = str(user.id) if user else "anon:" + http_request.client.host

        logger.info(f"[ANALYZE] Starting analysis - user_id: {user_id}, user_tier: {user_tier}")

        # Check daily quota
        allowed, quota_info = await rate_limit_service.check_rate_limit(
            user_id=user_id,
            user_tier=user_tier,
            quota_type="daily",
            db=db
        )

        logger.info(f"[ANALYZE] Rate limit check complete - allowed: {allowed}")

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Daily quota exceeded. Limit: {quota_info['limit']}, Used: {quota_info['used']}",
                    "limit_type": quota_info["limit_type"],
                    "limit": quota_info["limit"],
                    "used": quota_info["used"],
                    "remaining": quota_info["remaining"],
                    "resets_in": quota_info["resets_in"]
                }
            )

        # Perform analysis
        service = get_analysis_service()
        response = await service.analyze(request, user, db)

        logger.info(f"[ANALYZE] Analysis complete - errors found: {len(response.errors)}")

        # Track usage
        tokens_used = response.token_usage.get("total_tokens", 0)
        estimated_cost = response.token_usage.get("estimated_cost", 0.0)
        await rate_limit_service.track_usage(user_id, tokens_used, estimated_cost, db)

        return response

    except HTTPException:
        raise
    except AnalysisServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

