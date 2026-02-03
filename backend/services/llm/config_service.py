"""
LLM Configuration Service.

This module provides service layer for managing user LLM configurations,
including provider selection, model preferences, and API key management.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.llm_provider import LLMProvider, UserLLMConfig
from models.user import User, UserSettings
from providers import LLMProviderFactory
from .encryption import encrypt_api_key, decrypt_api_key, safe_decrypt, EncryptionError


class LLMConfigError(Exception):
    """Base exception for LLM configuration errors."""
    pass


class ProviderNotFoundError(LLMConfigError):
    """Raised when provider is not found."""
    pass


class UserNotFoundError(LLMConfigError):
    """Raised when user is not found."""
    pass


class ConfigurationError(LLMConfigError):
    """Raised when configuration is invalid."""
    pass


class LLMConfigService:
    """
    Service for managing user LLM configurations.

    Handles:
    - Getting user's active LLM configuration
    - Updating provider and model preferences
    - Managing custom API keys (encrypted storage)
    - Resolving API keys (custom or system default)
    """

    def __init__(self, db: Session):
        """
        Initialize LLM configuration service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_user_config(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current LLM configuration.

        Args:
            user_id: User ID (UUID as string)

        Returns:
            Dictionary containing user's LLM configuration:
            {
                "active_provider": "zhipu",
                "active_model": "glm-4-flashx",
                "has_custom_key": False,
                "using_system_default": True,
                "provider_display_name": "Zhipu AI",
                "model_display_name": "GLM-4-FlashX"
            }

        Raises:
            UserNotFoundError: If user does not exist
            LLMConfigError: For other database errors

        Example:
            ```python
            config = service.get_user_config(user_id="123e4567-e89b-12d3-a456-426614174000")
            print(f"User is using {config['provider_display_name']}")
            ```
        """
        try:
            # Get user settings
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            settings = user.settings
            if not settings:
                # Create default settings if not exist
                settings = UserSettings(
                    user_id=user_id,
                    active_llm_provider="zhipu",
                    active_llm_model="glm-4-flashx"
                )
                self.db.add(settings)
                self.db.commit()

            # Get provider information
            provider_name = settings.active_llm_provider
            model_name = settings.active_llm_model

            provider = self.db.query(LLMProvider).filter(
                LLMProvider.name == provider_name
            ).first()

            if not provider:
                raise ProviderNotFoundError(f"Provider '{provider_name}' not found")

            # Check if user has custom API key
            user_config = self.db.query(UserLLMConfig).filter(
                UserLLMConfig.user_id == user_id,
                UserLLMConfig.provider_name == provider_name
            ).first()

            has_custom_key = bool(user_config and user_config.custom_api_key_encrypted)

            # Get model display name
            model_display_name = model_name
            for model_info in provider.supported_models:
                if model_info.get("name") == model_name:
                    model_display_name = model_info.get("display_name", model_name)
                    break

            return {
                "active_provider": provider_name,
                "active_model": model_name,
                "has_custom_key": has_custom_key,
                "using_system_default": not has_custom_key,
                "provider_display_name": provider.display_name,
                "model_display_name": model_display_name,
            }

        except (UserNotFoundError, ProviderNotFoundError):
            raise
        except SQLAlchemyError as e:
            raise LLMConfigError(f"Database error: {str(e)}")

    def update_user_config(
        self,
        user_id: str,
        provider: str,
        model: str,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user's LLM configuration.

        Args:
            user_id: User ID (UUID as string)
            provider: Provider name ("zhipu", "openai", "anthropic")
            model: Model name (e.g., "glm-4-flashx", "gpt-4")
            api_key: Optional custom API key (will be encrypted before storage)

        Returns:
            Updated configuration dictionary

        Raises:
            UserNotFoundError: If user does not exist
            ProviderNotFoundError: If provider does not exist
            ConfigurationError: If model is not supported by provider
            LLMConfigError: For other errors

        Example:
            ```python
            config = service.update_user_config(
                user_id="123e4567-e89b-12d3-a456-426614174000",
                provider="openai",
                model="gpt-4",
                api_key="sk-1234567890"  # Optional
            )
            ```
        """
        try:
            # Validate user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            # Validate provider exists
            provider_obj = self.db.query(LLMProvider).filter(
                LLMProvider.name == provider,
                LLMProvider.is_enabled == True
            ).first()

            if not provider_obj:
                raise ProviderNotFoundError(
                    f"Provider '{provider}' not found or not enabled"
                )

            # Validate model is supported by provider
            supported_models = [m.get("name") for m in provider_obj.supported_models]
            if model not in supported_models:
                raise ConfigurationError(
                    f"Model '{model}' is not supported by provider '{provider}'. "
                    f"Supported models: {', '.join(supported_models)}"
                )

            # Update or create user settings
            settings = user.settings
            if not settings:
                settings = UserSettings(user_id=user_id)
                self.db.add(settings)

            settings.active_llm_provider = provider
            settings.active_llm_model = model

            # Handle custom API key
            if api_key:
                # Encrypt the API key
                encrypted_key = encrypt_api_key(api_key)

                # Create or update user LLM config
                user_config = self.db.query(UserLLMConfig).filter(
                    UserLLMConfig.user_id == user_id,
                    UserLLMConfig.provider_name == provider
                ).first()

                if user_config:
                    user_config.selected_model = model
                    user_config.custom_api_key_encrypted = encrypted_key
                    user_config.is_active = True
                else:
                    user_config = UserLLMConfig(
                        user_id=user_id,
                        provider_name=provider,
                        selected_model=model,
                        custom_api_key_encrypted=encrypted_key,
                        is_active=True
                    )
                    self.db.add(user_config)

            self.db.commit()

            # Return updated configuration
            return self.get_user_config(user_id)

        except (UserNotFoundError, ProviderNotFoundError, ConfigurationError):
            self.db.rollback()
            raise
        except EncryptionError as e:
            self.db.rollback()
            raise LLMConfigError(f"Failed to encrypt API key: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise LLMConfigError(f"Database error: {str(e)}")

    def delete_user_api_key(self, user_id: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete user's custom API key (fall back to system default).

        Args:
            user_id: User ID (UUID as string)
            provider: Optional provider name (deletes for active provider if not specified)

        Returns:
            Updated configuration dictionary

        Raises:
            UserNotFoundError: If user does not exist
            LLMConfigError: For other errors

        Example:
            ```python
            # Delete custom key for active provider
            config = service.delete_user_api_key(user_id="123e4567...")

            # Delete custom key for specific provider
            config = service.delete_user_api_key(user_id="123e4567...", provider="openai")
            ```
        """
        try:
            # Validate user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            # Determine which provider to delete key for
            if not provider:
                settings = user.settings
                if not settings:
                    raise LLMConfigError("User has no active provider configuration")
                provider = settings.active_llm_provider

            # Find and delete user config
            user_config = self.db.query(UserLLMConfig).filter(
                UserLLMConfig.user_id == user_id,
                UserLLMConfig.provider_name == provider
            ).first()

            if user_config:
                if user_config.custom_api_key_encrypted:
                    user_config.custom_api_key_encrypted = None
                    user_config.is_active = False
                    self.db.commit()

            # Return updated configuration
            return self.get_user_config(user_id)

        except UserNotFoundError:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise LLMConfigError(f"Database error: {str(e)}")

    def get_api_key_for_user(self, user_id: str, provider: str) -> str:
        """
        Get API key for a user and provider (custom or system default).

        Args:
            user_id: User ID (UUID as string)
            provider: Provider name

        Returns:
            Decrypted API key (plain text)

        Raises:
            UserNotFoundError: If user does not exist
            ProviderNotFoundError: If provider does not exist
            LLMConfigError: If no API key available (neither custom nor system default)

        Example:
            ```python
            api_key = service.get_api_key_for_user(
                user_id="123e4567...",
                provider="zhipu"
            )
            # Use api_key to create provider instance
            ```
        """
        try:
            # Check for custom user API key first
            user_config = self.db.query(UserLLMConfig).filter(
                UserLLMConfig.user_id == user_id,
                UserLLMConfig.provider_name == provider
            ).first()

            if user_config and user_config.custom_api_key_encrypted:
                # User has custom key, decrypt and return
                return decrypt_api_key(user_config.custom_api_key_encrypted)

            # Fall back to system default
            provider_obj = self.db.query(LLMProvider).filter(
                LLMProvider.name == provider
            ).first()

            if not provider_obj:
                raise ProviderNotFoundError(f"Provider '{provider}' not found")

            if not provider_obj.default_api_key_encrypted:
                raise LLMConfigError(
                    f"No API key available for provider '{provider}'. "
                    f"User has no custom key and provider has no system default."
                )

            # Decrypt and return system default
            return decrypt_api_key(provider_obj.default_api_key_encrypted)

        except (UserNotFoundError, ProviderNotFoundError):
            raise
        except EncryptionError as e:
            raise LLMConfigError(f"Failed to decrypt API key: {str(e)}")
        except SQLAlchemyError as e:
            raise LLMConfigError(f"Database error: {str(e)}")

    def list_available_providers(self) -> list:
        """
        List all available and enabled providers.

        Returns:
            List of provider information dictionaries

        Example:
            ```python
            providers = service.list_available_providers()
            for provider in providers:
                print(f"{provider['display_name']}: {len(provider['models'])} models")
            ```
        """
        try:
            providers = self.db.query(LLMProvider).filter(
                LLMProvider.is_enabled == True
            ).all()

            return [
                {
                    "name": p.name,
                    "display_name": p.display_name,
                    "is_enabled": p.is_enabled,
                    "models": p.supported_models,
                }
                for p in providers
            ]

        except SQLAlchemyError as e:
            raise LLMConfigError(f"Database error: {str(e)}")
