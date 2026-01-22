"""
Authentication middleware.

Verifies JWT tokens and injects user context into requests.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import logging

from core.security import verify_token
from core.config import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware.

    Validates JWT tokens and injects user information into request state.

    Attributes:
        public_paths: List of paths that don't require authentication
    """

    def __init__(self, app, public_paths: list = None):
        """
        Initialize authentication middleware.

        Args:
            app: FastAPI application
            public_paths: List of public paths (no auth required)
        """
        super().__init__(app)
        self.public_paths = public_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/register",
            "/api/v1/auth/login"
        ]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and validate authentication.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            HTTP response

        Raises:
            HTTPException: If authentication fails
        """
        # TODO: Implement authentication middleware
        # 1. Check if path is public
        # 2. Extract token from Authorization header
        # 3. Verify token
        # 4. Inject user info into request state
        # 5. Call next handler

        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        # Extract token
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        token = authorization.split(" ")[1]

        # Verify token
        payload = verify_token(token, settings.SECRET_KEY)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Inject user info into request state
        request.state.user_id = payload.get("sub")
        request.state.token_type = payload.get("type")

        # Call next handler
        response = await call_next(request)
        return response
