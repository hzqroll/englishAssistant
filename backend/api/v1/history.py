"""
History API routes.

Handles retrieval and management of user's analysis history.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from models import get_db, User
from services.analysis_service import AnalysisService
from core.security import get_current_user

router = APIRouter()

# Lazy load the service to avoid import-time issues with zhipuai on Python 3.14
def get_analysis_service() -> AnalysisService:
    """Get or create the analysis service instance."""
    return AnalysisService()


@router.get("/history")
async def get_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user's analysis history with pagination.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated history list
    """
    try:
        service = get_analysis_service()
        history = service.get_history(current_user, db, skip=skip, limit=limit)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.get("/history/{analysis_id}")
async def get_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific analysis.

    Args:
        analysis_id: Analysis ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Detailed analysis information

    Raises:
        401: If authentication fails
        404: If analysis not found
        403: If user doesn't own the analysis
    """
    try:
        # Convert string ID to UUID
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID format"
        )

    service = get_analysis_service()
    detail = service.get_analysis(analysis_id, current_user, db)

    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return detail


@router.delete("/history/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Soft delete an analysis record.

    Args:
        analysis_id: Analysis ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        401: If authentication fails
        404: If analysis not found
        403: If user doesn't own the analysis
    """
    try:
        # Convert string ID to UUID
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID format"
        )

    service = get_analysis_service()
    success = service.delete_analysis(analysis_id, current_user, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return {"message": "Analysis deleted successfully"}
