"""
Error schemas.

Pydantic models for API error responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class APIError(BaseModel):
    """Standard API error response."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "INVALID_INPUT",
                "message": "Invalid input data",
                "details": {
                    "field": "text",
                    "reason": "Text cannot be empty"
                },
                "timestamp": "2026-01-22T10:00:00Z"
            }
        }


class QuotaExceededError(APIError):
    """Quota exceeded error response."""

    def __init__(
        self,
        message: str,
        reset_at: Optional[datetime] = None,
        quota_type: Optional[str] = None
    ):
        """
        Initialize quota exceeded error.

        Args:
            message: Error message
            reset_at: When quota resets
            quota_type: Type of quota exceeded
        """
        details = {}
        if reset_at:
            details['reset_at'] = reset_at.isoformat()
        if quota_type:
            details['quota_type'] = quota_type

        super().__init__(
            error="QUOTA_EXCEEDED",
            message=message,
            details=details if details else None
        )


class ValidationError(APIError):
    """Validation error response."""

    def __init__(self, message: str, field: Optional[str] = None):
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
        """
        details = {"field": field} if field else None
        super().__init__(
            error="VALIDATION_ERROR",
            message=message,
            details=details
        )


class UnauthorizedError(APIError):
    """Unauthorized error response."""

    def __init__(self, message: str = "Authentication required"):
        """
        Initialize unauthorized error.

        Args:
            message: Error message
        """
        super().__init__(
            error="UNAUTHORIZED",
            message=message
        )


class NotFoundError(APIError):
    """Not found error response."""

    def __init__(self, resource: str, resource_id: Optional[str] = None):
        """
        Initialize not found error.

        Args:
            resource: Resource type
            resource_id: Resource ID
        """
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"

        super().__init__(
            error="NOT_FOUND",
            message=message,
            details={"resource": resource, "id": resource_id}
        )
