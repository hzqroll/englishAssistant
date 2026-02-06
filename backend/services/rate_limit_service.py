"""
Rate limiting service.

Manages API rate limiting and quota enforcement (in-memory for MVP version).
"""

import logging
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from models import User, APICredit

logger = logging.getLogger(__name__)


def _user_id_to_uuid(user_id: str) -> UUID:
    """
    Convert user_id string to UUID.

    For anonymous users with "anon:" prefix, generates a deterministic UUID
    from the string using MD5 hash. This ensures the same anonymous user
    (same IP) always gets the same UUID.

    Args:
        user_id: User ID string (UUID string or "anon:*" format)

    Returns:
        UUID object
    """
    if isinstance(user_id, UUID):
        return user_id

    try:
        # Try to parse as UUID directly
        return UUID(user_id)
    except ValueError:
        # For anonymous users with "anon:" prefix, generate deterministic UUID
        # from MD5 hash of the string
        hash_digest = hashlib.md5(user_id.encode()).hexdigest()
        return UUID(hash_digest)


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
        self.quota_types = ["hourly", "daily", "monthly"]
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
        logger.info(f"[RATE_LIMIT] check_rate_limit called - user_id: {user_id}, user_tier: {user_tier}, quota_type: {quota_type}")

        limit = self._get_limit(user_tier, quota_type)
        logger.info(f"[RATE_LIMIT] Got limit: {limit} for tier: {user_tier}, type: {quota_type}")

        # For anonymous users, use in-memory tracking only
        if user_tier == "anonymous":
            used = self._get_in_memory_count(user_id, quota_type)
            remaining = max(0, limit - used)
            allowed = used < limit
            reset_in = 3600 if quota_type == "hourly" else 86400  # 1 hour or 24 hours

            logger.info(f"[RATE_LIMIT] Anonymous user rate limit check - used: {used}, allowed: {allowed}")

            return (
                allowed,
                {
                    "limit_type": quota_type,
                    "limit": limit,
                    "used": used,
                    "remaining": remaining,
                    "resets_in": reset_in,
                },
            )

        # For authenticated users, use database tracking
        logger.info(f"[RATE_LIMIT] About to call _get_or_create_credit - user_id: {user_id}, quota_type: {quota_type}, user_tier: {user_tier}")
        credit = self._get_or_create_credit(user_id, quota_type, user_tier, db)
        logger.info(f"[RATE_LIMIT] Got credit - quota_type: {credit.quota_type}, used: {credit.used}, quota: {credit.quota}")

        remaining = max(0, limit - credit.used)
        allowed = credit.used < limit
        reset_at = credit.period_end

        logger.info(f"[RATE_LIMIT] Rate limit check result - allowed: {allowed}, remaining: {remaining}")

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
            user_id: User ID (string - can be UUID or "anon:*" format)
            tokens_used: Number of tokens consumed
            estimated_cost: Estimated cost in currency
            db: Database session
        """
        # For anonymous users (identified by "anon:" prefix), use in-memory tracking only
        if user_id.startswith("anon:"):
            self._increment_in_memory_count(user_id, "daily")
            return

        # For authenticated users, convert to UUID and track in database
        user_id_uuid = _user_id_to_uuid(user_id)
        user = db.query(User).filter(User.id == user_id_uuid).first()

        if not user:
            # If user not found, treat as anonymous
            self._increment_in_memory_count(user_id, "daily")
            return

        # Track daily usage in database for authenticated users
        daily_credit = self._get_or_create_credit(str(user_id_uuid), "daily", user.tier, db)
        daily_credit.used += 1
        daily_credit.total_tokens_used += tokens_used
        daily_credit.estimated_cost += estimated_cost

        db.commit()

    def _get_in_memory_count(self, user_id: str, quota_type: str) -> int:
        """
        Get in-memory request count for anonymous users.

        Args:
            user_id: User ID
            quota_type: Quota type

        Returns:
            Current count
        """
        if user_id not in self.request_counts:
            self.request_counts[user_id] = {}
        return self.request_counts[user_id].get(quota_type, 0)

    def _increment_in_memory_count(self, user_id: str, quota_type: str) -> None:
        """
        Increment in-memory request count for anonymous users.

        Args:
            user_id: User ID
            quota_type: Quota type
        """
        if user_id not in self.request_counts:
            self.request_counts[user_id] = {}
        self.request_counts[user_id][quota_type] = self._get_in_memory_count(user_id, quota_type) + 1

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
        logger.info(f"[GET_CREDIT] _get_or_create_credit called - user_id: {user_id}, quota_type: {quota_type}, user_tier: {user_tier}")

        limit = self._get_limit(user_tier, quota_type)
        logger.info(f"[GET_CREDIT] Calculated limit: {limit}")

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

        logger.info(f"[GET_CREDIT] Querying for existing credit - quota_type: {quota_type}, period_start: {period_start}")

        # Convert user_id to UUID for database query
        user_id_uuid = _user_id_to_uuid(user_id)

        credit = (
            db.query(APICredit)
            .filter(APICredit.user_id == user_id_uuid)
            .filter(APICredit.quota_type == quota_type)
            .filter(APICredit.period_start == period_start)
            .first()
        )

        if not credit:
            logger.info(f"[GET_CREDIT] No existing credit found, creating new - quota_type: {quota_type}")
            import uuid

            logger.info(f"[GET_CREDIT] Creating APICredit with - quota_type: {quota_type}, quota: {limit}, user_id: {user_id_uuid}")

            credit = APICredit(
                id=uuid.uuid4(),
                user_id=user_id_uuid,
                quota_type=quota_type,
                quota=limit,
                used=0,
                period_start=period_start,
                period_end=period_end,
            )
            db.add(credit)
            db.commit()
            logger.info(f"[GET_CREDIT] APICredit created successfully - quota_type: {credit.quota_type}")

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

        # Convert user_id to UUID for database query
        user_id_uuid = _user_id_to_uuid(user_id)

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
            .filter(APICredit.user_id == user_id_uuid)
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

        # Convert user_id to UUID for database query
        user_id_uuid = _user_id_to_uuid(user_id)

        credits = db.query(APICredit).filter(APICredit.user_id == user_id_uuid).all()

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
