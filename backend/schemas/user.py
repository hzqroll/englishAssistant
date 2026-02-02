"""
User-related schemas.

Pydantic models for user operations.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User creation request."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    tier: Optional[str] = Field(default="free", description="User tier")
    default_mode: Optional[str] = Field(default="accuracy", description="Default correction mode")


class UserUpdate(BaseModel):
    """User update request."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    tier: Optional[str] = Field(None, description="User tier")
    default_mode: Optional[str] = Field(None, description="Default correction mode")


class UserResponse(BaseModel):
    """User response."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    tier: str = Field(..., description="User tier")
    is_active: bool = Field(..., description="Account status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation date")
    last_login_at: Optional[datetime] = Field(None, description="Last login date")

    class Config:
        """Pydantic config."""
        from_attributes = True
