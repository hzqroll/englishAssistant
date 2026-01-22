"""
Schemas package.

This package contains all Pydantic schemas for API requests and responses.
"""

from .auth import RegisterRequest, LoginRequest, RefreshTokenRequest, AuthResponse, UserResponse
from .analysis import AnalyzeRequest, AnalyzeResponse, ErrorDetailResponse
from .user import UserCreate, UserUpdate, UserResponse as UserResponseSchema
from .error import APIError, QuotaExceededError

__all__ = [
    # Auth schemas
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "AuthResponse",
    "UserResponse",

    # Analysis schemas
    "AnalyzeRequest",
    "AnalyzeResponse",
    "ErrorDetailResponse",

    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponseSchema",

    # Error schemas
    "APIError",
    "QuotaExceededError",
]
