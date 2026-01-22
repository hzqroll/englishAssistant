"""
Performance monitoring middleware.

Tracks request timing and performance metrics.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
import time

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring middleware.

    Tracks request timing and logs performance metrics.

    Attributes:
        log_slow_requests: Whether to log slow requests
        slow_request_threshold_ms: Threshold for slow requests (milliseconds)
    """

    def __init__(
        self,
        app,
        log_slow_requests: bool = True,
        slow_request_threshold_ms: int = 1000
    ):
        """
        Initialize performance middleware.

        Args:
            app: FastAPI application
            log_slow_requests: Whether to log slow requests
            slow_request_threshold_ms: Threshold for slow requests
        """
        super().__init__(app)
        self.log_slow_requests = log_slow_requests
        self.slow_request_threshold_ms = slow_request_threshold_ms

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and track performance.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # TODO: Implement performance monitoring
        # 1. Record start time
        # 2. Call next handler
        # 3. Calculate duration
        # 4. Log slow requests
        # 5. Add timing headers to response
        # 6. Track metrics (optional: send to monitoring system)

        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log slow requests
        if self.log_slow_requests and duration_ms > self.slow_request_threshold_ms:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration_ms}ms"
            )

        # Add timing headers
        response.headers["X-Process-Time"] = str(duration_ms)

        return response
