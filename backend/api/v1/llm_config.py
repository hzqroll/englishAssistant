"""
LLM Configuration API Router.

This module provides API endpoints for managing LLM provider configurations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.session import get_db
from api.v1.dependencies import get_current_user
from models.user import User
from services.llm import (
    LLMConfigService,
    ProviderKeyResolver,
    ConfigValidator,
    LLMConfigError,
    ProviderNotFoundError,
    UserNotFoundError,
    ConfigurationError,
    ValidationError,
)
from .schemas.llm_config import (
    ProviderInfo,
    ModelInfo,
    ProvidersResponse,
    UserConfigResponse,
    UpdateConfigRequest,
    UpdateConfigResponse,
    DeleteApiKeyResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/llm", tags=["LLM Configuration"])


@router.get(
    "/providers",
    response_model=ProvidersResponse,
    status_code=status.HTTP_200_OK,
    summary="List available LLM providers",
    description="Get list of all available LLM providers and their supported models"
)
def list_providers(
    db: Session = Depends(get_db)
) -> ProvidersResponse:
    """
    List all available LLM providers and their supported models.

    This is a public endpoint that does not require authentication.

    Returns:
        List of providers with their models and capabilities
    """
    try:
        config_service = LLMConfigService(db)
        providers_data = config_service.list_available_providers()

        # Convert to response format
        providers = []
        for provider in providers_data:
            models = [
                ModelInfo(**model) for model in provider.get("models", [])
            ]
            providers.append(
                ProviderInfo(
                    name=provider["name"],
                    display_name=provider["display_name"],
                    is_enabled=provider["is_enabled"],
                    models=models
                )
            )

        return ProvidersResponse(providers=providers)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve providers: {str(e)}"
        )


@router.get(
    "/config",
    response_model=UserConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's LLM configuration",
    description="Get current user's LLM provider and model configuration"
)
def get_user_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserConfigResponse:
    """
    Get current user's LLM configuration.

    Requires JWT authentication.

    Returns:
        User's active provider, model, and API key status
    """
    try:
        config_service = LLMConfigService(db)
        config = config_service.get_user_config(str(current_user.id))

        return UserConfigResponse(**config)

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except LLMConfigError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve configuration: {str(e)}"
        )


@router.put(
    "/config",
    response_model=UpdateConfigResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user's LLM configuration",
    description="Update user's LLM provider, model, and optional custom API key"
)
def update_user_config(
    request: UpdateConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UpdateConfigResponse:
    """
    Update user's LLM configuration.

    Requires JWT authentication.

    Args:
        request: Configuration update request
        - provider: Provider name
        - model: Model name
        - api_key: Optional custom API key

    Returns:
        Updated configuration

    Raises:
        400: Invalid configuration
        404: Provider not found
        422: Validation error
    """
    try:
        # Validate configuration first
        validator = ConfigValidator(db)

        # Validate provider and model
        if not validator.validate_provider_name(request.provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{request.provider}' is not supported or enabled",
                headers={"error_code": "INVALID_PROVIDER"}
            )

        if not validator.validate_model_for_provider(request.provider, request.model):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{request.model}' is not supported by provider '{request.provider}'",
                headers={"error_code": "INVALID_MODEL"}
            )

        # Test API key if provided
        if request.api_key:
            key_validation = validator.validate_api_key(
                request.provider,
                request.api_key,
                timeout=10
            )
            if not key_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"API key validation failed: {key_validation['message']}",
                    headers={"error_code": key_validation.get("error", "INVALID_API_KEY")}
                )

        # Update configuration
        config_service = LLMConfigService(db)
        updated_config = config_service.update_user_config(
            user_id=str(current_user.id),
            provider=request.provider,
            model=request.model,
            api_key=request.api_key
        )

        return UpdateConfigResponse(
            active_provider=updated_config["active_provider"],
            active_model=updated_config["active_model"],
            has_custom_key=updated_config["has_custom_key"],
            using_system_default=updated_config["using_system_default"],
            message="LLM configuration updated successfully"
        )

    except (ProviderNotFoundError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ConfigurationError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except LLMConfigError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.delete(
    "/config/api-key",
    response_model=DeleteApiKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete custom API key",
    description="Remove user's custom API key and fall back to system default"
)
def delete_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> DeleteApiKeyResponse:
    """
    Delete user's custom API key.

    Requires JWT authentication.

    After deletion, the system will use the default API key for the provider.

    Returns:
        Updated configuration showing system default usage
    """
    try:
        config_service = LLMConfigService(db)
        updated_config = config_service.delete_user_api_key(str(current_user.id))

        return DeleteApiKeyResponse(
            message="Custom API key removed. Using system default.",
            active_provider=updated_config["active_provider"],
            active_model=updated_config["active_model"],
            has_custom_key=updated_config["has_custom_key"],
            using_system_default=updated_config["using_system_default"]
        )

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except LLMConfigError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API key: {str(e)}"
        )
