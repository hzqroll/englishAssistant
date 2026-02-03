"""
Statistics API routes.

Handles user statistics and token usage information.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from typing import Dict, Any
from datetime import datetime, timedelta

from models import get_db, User, Analysis, ErrorDetail, APICredit
from core.security import get_current_user

router = APIRouter()


@router.get("/overview")
async def get_statistics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user's error statistics and trends.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Statistics overview with error counts, trends, and patterns

    Raises:
        401: If authentication fails
    """
    try:
        # Get total analyses count
        total_analyses = (
            db.query(func.count(Analysis.id))
            .filter(Analysis.user_id == current_user.id)
            .filter(Analysis.is_deleted == False)
            .scalar()
        ) or 0

        # Get total errors count
        total_errors = (
            db.query(func.count(ErrorDetail.id))
            .join(Analysis)
            .filter(Analysis.user_id == current_user.id)
            .filter(Analysis.is_deleted == False)
            .scalar()
        ) or 0

        # Get error distribution by type
        error_distribution = (
            db.query(
                ErrorDetail.error_type,
                func.count(ErrorDetail.id).label('count')
            )
            .join(Analysis)
            .filter(Analysis.user_id == current_user.id)
            .filter(Analysis.is_deleted == False)
            .group_by(ErrorDetail.error_type)
            .all()
        )

        error_types = {
            error_type: count
            for error_type, count in error_distribution
        }

        # Get most common errors (top 5)
        most_common_errors = sorted(
            error_types.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Get recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_analyses = (
            db.query(func.count(Analysis.id))
            .filter(Analysis.user_id == current_user.id)
            .filter(Analysis.created_at >= seven_days_ago)
            .filter(Analysis.is_deleted == False)
            .scalar()
        ) or 0

        # Calculate average errors per analysis
        avg_errors = round(total_errors / total_analyses, 2) if total_analyses > 0 else 0

        return {
            "total_analyses": total_analyses,
            "total_errors": total_errors,
            "average_errors_per_analysis": avg_errors,
            "error_distribution": error_types,
            "most_common_errors": [
                {"type": error_type, "count": count}
                for error_type, count in most_common_errors
            ],
            "recent_activity": {
                "last_7_days": recent_analyses
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/tokens")
async def get_token_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user's token usage statistics and costs.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Token usage statistics including totals, costs, and efficiency metrics

    Raises:
        401: If authentication fails
    """
    try:
        # Get current period API credits
        now = datetime.utcnow()
        current_credit = (
            db.query(APICredit)
            .filter(APICredit.user_id == current_user.id)
            .filter(APICredit.quota_type == "daily")
            .filter(APICredit.period_start <= now)
            .filter(APICredit.period_end > now)
            .first()
        )

        # Get all-time token usage from analyses
        # Using PostgreSQL JSON operators: ->> extracts as text, CAST to integer
        total_token_usage = (
            db.query(
                func.sum(
                    func.cast(
                        Analysis.token_usage['total_tokens'].astext,
                        Integer
                    )
                ).label('total_tokens')
            )
            .filter(Analysis.user_id == current_user.id)
            .filter(Analysis.is_deleted == False)
            .scalar()
        ) or 0

        # Build response
        quota_info = {
            "quota": current_credit.quota if current_credit else 0,
            "used": current_credit.used if current_credit else 0,
            "remaining": current_credit.remaining if current_credit else 0,
            "period_end": current_credit.period_end.isoformat() if current_credit else None,
        }

        token_stats = {
            "total_tokens_used": current_credit.total_tokens_used if current_credit else 0,
            "estimated_cost": round(current_credit.estimated_cost, 4) if current_credit else 0.0,
            "all_time_tokens": total_token_usage,
        }

        return {
            "quota": quota_info,
            "tokens": token_stats,
            "tier": current_user.tier
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve token usage: {str(e)}"
        )
