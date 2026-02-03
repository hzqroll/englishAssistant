"""
LLM Provider Factory.

This module provides a factory for creating LLM provider instances.
It centralizes provider registration and instantiation logic.
"""

from typing import Dict, Type, List, Optional
from .base import BaseLLMProvider, LLMProviderError
from .zhipu_provider import ZhipuProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.

    This factory manages provider registration and instantiation,
    providing a centralized way to create providers by name.

    Example:
        ```python
        # Create a provider
        provider = LLMProviderFactory.create_provider(
            provider_name="zhipu",
            api_key="your-api-key"
        )

        # Get available providers
        providers = LLMProviderFactory.get_available_providers()
        # Returns: ["zhipu", "openai", "anthropic"]

        # Check if provider is supported
        is_supported = LLMProviderFactory.is_provider_supported("zhipu")
        # Returns: True
        ```
    """

    # Registry of available providers
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "zhipu": ZhipuProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
    }

    # Provider display names
    _display_names: Dict[str, str] = {
        "zhipu": "Zhipu AI",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "gemini": "Google Gemini",
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Name of the provider ("zhipu", "openai", "anthropic")
            api_key: API key for authentication
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)

        Returns:
            Instantiated provider instance

        Raises:
            LLMProviderError: If provider name is not supported
            ValueError: If api_key is empty
            AuthenticationError: If provider initialization fails

        Example:
            ```python
            provider = LLMProviderFactory.create_provider(
                provider_name="zhipu",
                api_key="your-zhipu-api-key"
            )

            result = provider.optimize(
                text="He go to school.",
                mode=CorrectionMode.ACCURACY
            )
            ```
        """
        provider_name = provider_name.lower().strip()

        if not cls.is_provider_supported(provider_name):
            available = ", ".join(cls.get_available_providers())
            raise LLMProviderError(
                f"Provider '{provider_name}' is not supported. "
                f"Available providers: {available}"
            )

        if not api_key:
            raise ValueError(f"API key cannot be empty for provider '{provider_name}'")

        provider_class = cls._providers[provider_name]

        try:
            return provider_class(
                api_key=api_key,
                timeout=timeout,
                max_retries=max_retries,
            )
        except Exception as e:
            raise LLMProviderError(
                f"Failed to create provider '{provider_name}': {str(e)}"
            ) from e

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available provider names.

        Returns:
            List of provider names as strings

        Example:
            ```python
            providers = LLMProviderFactory.get_available_providers()
            # Returns: ["zhipu", "openai", "anthropic"]
            ```
        """
        return list(cls._providers.keys())

    @classmethod
    def is_provider_supported(cls, provider_name: str) -> bool:
        """
        Check if a provider is supported.

        Args:
            provider_name: Name of the provider to check

        Returns:
            True if provider is supported, False otherwise

        Example:
            ```python
            if LLMProviderFactory.is_provider_supported("zhipu"):
                provider = LLMProviderFactory.create_provider("zhipu", api_key)
            ```
        """
        return provider_name.lower().strip() in cls._providers

    @classmethod
    def get_provider_display_name(cls, provider_name: str) -> Optional[str]:
        """
        Get human-readable display name for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Display name or None if provider not found

        Example:
            ```python
            display_name = LLMProviderFactory.get_provider_display_name("zhipu")
            # Returns: "Zhipu AI"
            ```
        """
        return cls._display_names.get(provider_name.lower().strip())

    @classmethod
    def get_provider_info(cls, provider_name: str) -> Dict[str, any]:
        """
        Get information about a provider including supported models.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary containing provider information

        Raises:
            LLMProviderError: If provider is not supported

        Example:
            ```python
            info = LLMProviderFactory.get_provider_info("zhipu")
            # Returns:
            # {
            #     "name": "zhipu",
            #     "display_name": "Zhipu AI",
            #     "models": [
            #         {"name": "glm-4-flashx", "display_name": "GLM-4-FlashX", ...},
            #         ...
            #     ]
            # }
            ```
        """
        provider_name = provider_name.lower().strip()

        if not cls.is_provider_supported(provider_name):
            raise LLMProviderError(f"Provider '{provider_name}' is not supported")

        provider_class = cls._providers[provider_name]

        # Create temporary instance to get models (uses empty key just for info)
        # Note: This won't actually initialize the client, just get model metadata
        try:
            # Get models from class attribute if available
            if hasattr(provider_class, 'MODELS'):
                models = [
                    {
                        "name": model.name,
                        "display_name": model.display_name,
                        "is_default": model.is_default,
                        "description": model.description,
                        "max_tokens": model.max_tokens,
                        "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    }
                    for model in provider_class.MODELS
                ]
            else:
                models = []

            return {
                "name": provider_name,
                "display_name": cls._display_names.get(provider_name, provider_name),
                "models": models,
            }
        except Exception as e:
            raise LLMProviderError(
                f"Failed to get provider info for '{provider_name}': {str(e)}"
            ) from e

    @classmethod
    def register_provider(
        cls,
        provider_name: str,
        provider_class: Type[BaseLLMProvider],
        display_name: Optional[str] = None,
    ) -> None:
        """
        Register a custom provider.

        This allows extending the factory with custom provider implementations.

        Args:
            provider_name: Unique name for the provider
            provider_class: Provider class (must inherit from BaseLLMProvider)
            display_name: Human-readable display name (optional)

        Raises:
            ValueError: If provider_class doesn't inherit from BaseLLMProvider
            LLMProviderError: If provider name already exists

        Example:
            ```python
            class CustomProvider(BaseLLMProvider):
                # ... implementation ...
                pass

            LLMProviderFactory.register_provider(
                provider_name="custom",
                provider_class=CustomProvider,
                display_name="Custom LLM Provider"
            )
            ```
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError(
                f"provider_class must inherit from BaseLLMProvider, "
                f"got {provider_class.__name__}"
            )

        provider_name = provider_name.lower().strip()

        if provider_name in cls._providers:
            raise LLMProviderError(
                f"Provider '{provider_name}' is already registered"
            )

        cls._providers[provider_name] = provider_class
        cls._display_names[provider_name] = display_name or provider_name.title()

    @classmethod
    def unregister_provider(cls, provider_name: str) -> None:
        """
        Unregister a provider.

        Args:
            provider_name: Name of the provider to unregister

        Raises:
            LLMProviderError: If provider is not registered

        Example:
            ```python
            LLMProviderFactory.unregister_provider("custom")
            ```
        """
        provider_name = provider_name.lower().strip()

        if provider_name not in cls._providers:
            raise LLMProviderError(
                f"Provider '{provider_name}' is not registered"
            )

        del cls._providers[provider_name]
        if provider_name in cls._display_names:
            del cls._display_names[provider_name]

    @classmethod
    def get_all_providers_info(cls) -> List[Dict[str, any]]:
        """
        Get information about all registered providers.

        Returns:
            List of provider information dictionaries

        Example:
            ```python
            all_providers = LLMProviderFactory.get_all_providers_info()
            for provider in all_providers:
                print(f"{provider['display_name']}: {len(provider['models'])} models")
            ```
        """
        return [
            cls.get_provider_info(provider_name)
            for provider_name in cls.get_available_providers()
        ]
