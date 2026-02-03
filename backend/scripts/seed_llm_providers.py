"""
Seed script for LLM provider configurations.

This script initializes the database with system default LLM providers
and their supported models. It encrypts API keys using Fernet encryption
before storing them in the database.

Usage:
    poetry run python scripts/seed_llm_providers.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from cryptography.fernet import Fernet

from core.config import settings
from models.session import SessionLocal
from models.llm_provider import LLMProvider


def get_encryption_key() -> bytes:
    """
    Get encryption key from environment or generate a warning.

    Returns:
        Fernet encryption key as bytes

    Raises:
        ValueError: If ENCRYPTION_KEY is not set
    """
    # Check for ENCRYPTION_KEY environment variable
    encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)

    if not encryption_key:
        print("⚠️  WARNING: ENCRYPTION_KEY not set in environment")
        print("   Using SECRET_KEY as fallback (not recommended for production)")
        encryption_key = settings.SECRET_KEY.encode()

    # Ensure key is 32 bytes for Fernet
    if len(encryption_key) < 32:
        encryption_key = encryption_key.ljust(32, b'0')
    elif len(encryption_key) > 32:
        encryption_key = encryption_key[:32]

    # Base64 encode for Fernet
    from base64 import urlsafe_b64encode
    return urlsafe_b64encode(encryption_key)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt API key using Fernet encryption.

    Args:
        api_key: Plain text API key

    Returns:
        Encrypted API key as string
    """
    if not api_key:
        return ""

    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def seed_llm_providers():
    """
    Seed database with default LLM providers.

    Creates or updates:
    - Zhipu AI (glm-4-flashx, glm-4-flash, glm-4-plus, glm-4-air)
    - OpenAI (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
    - Anthropic (claude-3-opus, claude-3-sonnet, claude-3-haiku)
    """
    print("🌱 Starting LLM provider seeding...")

    session = SessionLocal()

    try:
        # Check existing providers
        existing_providers = {provider.name: provider for provider in session.query(LLMProvider).all()}

        providers_data = [
            {
                "name": "zhipu",
                "display_name": "Zhipu AI",
                "is_enabled": True,
                "default_api_key_encrypted": encrypt_api_key(settings.ZHIPUAI_API_KEY),
                "supported_models": [
                    {
                        "name": "glm-4-flashx",
                        "display_name": "GLM-4-FlashX",
                        "is_default": True,
                        "description": "Fastest model with excellent quality"
                    },
                    {
                        "name": "glm-4-flash",
                        "display_name": "GLM-4-Flash",
                        "is_default": False,
                        "description": "Fast and cost-effective model"
                    },
                    {
                        "name": "glm-4-plus",
                        "display_name": "GLM-4-Plus",
                        "is_default": False,
                        "description": "Balanced performance and speed"
                    },
                    {
                        "name": "glm-4-air",
                        "display_name": "GLM-4-Air",
                        "is_default": False,
                        "description": "Lightweight model for simple tasks"
                    }
                ]
            },
            {
                "name": "openai",
                "display_name": "OpenAI",
                "is_enabled": True,
                "default_api_key_encrypted": "",  # No system default, users must provide
                "supported_models": [
                    {
                        "name": "gpt-4",
                        "display_name": "GPT-4",
                        "is_default": True,
                        "description": "Most capable model for complex tasks"
                    },
                    {
                        "name": "gpt-4-turbo",
                        "display_name": "GPT-4 Turbo",
                        "is_default": False,
                        "description": "Faster variant of GPT-4"
                    },
                    {
                        "name": "gpt-3.5-turbo",
                        "display_name": "GPT-3.5 Turbo",
                        "is_default": False,
                        "description": "Fast and cost-effective model"
                    }
                ]
            },
            {
                "name": "anthropic",
                "display_name": "Anthropic",
                "is_enabled": True,
                "default_api_key_encrypted": "",  # No system default, users must provide
                "supported_models": [
                    {
                        "name": "claude-3-opus-20240229",
                        "display_name": "Claude 3 Opus",
                        "is_default": True,
                        "description": "Most powerful model for complex reasoning"
                    },
                    {
                        "name": "claude-3-sonnet-20240229",
                        "display_name": "Claude 3 Sonnet",
                        "is_default": False,
                        "description": "Balanced model for most tasks"
                    },
                    {
                        "name": "claude-3-haiku-20240307",
                        "display_name": "Claude 3 Haiku",
                        "is_default": False,
                        "description": "Fastest model for simple tasks"
                    }
                ]
            }
        ]

        for provider_data in providers_data:
            name = provider_data["name"]

            if name in existing_providers:
                # Update existing provider
                provider = existing_providers[name]
                provider.display_name = provider_data["display_name"]
                provider.is_enabled = provider_data["is_enabled"]
                provider.default_api_key_encrypted = provider_data["default_api_key_encrypted"]
                provider.supported_models = provider_data["supported_models"]
                print(f"  ✓ Updated provider: {provider_data['display_name']}")
            else:
                # Create new provider
                provider = LLMProvider(**provider_data)
                session.add(provider)
                print(f"  + Created provider: {provider_data['display_name']}")

        session.commit()
        print("\n✅ LLM provider seeding completed successfully!")
        print(f"\nSummary:")
        print(f"  - Total providers: {len(providers_data)}")
        print(f"  - Zhipu AI: {len(providers_data[0]['supported_models'])} models")
        print(f"  - OpenAI: {len(providers_data[1]['supported_models'])} models")
        print(f"  - Anthropic: {len(providers_data[2]['supported_models'])} models")

    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def main():
    """Main entry point for the seed script."""
    try:
        seed_llm_providers()
    except Exception as e:
        print(f"\n❌ Error seeding providers: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
