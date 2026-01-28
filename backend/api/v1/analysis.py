"""
Analysis API routes.

Handles text analysis and correction endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import get_db, User
from schemas.analysis import AnalyzeRequest, AnalyzeResponse
from services.analysis_service import AnalysisService, AnalysisServiceError
from services.rate_limit_service import RateLimitService, QuotaExceededError
from core.security import get_optional_user

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
        # TODO: Check rate limits
        # For now, skip rate limiting to test core functionality

        # Perform analysis
        service = get_analysis_service()
        response = service.analyze(request, user, db)
        return response

    except AnalysisServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

