"""
Rate limiting service.

Manages API rate limiting and quota enforcement (in-memory for MVP version).
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import User, APICredit


class RateLimitService:
    """
    Rate limiting and quota management service (MVP version).

    Enforces API usage limits based on user tier and quota type.
    Uses in-memory storage for simplicity (suitable for V1).

    Attributes:
        limits: Dictionary of tier-based limits
        quota_types: Supported quota types
        request_counts: In-memory request counters
    """

    def __init__(self):
        """Initialize rate limit service."""
        self.limits = {
            "anonymous": {"hourly": 5, "daily": 10},
            "free": {"hourly": 10, "daily": 50},
            "pro": {"hourly": 100, "daily": 500},
            "enterprise": {"hourly": 1000, "daily": 5000},
        }
        self.quota_types = ["hourly", "daily"]
        self.request_counts: Dict[str, Dict[str, int]] = {}

    async def check_rate_limit(
        self, user_id: str, user_tier: str, quota_type: str, db: Session
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User ID
            user_tier: User tier
            quota_type: Type of quota (daily/hourly)
            db: Database session

        Returns:
            Tuple of (allowed, info_dict)

        Example:
            ```python
            service = RateLimitService()
            allowed, info = await service.check_rate_limit("user123", "free", "daily", db)
            if not allowed:
                raise QuotaExceededError(info['message'])
            ```
        """
        limit = self._get_limit(user_tier, quota_type)
        credit = self._get_or_create_credit(user_id, user_tier, quota_type, db)

        remaining = max(0, limit - credit.used)
        allowed = credit.used < limit
        reset_at = credit.period_end

        return (
            allowed,
            {
                "limit_type": quota_type,
                "limit": limit,
                "used": credit.used,
                "remaining": remaining,
                "resets_in": max(0, (reset_at - datetime.utcnow()).total_seconds()),
            },
        )

    async def track_usage(
        self, user_id: str, tokens_used: int, estimated_cost: float, db: Session
    ) -> None:
        """
        Track API usage for rate limiting.

        Args:
            user_id: User ID
            tokens_used: Number of tokens consumed
            estimated_cost: Estimated cost in currency
            db: Database session
        """
        now = datetime.utcnow()

        daily_credit = self._get_or_create_credit(user_id, "daily", "free", db)
        daily_credit.used += 1
        daily_credit.total_tokens_used += tokens_used
        daily_credit.estimated_cost += estimated_cost
        daily_credit.period_end = daily_credit.period_start + timedelta(days=1)

        monthly_credit = self._get_or_create_credit(user_id, "monthly", "free", db)
        monthly_credit.used += 1
        monthly_credit.total_tokens_used += tokens_used
        monthly_credit.estimated_cost += estimated_cost

        db.commit()

    def _get_limit(self, user_tier: str, quota_type: str) -> int:
        """
        Get rate limit for user tier and quota type.

        Args:
            user_tier: User tier
            quota_type: Quota type

        Returns:
            Rate limit value
        """
        return self.limits.get(user_tier, {}).get(quota_type, 0)

    def _get_or_create_credit(
        self, user_id: str, quota_type: str, user_tier: str, db: Session
    ) -> APICredit:
        """
        Get or create API credit record.

        Args:
            user_id: User ID
            quota_type: Quota type
            user_tier: User tier
            db: Database session

        Returns:
            APICredit object
        """
        limit = self._get_limit(user_tier, quota_type)

        now = datetime.utcnow()

        if quota_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif quota_type == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        else:
            period_start = now
            period_end = now + timedelta(days=1)

        credit = (
            db.query(APICredit)
            .filter(APICredit.user_id == user_id)
            .filter(APICredit.quota_type == quota_type)
            .filter(APICredit.period_start == period_start)
            .first()
        )

        if not credit:
            from models import get_uuid

            credit = APICredit(
                id=get_uuid(),
                user_id=get_uuid(),
                quota_type=quota_type,
                quota=limit,
                used=0,
                period_start=period_start,
                period_end=period_end,
            )
            db.add(credit)
            db.commit()

        return credit

    async def reset_quota(self, user_id: str, quota_type: str, db: Session) -> bool:
        """
        Reset user's quota (admin function).

        Args:
            user_id: User ID
            quota_type: Quota type
            db: Database session

        Returns:
            True if successful
        """
        from models import APICredit

        now = datetime.utcnow()

        if quota_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif quota_type == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        else:
            period_start = now
            period_end = now + timedelta(days=1)

        credit = (
            db.query(APICredit)
            .filter(APICredit.user_id == user_id)
            .filter(APICredit.quota_type == quota_type)
            .filter(APICredit.period_start == period_start)
            .first()
        )

        if credit:
            credit.used = 0
            db.commit()
            return True

        return False

    def get_user_stats(self, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Get user's rate limit statistics.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Statistics dictionary
        """
        from models import APICredit

        credits = db.query(APICredit).filter(APICredit.user_id == user_id).all()

        stats = {"tier": None, "quotas": {}}

        for credit in credits:
            stats["quotas"][credit.quota_type] = {
                "limit": credit.quota,
                "used": credit.used,
                "remaining": max(0, credit.quota - credit.used),
                "is_exceeded": credit.used >= credit.quota,
                "period_start": credit.period_start,
                "period_end": credit.period_end,
                "total_tokens": credit.total_tokens_used,
                "estimated_cost": credit.estimated_cost,
            }

        return stats


class RateLimitError(Exception):
    """Base exception for rate limit errors."""

    pass


class QuotaExceededError(RateLimitError):
    """Exception raised when quota is exceeded."""

    def __init__(self, message: str, limit_type: Optional[str] = None):
        """
        Initialize quota exceeded error.

        Args:
            message: Error message
            limit_type: Type of quota exceeded
        """
        self.message = message
        self.limit_type = limit_type
        super().__init__(self.message)
