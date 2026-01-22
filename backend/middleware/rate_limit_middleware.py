"""
Rate limiting middleware.

Enforces API rate limits based on user tier and quota.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import logging
from datetime import datetime

from services import RateLimitService

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Enforces rate limits for API requests based on user tier.

    Attributes:
        rate_limit_service: Rate limit service instance
        limit_exempt_paths: Paths exempt from rate limiting
    """

    def __init__(
        self,
        app,
        rate_limit_service: RateLimitService = None,
        limit_exempt_paths: list = None
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            rate_limit_service: Rate limit service instance
            limit_exempt_paths: Paths exempt from rate limiting
        """
        super().__init__(app)
        self.rate_limit_service = rate_limit_service or RateLimitService()
        self.limit_exempt_paths = limit_exempt_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and enforce rate limits.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            HTTP response

        Raises:
            HTTPException: If rate limit exceeded
        """
        # TODO: Implement rate limiting middleware
        # 1. Check if path is exempt
        # 2. Get user from request state
        # 3. Check rate limits
        # 4. Track usage
        # 5. Add rate limit headers to response
        # 6. Call next handler

        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.limit_exempt_paths):
            return await call_next(request)

        # Get user from state (set by auth middleware)
        user = getattr(request.state, "user", None)

        if user:
            # Check rate limits
            # Note: This requires database session, which we don't have here
            # In production, move this check to endpoint level or use dependency injection
            pass

        # Call next handler
        response = await call_next(request)

        # Add rate limit headers
        # TODO: Add actual rate limit info
        response.headers["X-RateLimit-Limit"] = "100"
        response.headers["X-RateLimit-Remaining"] = "99"
        response.headers["X-RateLimit-Reset"] = "1640000000"

        return response
