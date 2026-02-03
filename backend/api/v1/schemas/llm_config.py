"""
Pydantic schemas for LLM configuration API.

This module defines request/response schemas for LLM configuration endpoints.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class ModelInfo(BaseModel):
    """Schema for model information."""

    name: str = Field(..., description="Model name (e.g., 'glm-4-flashx', 'gpt-4')")
    display_name: str = Field(..., description="Human-readable model name")
    is_default: bool = Field(default=False, description="Whether this is the default model")
    description: str = Field(default="", description="Model description")
    max_tokens: Optional[int] = Field(None, description="Maximum token limit")
    cost_per_1k_tokens: Optional[float] = Field(None, description="Cost per 1000 tokens")

    class Config:
        schema_extra = {
            "example": {
                "name": "glm-4-flashx",
                "display_name": "GLM-4-FlashX",
                "is_default": True,
                "description": "Fastest model with excellent quality",
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.0001
            }
        }


class ProviderInfo(BaseModel):
    """Schema for provider information."""

    name: str = Field(..., description="Provider name (e.g., 'zhipu', 'openai')")
    display_name: str = Field(..., description="Human-readable provider name")
    is_enabled: bool = Field(..., description="Whether provider is enabled")
    models: List[ModelInfo] = Field(..., description="Supported models")

    class Config:
        schema_extra = {
            "example": {
                "name": "zhipu",
                "display_name": "Zhipu AI",
                "is_enabled": True,
                "models": [
                    {
                        "name": "glm-4-flashx",
                        "display_name": "GLM-4-FlashX",
                        "is_default": True,
                        "description": "Fastest model with excellent quality"
                    }
                ]
            }
        }


class ProvidersResponse(BaseModel):
    """Response schema for GET /llm/providers endpoint."""

    providers: List[ProviderInfo] = Field(..., description="List of available providers")

    class Config:
        schema_extra = {
            "example": {
                "providers": [
                    {
                        "name": "zhipu",
                        "display_name": "Zhipu AI",
                        "is_enabled": True,
                        "models": []
                    }
                ]
            }
        }


class UserConfigResponse(BaseModel):
    """Response schema for GET /llm/config endpoint."""

    active_provider: str = Field(..., description="Active provider name")
    active_model: str = Field(..., description="Active model name")
    has_custom_key: bool = Field(..., description="Whether user has custom API key")
    using_system_default: bool = Field(..., description="Whether using system default key")
    provider_display_name: str = Field(..., description="Provider display name")
    model_display_name: str = Field(..., description="Model display name")

    class Config:
        schema_extra = {
            "example": {
                "active_provider": "zhipu",
                "active_model": "glm-4-flashx",
                "has_custom_key": False,
                "using_system_default": True,
                "provider_display_name": "Zhipu AI",
                "model_display_name": "GLM-4-FlashX"
            }
        }


class UpdateConfigRequest(BaseModel):
    """Request schema for PUT /llm/config endpoint."""

    provider: str = Field(..., description="Provider name", min_length=1)
    model: str = Field(..., description="Model name", min_length=1)
    api_key: Optional[str] = Field(None, description="Optional custom API key")

    @validator('provider')
    def validate_provider(cls, v):
        """Validate provider name format."""
        if not v or not v.strip():
            raise ValueError("Provider name cannot be empty")
        return v.strip().lower()

    @validator('model')
    def validate_model(cls, v):
        """Validate model name format."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()

    @validator('api_key')
    def validate_api_key(cls, v):
        """Validate API key format if provided."""
        if v is not None:
            if len(v.strip()) < 10:
                raise ValueError("API key is too short (minimum 10 characters)")
            return v.strip()
        return v

    class Config:
        schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key": "sk-1234567890abcdef"
            }
        }


class UpdateConfigResponse(BaseModel):
    """Response schema for PUT /llm/config endpoint."""

    active_provider: str = Field(..., description="Updated active provider")
    active_model: str = Field(..., description="Updated active model")
    has_custom_key: bool = Field(..., description="Whether custom key was set")
    using_system_default: bool = Field(..., description="Whether using system default")
    message: str = Field(..., description="Success message")

    class Config:
        schema_extra = {
            "example": {
                "active_provider": "openai",
                "active_model": "gpt-4",
                "has_custom_key": True,
                "using_system_default": False,
                "message": "LLM configuration updated successfully"
            }
        }


class DeleteApiKeyResponse(BaseModel):
    """Response schema for DELETE /llm/config/api-key endpoint."""

    message: str = Field(..., description="Success message")
    active_provider: str = Field(..., description="Active provider")
    active_model: str = Field(..., description="Active model")
    has_custom_key: bool = Field(..., description="Should be False after deletion")
    using_system_default: bool = Field(..., description="Should be True after deletion")

    class Config:
        schema_extra = {
            "example": {
                "message": "Custom API key removed. Using system default.",
                "active_provider": "openai",
                "active_model": "gpt-4",
                "has_custom_key": False,
                "using_system_default": True
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for error responses."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Provider 'invalid' is not supported",
                "error_code": "INVALID_PROVIDER"
            }
        }
