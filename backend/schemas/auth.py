"""
Authentication-related schemas.

Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    tier: Optional[str] = Field(default="free", description="User tier")
    default_mode: Optional[str] = Field(default="accuracy", description="Default correction mode")


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response with tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    tier: str = Field(..., description="User tier")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "tier": "free"
            }
        }


class UserResponse(BaseModel):
    """User information response."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    tier: str = Field(..., description="User tier")
    is_active: bool = Field(..., description="Whether account is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    created_at: datetime = Field(..., description="Account creation date")
    last_login_at: Optional[datetime] = Field(None, description="Last login date")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "tier": "free",
                "is_active": True,
                "is_verified": False,
                "created_at": "2026-01-22T10:00:00Z",
                "last_login_at": "2026-01-22T12:00:00Z"
            }
        }
