"""
Provider Key Resolver Utility.

This module provides utilities to resolve API keys and create provider instances
for users, handling the complexity of custom keys vs system defaults.
"""

from typing import Optional, Dict, Any
from functools import lru_cache

from sqlalchemy.orm import Session
from providers import LLMProviderFactory, BaseLLMProvider, CorrectionMode
from .config_service import LLMConfigService, LLMConfigError
from .encryption import decrypt_api_key


class ProviderResolverError(Exception):
    """Exception raised when provider resolution fails."""
    pass


class ProviderKeyResolver:
    """
    Utility for resolving and creating LLM provider instances for users.

    This class combines LLMConfigService and LLMProviderFactory to provide
    a simple interface for getting provider instances with the correct
    API keys (user's custom key or system default).

    Example:
        ```python
        resolver = ProviderKeyResolver(db)

        # Get provider instance for user's active configuration
        provider = resolver.get_provider_for_user(user_id="123e4567...")

        # Get provider instance for specific provider
        provider = resolver.get_provider(user_id="123e4567...", provider="openai")

        # Optimize text using user's configuration
        result = resolver.optimize_text(
            user_id="123e4567...",
            text="He go to school yesterday.",
            mode=CorrectionMode.ACCURACY
        )
        ```
    """

    def __init__(self, db: Session, timeout: int = 30, max_retries: int = 3):
        """
        Initialize provider key resolver.

        Args:
            db: SQLAlchemy database session
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts for API calls (default: 3)
        """
        self.db = db
        self.timeout = timeout
        self.max_retries = max_retries
        self.config_service = LLMConfigService(db)

    def get_provider_for_user(
        self,
        user_id: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Get a configured provider instance for a user.

        This method resolves the correct API key (custom or system default)
        and returns a ready-to-use provider instance.

        Args:
            user_id: User ID (UUID as string)
            provider: Optional provider name (uses user's active provider if not specified)
            model: Optional model name (uses user's active model if not specified)

        Returns:
            Configured provider instance

        Raises:
            ProviderResolverError: If provider cannot be created
            LLMConfigError: If user configuration is invalid

        Example:
            ```python
            # Use user's active provider and model
            provider = resolver.get_provider_for_user(user_id="123e4567...")

            # Use specific provider (user's active model)
            provider = resolver.get_provider_for_user(
                user_id="123e4567...",
                provider="openai"
            )

            # Use specific provider and model
            provider = resolver.get_provider_for_user(
                user_id="123e4567...",
                provider="openai",
                model="gpt-4-turbo"
            )
            ```
        """
        try:
            # Get user's active configuration if provider not specified
            if not provider:
                config = self.config_service.get_user_config(user_id)
                provider = config["active_provider"]

            # Get API key for user (custom or system default)
            try:
                api_key = self.config_service.get_api_key_for_user(user_id, provider)
            except LLMConfigError as e:
                raise ProviderResolverError(
                    f"No API key available for provider '{provider}': {str(e)}"
                )

            # Create provider instance
            try:
                provider_instance = LLMProviderFactory.create_provider(
                    provider_name=provider,
                    api_key=api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
                return provider_instance

            except Exception as e:
                raise ProviderResolverError(
                    f"Failed to create provider '{provider}': {str(e)}"
                )

        except LLMConfigError:
            raise
        except Exception as e:
            raise ProviderResolverError(f"Provider resolution failed: {str(e)}")

    def optimize_text(
        self,
        user_id: str,
        text: str,
        mode: CorrectionMode,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Optimize text using user's LLM configuration.

        This is a convenience method that combines provider resolution
        and text optimization in a single call.

        Args:
            user_id: User ID (UUID as string)
            text: Text to optimize
            mode: Correction mode (accuracy or natural)
            provider: Optional provider name (uses user's active if not specified)
            model: Optional model name (uses user's active if not specified)
            **kwargs: Additional parameters passed to provider.optimize()

        Returns:
            OptimizationResult from provider

        Raises:
            ProviderResolverError: If provider resolution or optimization fails

        Example:
            ```python
            from providers import CorrectionMode

            result = resolver.optimize_text(
                user_id="123e4567...",
                text="He go to school yesterday.",
                mode=CorrectionMode.ACCURACY
            )

            print(result.optimized_text)  # "He went to school yesterday."
            print(result.processing_time_ms)  # 1234
            ```
        """
        try:
            # Get provider instance
            provider_instance = self.get_provider_for_user(user_id, provider, model)

            # Get model to use
            if not model:
                config = self.config_service.get_user_config(user_id)
                model = config["active_model"]

            # Optimize text
            result = provider_instance.optimize(
                text=text,
                mode=mode,
                model=model,
                **kwargs
            )

            return result

        except Exception as e:
            raise ProviderResolverError(f"Text optimization failed: {str(e)}")

    def test_user_provider(self, user_id: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Test API connectivity for a user's provider configuration.

        Args:
            user_id: User ID (UUID as string)
            provider: Optional provider name (uses user's active if not specified)

        Returns:
            Dictionary with test results:
            {
                "success": True,
                "provider": "zhipu",
                "using_custom_key": False,
                "message": "Connection successful"
            }

        Example:
            ```python
            result = resolver.test_user_provider(user_id="123e4567...")
            if result["success"]:
                print(f"Provider {result['provider']} is working")
            ```
        """
        try:
            # Get user's active provider if not specified
            if not provider:
                config = self.config_service.get_user_config(user_id)
                provider = config["active_provider"]
                using_custom_key = config["has_custom_key"]
            else:
                config = self.config_service.get_user_config(user_id)
                using_custom_key = (provider == config["active_provider"] and
                                   config["has_custom_key"])

            # Get provider instance
            provider_instance = self.get_provider_for_user(user_id, provider)

            # Test connection
            success = provider_instance.test_connection()

            return {
                "success": success,
                "provider": provider,
                "using_custom_key": using_custom_key,
                "message": "Connection successful" if success else "Connection failed"
            }

        except Exception as e:
            return {
                "success": False,
                "provider": provider or "unknown",
                "using_custom_key": False,
                "message": f"Test failed: {str(e)}"
            }

    def get_provider_info_for_user(
        self,
        user_id: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a user's provider configuration.

        Args:
            user_id: User ID (UUID as string)
            provider: Optional provider name (uses user's active if not specified)

        Returns:
            Dictionary with provider information

        Example:
            ```python
            info = resolver.get_provider_info_for_user(user_id="123e4567...")
            print(f"Provider: {info['display_name']}")
            print(f"Model: {info['model']}")
            print(f"Using custom key: {info['has_custom_key']}")
            ```
        """
        try:
            # Get user's active configuration
            config = self.config_service.get_user_config(user_id)

            # Use specified provider or active provider
            provider_name = provider or config["active_provider"]

            # Get provider info from factory
            provider_info = LLMProviderFactory.get_provider_info(provider_name)

            # Add user-specific information
            if provider_name == config["active_provider"]:
                provider_info["is_active"] = True
                provider_info["active_model"] = config["active_model"]
                provider_info["has_custom_key"] = config["has_custom_key"]
                provider_info["using_system_default"] = config["using_system_default"]
            else:
                # Check if user has config for this provider
                try:
                    api_key = self.config_service.get_api_key_for_user(user_id, provider_name)
                    provider_info["has_custom_key"] = True
                    provider_info["using_system_default"] = False
                except LLMConfigError:
                    provider_info["has_custom_key"] = False
                    provider_info["using_system_default"] = True
                provider_info["is_active"] = False
                provider_info["active_model"] = None

            return provider_info

        except Exception as e:
            raise ProviderResolverError(f"Failed to get provider info: {str(e)}")

    def switch_provider(
        self,
        user_id: str,
        new_provider: str,
        new_model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Switch user to a different provider.

        This is a convenience method that combines configuration update
        with validation.

        Args:
            user_id: User ID (UUID as string)
            new_provider: New provider name
            new_model: Optional new model name (uses provider's default if not specified)
            api_key: Optional custom API key for new provider

        Returns:
            Updated configuration dictionary

        Example:
            ```python
            # Switch to OpenAI with GPT-4 and custom key
            config = resolver.switch_provider(
                user_id="123e4567...",
                new_provider="openai",
                new_model="gpt-4",
                api_key="sk-1234567890"
            )

            # Switch to Zhipu AI with system default key
            config = resolver.switch_provider(
                user_id="123e4567...",
                new_provider="zhipu"
            )
            ```
        """
        try:
            # Validate provider is supported
            if not LLMProviderFactory.is_provider_supported(new_provider):
                raise ProviderResolverError(
                    f"Provider '{new_provider}' is not supported"
                )

            # Get provider's default model if not specified
            if not new_model:
                provider_info = LLMProviderFactory.get_provider_info(new_provider)
                for model in provider_info["models"]:
                    if model["is_default"]:
                        new_model = model["name"]
                        break
                if not new_model and provider_info["models"]:
                    new_model = provider_info["models"][0]["name"]

            # Update user configuration
            updated_config = self.config_service.update_user_config(
                user_id=user_id,
                provider=new_provider,
                model=new_model,
                api_key=api_key
            )

            return updated_config

        except LLMConfigError:
            raise
        except Exception as e:
            raise ProviderResolverError(f"Failed to switch provider: {str(e)}")
