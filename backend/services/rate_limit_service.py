"""
Rate limiting service.

Manages API rate limiting and quota enforcement.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import User, APICredit


class RateLimitService:
    """
    Rate limiting and quota management service.

    Enforces API usage limits based on user tier and quota type.

    Attributes:
        limits: Dictionary of tier-based limits
        quota_types: Supported quota types
    """

    def __init__(self):
        """Initialize the rate limit service."""
        self.limits = {
            'anonymous': {'hourly': 5, 'daily': 10},
            'free': {'daily': 50, 'monthly': 1000},
            'pro': {'daily': 500, 'monthly': 10000},
            'enterprise': {'daily': 5000, 'monthly': 100000}
        }
        self.quota_types = ['hourly', 'daily', 'monthly']

    async def check_rate_limit(
        self,
        user: User,
        quota_type: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Check if user has exceeded rate limit.

        Args:
            user: User object
            quota_type: Type of quota (daily/monthly)
            db: Database session

        Returns:
            Dictionary with limit status

        Example:
            ```python
            service = RateLimitService()
            status = await service.check_rate_limit(user, 'daily', db)
            if not status['allowed']:
                raise QuotaExceededError(status['message'])
            ```
        """
        # TODO: Implement rate limit check
        # 1. Get user's quota limits based on tier
        # 2. Find or create quota record
        # 3. Check if quota exceeded
        # 4. Return status

        limit = self._get_limit(user.tier, quota_type)
        credit = self._get_or_create_credit(user, quota_type, db)

        remaining = max(0, limit - credit.used)
        allowed = credit.used < limit
        reset_at = credit.period_end

        return {
            'allowed': allowed,
            'limit': limit,
            'used': credit.used,
            'remaining': remaining,
            'reset_at': reset_at,
            'message': self._get_limit_message(allowed, remaining, reset_at)
        }

    async def track_usage(
        self,
        user: User,
        tokens_used: int,
        estimated_cost: float,
        db: Session
    ) -> None:
        """
        Track API usage for rate limiting.

        Args:
            user: User object
            tokens_used: Number of tokens consumed
            estimated_cost: Estimated cost in currency
            db: Database session
        """
        # TODO: Implement usage tracking
        # 1. Update daily quota
        # 2. Update monthly quota
        # 3. Increment usage counters
        # 4. Update token statistics

        now = datetime.utcnow()

        # Update daily quota
        daily_credit = self._get_or_create_credit(user, 'daily', db)
        daily_credit.used += 1
        daily_credit.total_tokens_used += tokens_used
        daily_credit.estimated_cost += estimated_cost

        # Update monthly quota
        monthly_credit = self._get_or_create_credit(user, 'monthly', db)
        monthly_credit.used += 1
        monthly_credit.total_tokens_used += tokens_used
        monthly_credit.estimated_cost += estimated_cost

        db.commit()

    def _get_limit(self, tier: str, quota_type: str) -> int:
        """
        Get rate limit for user tier and quota type.

        Args:
            tier: User tier
            quota_type: Quota type

        Returns:
            Rate limit value
        """
        return self.limits.get(tier, {}).get(quota_type, 0)

    def _get_or_create_credit(
        self,
        user: User,
        quota_type: str,
        db: Session
    ) -> APICredit:
        """
        Get or create API credit record.

        Args:
            user: User object
            quota_type: Quota type
            db: Database session

        Returns:
            APICredit object
        """
        # TODO: Implement credit record retrieval/creation
        now = datetime.utcnow()

        if quota_type == 'daily':
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif quota_type == 'monthly':
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Calculate next month
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        else:
            raise ValueError(f"Invalid quota_type: {quota_type}")

        # Find existing credit
        credit = (
            db.query(APICredit)
            .filter(APICredit.user_id == user.id)
            .filter(APICredit.quota_type == quota_type)
            .filter(APICredit.period_start == period_start)
            .first()
        )

        if not credit:
            # Create new credit record
            limit = self._get_limit(user.tier, quota_type)
            credit = APICredit(
                user_id=user.id,
                quota_type=quota_type,
                quota=limit,
                used=0,
                period_start=period_start,
                period_end=period_end
            )
            db.add(credit)
            db.commit()

        return credit

    def _get_limit_message(
        self,
        allowed: bool,
        remaining: int,
        reset_at: datetime
    ) -> str:
        """
        Get human-readable limit message.

        Args:
            allowed: Whether request is allowed
            remaining: Remaining quota
            reset_at: Reset timestamp

        Returns:
            Message string
        """
        if allowed:
            return f"{remaining} requests remaining"
        else:
            return f"Rate limit exceeded. Resets at {reset_at.isoformat()}"

    async def reset_quota(
        self,
        user: User,
        quota_type: str,
        db: Session
    ) -> bool:
        """
        Reset user's quota (admin function).

        Args:
            user: User object
            quota_type: Quota type
            db: Database session

        Returns:
            True if successful
        """
        # TODO: Implement quota reset
        credit = (
            db.query(APICredit)
            .filter(APICredit.user_id == user.id)
            .filter(APICredit.quota_type == quota_type)
            .first()
        )

        if credit:
            credit.used = 0
            db.commit()

        return True

    def get_user_stats(self, user: User, db: Session) -> Dict[str, Any]:
        """
        Get user's rate limit statistics.

        Args:
            user: User object
            db: Database session

        Returns:
            Statistics dictionary
        """
        # TODO: Implement statistics retrieval
        credits = (
            db.query(APICredit)
            .filter(APICredit.user_id == user.id)
            .all()
        )

        stats = {
            'tier': user.tier,
            'quotas': {}
        }

        for credit in credits:
            stats['quotas'][credit.quota_type] = {
                'limit': credit.quota,
                'used': credit.used,
                'remaining': credit.remaining,
                'is_exceeded': credit.is_exceeded,
                'period_start': credit.period_start,
                'period_end': credit.period_end,
                'total_tokens': credit.total_tokens_used,
                'estimated_cost': credit.estimated_cost
            }

        return stats


class RateLimitError(Exception):
    """Base exception for rate limit errors."""

    pass


class QuotaExceededError(RateLimitError):
    """Exception raised when quota is exceeded."""

    def __init__(self, message: str, reset_at: Optional[datetime] = None):
        """
        Initialize quota exceeded error.

        Args:
            message: Error message
            reset_at: When quota resets
        """
        self.message = message
        self.reset_at = reset_at
        super().__init__(self.message)
