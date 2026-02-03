"""
LLM Configuration Service Package.

This package provides services for managing LLM provider configurations,
API key encryption, and user preferences.
"""

from .encryption import (
    encrypt_api_key,
    decrypt_api_key,
    get_encryption_key,
    validate_encryption_key,
    is_encrypted,
    safe_decrypt,
    EncryptionError,
)
from .config_service import (
    LLMConfigService,
    LLMConfigError,
    ProviderNotFoundError,
    UserNotFoundError,
    ConfigurationError,
)
from .provider_resolver import (
    ProviderKeyResolver,
    ProviderResolverError,
)
from .validation import (
    ConfigValidator,
    ValidationError,
)

__all__ = [
    # Encryption utilities
    "encrypt_api_key",
    "decrypt_api_key",
    "get_encryption_key",
    "validate_encryption_key",
    "is_encrypted",
    "safe_decrypt",
    "EncryptionError",
    # Configuration service
    "LLMConfigService",
    "LLMConfigError",
    "ProviderNotFoundError",
    "UserNotFoundError",
    "ConfigurationError",
    # Provider resolver
    "ProviderKeyResolver",
    "ProviderResolverError",
    # Validation
    "ConfigValidator",
    "ValidationError",
]
