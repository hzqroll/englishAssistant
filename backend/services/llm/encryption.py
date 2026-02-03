"""
Encryption utilities for API key storage.

This module provides Fernet symmetric encryption for securely storing
API keys in the database.
"""

import os
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from base64 import urlsafe_b64encode

from core.config import settings


class EncryptionError(Exception):
    """Exception raised when encryption/decryption fails."""
    pass


def get_encryption_key() -> bytes:
    """
    Get encryption key from environment.

    Returns:
        Fernet encryption key as bytes

    Raises:
        EncryptionError: If encryption key cannot be retrieved or is invalid

    Note:
        The encryption key should be set in the ENCRYPTION_KEY environment variable.
        If not set, it will fall back to SECRET_KEY (not recommended for production).
    """
    # Try to get ENCRYPTION_KEY from environment
    encryption_key = os.getenv("ENCRYPTION_KEY")

    # Fallback to SECRET_KEY if ENCRYPTION_KEY not set
    if not encryption_key:
        encryption_key = settings.SECRET_KEY
        if not encryption_key:
            raise EncryptionError("No encryption key available in environment")

    # Convert to bytes if string
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode()

    # Ensure key is 32 bytes for Fernet
    if len(encryption_key) < 32:
        # Pad with zeros if too short
        encryption_key = encryption_key.ljust(32, b'0')
    elif len(encryption_key) > 32:
        # Truncate if too long
        encryption_key = encryption_key[:32]

    # Base64 encode for Fernet
    try:
        return urlsafe_b64encode(encryption_key)
    except Exception as e:
        raise EncryptionError(f"Failed to prepare encryption key: {str(e)}")


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage.

    Args:
        api_key: Plain text API key to encrypt

    Returns:
        Encrypted API key as base64-encoded string

    Raises:
        EncryptionError: If encryption fails
        ValueError: If api_key is empty

    Example:
        ```python
        encrypted = encrypt_api_key("sk-1234567890abcdef")
        # Returns: "gAAAAABl..."
        ```
    """
    if not api_key:
        raise ValueError("API key cannot be empty")

    if not isinstance(api_key, str):
        raise ValueError("API key must be a string")

    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = fernet.encrypt(api_key.encode())
        return encrypted_bytes.decode()
    except Exception as e:
        raise EncryptionError(f"Failed to encrypt API key: {str(e)}")


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    Decrypt an API key from storage.

    Args:
        encrypted_api_key: Encrypted API key (base64-encoded string)

    Returns:
        Decrypted plain text API key

    Raises:
        EncryptionError: If decryption fails
        ValueError: If encrypted_api_key is empty

    Example:
        ```python
        decrypted = decrypt_api_key("gAAAAABl...")
        # Returns: "sk-1234567890abcdef"
        ```
    """
    if not encrypted_api_key:
        raise ValueError("Encrypted API key cannot be empty")

    if not isinstance(encrypted_api_key, str):
        raise ValueError("Encrypted API key must be a string")

    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decrypted_bytes = fernet.decrypt(encrypted_api_key.encode())
        return decrypted_bytes.decode()
    except InvalidToken:
        raise EncryptionError("Invalid encrypted API key - decryption failed")
    except Exception as e:
        raise EncryptionError(f"Failed to decrypt API key: {str(e)}")


def validate_encryption_key() -> bool:
    """
    Validate that encryption is properly configured.

    Returns:
        True if encryption key is valid and can be used

    Example:
        ```python
        if validate_encryption_key():
            # Safe to use encryption
            encrypted = encrypt_api_key(api_key)
        ```
    """
    try:
        key = get_encryption_key()
        # Test encryption/decryption
        test_data = "test"
        fernet = Fernet(key)
        encrypted = fernet.encrypt(test_data.encode())
        decrypted = fernet.decrypt(encrypted).decode()
        return decrypted == test_data
    except Exception:
        return False


def is_encrypted(value: str) -> bool:
    """
    Check if a value appears to be encrypted.

    This is a heuristic check based on Fernet token format.

    Args:
        value: String to check

    Returns:
        True if value appears to be encrypted, False otherwise

    Example:
        ```python
        if is_encrypted(stored_key):
            api_key = decrypt_api_key(stored_key)
        else:
            api_key = stored_key  # Already plain text
        ```
    """
    if not value or not isinstance(value, str):
        return False

    # Fernet tokens start with "gAAAAA" when base64-encoded
    # This is a heuristic, not definitive
    return value.startswith("gAAAAA") and len(value) > 50


def safe_decrypt(encrypted_value: Optional[str], default: str = "") -> str:
    """
    Safely decrypt a value, returning default if decryption fails.

    Args:
        encrypted_value: Encrypted value to decrypt
        default: Default value to return on failure

    Returns:
        Decrypted value or default

    Example:
        ```python
        api_key = safe_decrypt(user_config.custom_api_key_encrypted, "")
        if not api_key:
            # Use system default
            api_key = safe_decrypt(provider.default_api_key_encrypted)
        ```
    """
    if not encrypted_value:
        return default

    try:
        return decrypt_api_key(encrypted_value)
    except (EncryptionError, ValueError):
        return default
