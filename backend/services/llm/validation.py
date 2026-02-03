"""
Configuration Validation Utilities.

This module provides validation utilities for LLM configurations,
including provider names, model names, and API key validation.
"""

from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session

from models.llm_provider import LLMProvider
from providers import LLMProviderFactory, BaseLLMProvider, AuthenticationError, LLMProviderError


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


class ConfigValidator:
    """
    Validator for LLM configurations.

    Provides methods to validate provider names, model names, API keys,
    and complete configurations before saving to database.

    Example:
        ```python
        validator = ConfigValidator(db)

        # Validate provider name
        if validator.validate_provider_name("zhipu"):
            print("Provider is valid")

        # Validate model for provider
        if validator.validate_model_for_provider("zhipu", "glm-4-flashx"):
            print("Model is valid for this provider")

        # Validate API key by testing connectivity
        result = validator.validate_api_key("zhipu", "your-api-key")
        if result["valid"]:
            print("API key is working!")
        ```
    """

    def __init__(self, db: Session):
        """
        Initialize configuration validator.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def validate_provider_name(self, provider_name: str) -> bool:
        """
        Validate that a provider name is supported and enabled.

        Args:
            provider_name: Provider name to validate

        Returns:
            True if provider is valid and enabled, False otherwise

        Example:
            ```python
            if validator.validate_provider_name("zhipu"):
                # Provider is valid
                pass
            ```
        """
        if not provider_name or not isinstance(provider_name, str):
            return False

        # Check if provider is registered in factory
        if not LLMProviderFactory.is_provider_supported(provider_name):
            return False

        # Check if provider is enabled in database
        provider = self.db.query(LLMProvider).filter(
            LLMProvider.name == provider_name,
            LLMProvider.is_enabled == True
        ).first()

        return provider is not None

    def validate_model_for_provider(self, provider_name: str, model_name: str) -> bool:
        """
        Validate that a model is supported by a specific provider.

        Args:
            provider_name: Provider name
            model_name: Model name to validate

        Returns:
            True if model is supported by provider, False otherwise

        Example:
            ```python
            if validator.validate_model_for_provider("zhipu", "glm-4-flashx"):
                # Model is valid for Zhipu AI
                pass
            ```
        """
        if not provider_name or not model_name:
            return False

        try:
            # Get provider info from database
            provider = self.db.query(LLMProvider).filter(
                LLMProvider.name == provider_name
            ).first()

            if not provider:
                return False

            # Check if model is in supported models
            supported_models = [m.get("name") for m in provider.supported_models]
            return model_name in supported_models

        except Exception:
            return False

    def validate_api_key(
        self,
        provider_name: str,
        api_key: str,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Validate an API key by testing connectivity.

        This makes an actual API call to verify the key is valid.

        Args:
            provider_name: Provider name
            api_key: API key to validate
            timeout: Request timeout in seconds (default: 10)

        Returns:
            Dictionary with validation results:
            {
                "valid": True,
                "provider": "zhipu",
                "message": "API key is valid",
                "error": None
            }

        Example:
            ```python
            result = validator.validate_api_key("openai", "sk-1234567890")
            if result["valid"]:
                print("✅ API key is valid")
            else:
                print(f"❌ {result['message']}")
            ```
        """
        # Basic validation
        if not api_key or not isinstance(api_key, str):
            return {
                "valid": False,
                "provider": provider_name,
                "message": "API key cannot be empty",
                "error": "EMPTY_KEY"
            }

        if len(api_key.strip()) < 10:
            return {
                "valid": False,
                "provider": provider_name,
                "message": "API key is too short",
                "error": "INVALID_FORMAT"
            }

        # Validate provider
        if not self.validate_provider_name(provider_name):
            return {
                "valid": False,
                "provider": provider_name,
                "message": f"Provider '{provider_name}' is not supported or enabled",
                "error": "INVALID_PROVIDER"
            }

        # Test API connectivity
        try:
            provider_instance = LLMProviderFactory.create_provider(
                provider_name=provider_name,
                api_key=api_key,
                timeout=timeout,
                max_retries=1
            )

            # Test connection
            success = provider_instance.test_connection()

            if success:
                return {
                    "valid": True,
                    "provider": provider_name,
                    "message": "API key is valid",
                    "error": None
                }
            else:
                return {
                    "valid": False,
                    "provider": provider_name,
                    "message": "API connection test failed",
                    "error": "CONNECTION_FAILED"
                }

        except AuthenticationError as e:
            return {
                "valid": False,
                "provider": provider_name,
                "message": f"Authentication failed: {str(e)}",
                "error": "AUTHENTICATION_FAILED"
            }
        except Exception as e:
            return {
                "valid": False,
                "provider": provider_name,
                "message": f"Validation error: {str(e)}",
                "error": "VALIDATION_ERROR"
            }

    def validate_configuration(
        self,
        provider_name: str,
        model_name: str,
        api_key: Optional[str] = None,
        test_api_key: bool = False
    ) -> Dict[str, Any]:
        """
        Validate a complete LLM configuration.

        Args:
            provider_name: Provider name
            model_name: Model name
            api_key: Optional API key (if provided, will be validated)
            test_api_key: Whether to test API key connectivity (default: False)

        Returns:
            Dictionary with validation results:
            {
                "valid": True,
                "errors": [],
                "warnings": [],
                "provider": "zhipu",
                "model": "glm-4-flashx",
                "api_key_valid": True  # Only if api_key provided
            }

        Example:
            ```python
            result = validator.validate_configuration(
                provider_name="zhipu",
                model_name="glm-4-flashx",
                api_key="your-api-key",
                test_api_key=True
            )

            if result["valid"]:
                # Configuration is valid
                save_to_database()
            else:
                # Show errors
                for error in result["errors"]:
                    print(f"Error: {error}")
            ```
        """
        errors = []
        warnings = []

        # Validate provider name
        if not self.validate_provider_name(provider_name):
            errors.append(f"Provider '{provider_name}' is not supported or enabled")

        # Validate model for provider
        if not self.validate_model_for_provider(provider_name, model_name):
            errors.append(
                f"Model '{model_name}' is not supported by provider '{provider_name}'"
            )

        # Validate API key if provided
        api_key_valid = None
        if api_key:
            if test_api_key:
                key_result = self.validate_api_key(provider_name, api_key)
                api_key_valid = key_result["valid"]
                if not key_result["valid"]:
                    errors.append(f"API key validation failed: {key_result['message']}")
            else:
                # Basic validation only
                if len(api_key.strip()) < 10:
                    warnings.append("API key seems too short (not tested)")

        # Build result
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "provider": provider_name,
            "model": model_name,
            "api_key_valid": api_key_valid
        }

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of available providers with their models.

        Returns:
            List of provider information dictionaries

        Example:
            ```python
            providers = validator.get_available_providers()
            for provider in providers:
                print(f"{provider['display_name']}:")
                for model in provider['models']:
                    print(f"  - {model['display_name']}")
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
                    "has_system_default_key": bool(p.default_api_key_encrypted)
                }
                for p in providers
            ]
        except Exception:
            return []

    def get_models_for_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        """
        Get list of models supported by a provider.

        Args:
            provider_name: Provider name

        Returns:
            List of model information dictionaries

        Example:
            ```python
            models = validator.get_models_for_provider("zhipu")
            for model in models:
                print(f"{model['display_name']}: {model['description']}")
            ```
        """
        try:
            provider = self.db.query(LLMProvider).filter(
                LLMProvider.name == provider_name
            ).first()

            if not provider:
                return []

            return provider.supported_models

        except Exception:
            return []

    def validate_batch_configurations(
        self,
        configurations: List[Dict[str, Any]],
        test_api_keys: bool = False
    ) -> Dict[str, Any]:
        """
        Validate multiple configurations at once.

        Args:
            configurations: List of configuration dictionaries
            test_api_keys: Whether to test API key connectivity

        Returns:
            Dictionary with batch validation results

        Example:
            ```python
            configs = [
                {"provider": "zhipu", "model": "glm-4-flashx", "api_key": "key1"},
                {"provider": "openai", "model": "gpt-4", "api_key": "key2"}
            ]

            result = validator.validate_batch_configurations(configs)
            print(f"Valid: {result['valid_count']}/{result['total_count']}")
            ```
        """
        results = []
        valid_count = 0

        for config in configurations:
            result = self.validate_configuration(
                provider_name=config.get("provider", ""),
                model_name=config.get("model", ""),
                api_key=config.get("api_key"),
                test_api_key=test_api_keys
            )
            results.append(result)
            if result["valid"]:
                valid_count += 1

        return {
            "total_count": len(configurations),
            "valid_count": valid_count,
            "invalid_count": len(configurations) - valid_count,
            "results": results,
            "all_valid": valid_count == len(configurations)
        }

    def get_validation_summary(self, provider_name: str, model_name: str) -> str:
        """
        Get a human-readable validation summary.

        Args:
            provider_name: Provider name
            model_name: Model name

        Returns:
            Human-readable validation summary string

        Example:
            ```python
            summary = validator.get_validation_summary("zhipu", "glm-4-flashx")
            print(summary)
            # Output: "✅ Zhipu AI with GLM-4-FlashX is valid"
            ```
        """
        provider_valid = self.validate_provider_name(provider_name)
        model_valid = self.validate_model_for_provider(provider_name, model_name)

        if provider_valid and model_valid:
            provider_info = LLMProviderFactory.get_provider_display_name(provider_name)
            models = self.get_models_for_provider(provider_name)
            model_display = model_name
            for m in models:
                if m.get("name") == model_name:
                    model_display = m.get("display_name", model_name)
                    break
            return f"✅ {provider_info} with {model_display} is valid"
        elif not provider_valid:
            return f"❌ Provider '{provider_name}' is not supported or enabled"
        else:
            return f"❌ Model '{model_name}' is not supported by provider '{provider_name}'"
