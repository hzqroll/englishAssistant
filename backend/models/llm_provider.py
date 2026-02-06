"""
LLM Provider database models.

This module contains SQLAlchemy models for LLM provider configurations
and user LLM settings.
"""

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, UniqueConstraint, Index, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates, foreign
from datetime import datetime
import uuid

from .base import Base, TimestampMixin


class LLMProvider(Base, TimestampMixin):
    """
    LLM Provider model representing available LLM service providers.

    Stores system-level configurations for each supported LLM provider
    (Zhipu AI, OpenAI, Anthropic, etc.).

    Attributes:
        id: Unique provider identifier (UUID)
        name: Internal provider name (unique, e.g., "zhipu", "openai", "anthropic")
        display_name: Human-readable display name (e.g., "Zhipu AI", "OpenAI")
        is_enabled: Whether the provider is currently enabled
        default_api_key_encrypted: Fernet-encrypted system default API key
        supported_models: JSONB array of supported model configurations
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_configs: User configurations for this provider (one-to-many)
    """

    __tablename__ = "ea_llm_providers"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Provider identification
    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )  # "zhipu", "openai", "anthropic"

    display_name = Column(
        String(100),
        nullable=False
    )  # "Zhipu AI", "OpenAI", "Anthropic"

    # Provider status
    is_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # API key storage (encrypted at rest)
    default_api_key_encrypted = Column(
        Text,
        nullable=False
    )  # Fernet encrypted system default key

    # Supported models (JSONB for flexibility)
    # Format: [{"name": "glm-4-flashx", "display_name": "GLM-4-FlashX", "is_default": True}, ...]
    supported_models = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False
    )

    # Relationships
    user_configs = relationship(
        "UserLLMConfig",
        back_populates="provider",
        cascade="all, delete-orphan",
        lazy="dynamic",
        primaryjoin="LLMProvider.name == foreign(UserLLMConfig.provider_name)",
        foreign_keys="[UserLLMConfig.provider_name]"
    )

    # Indexes
    __table_args__ = (
        Index('ix_llm_providers_enabled', 'is_enabled'),
    )

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """
        Validate and normalize provider name.

        Args:
            key: Field name
            name: Provider name to validate

        Returns:
            Normalized provider name

        Raises:
            ValueError: If name is invalid
        """
        if not name or len(name) > 50:
            raise ValueError("Provider name must be 1-50 characters")
        return name.lower().strip()

    @validates('is_enabled')
    def validate_is_enabled(self, key: str, is_enabled: bool) -> bool:
        """
        Validate provider enabled status.

        Args:
            key: Field name
            is_enabled: Enabled status

        Returns:
            Validated boolean status
        """
        return bool(is_enabled)

    @validates('supported_models')
    def validate_supported_models(self, key: str, models: list) -> list:
        """
        Validate supported models configuration.

        Args:
            key: Field name
            models: List of model configurations

        Returns:
            Validated models list

        Raises:
            ValueError: If models configuration is invalid
        """
        if not isinstance(models, list) or len(models) == 0:
            raise ValueError("supported_models must be a non-empty list")

        for model in models:
            if not isinstance(model, dict):
                raise ValueError("Each model must be a dictionary")
            if 'name' not in model or 'display_name' not in model:
                raise ValueError("Each model must have 'name' and 'display_name' fields")

        return models


class UserLLMConfig(Base, TimestampMixin):
    """
    User LLM Configuration model for user-specific LLM provider settings.

    Stores user preferences and optional custom API keys for each provider.
    Each user can have one configuration per provider.

    Attributes:
        id: Unique configuration ID (UUID)
        user_id: User ID (foreign key to ea_users)
        provider_name: Provider name (e.g., "zhipu", "openai")
        selected_model: Selected model for this provider (e.g., "glm-4-flashx", "gpt-4")
        custom_api_key_encrypted: Optional Fernet-encrypted user-provided API key
        is_active: Whether this configuration is currently active
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user: Related User object
        provider: Related LLMProvider object
    """

    __tablename__ = "ea_user_llm_configs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ea_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Provider identification
    provider_name = Column(
        String(50),
        nullable=False
    )  # "zhipu", "openai", "anthropic"

    # Model selection
    selected_model = Column(
        String(100),
        nullable=False
    )  # "glm-4-flashx", "gpt-4", "claude-3-opus", etc.

    # Optional user-provided API key (encrypted)
    custom_api_key_encrypted = Column(
        Text,
        nullable=True
    )  # User's custom key, or None to use system default

    # Activation status
    is_active = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship(
        "User",
        backref="llm_configs"
    )
    provider = relationship(
        "LLMProvider",
        back_populates="user_configs",
        foreign_keys=[provider_name],
        primaryjoin="UserLLMConfig.provider_name == LLMProvider.name",
        uselist=False
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'provider_name', name='uq_user_provider'),
        Index('ix_user_llm_configs_user_active', 'user_id', 'is_active'),
        Index('ix_user_llm_configs_provider', 'provider_name'),
    )

    @validates('provider_name')
    def validate_provider_name(self, key: str, provider_name: str) -> str:
        """
        Validate and normalize provider name.

        Args:
            key: Field name
            provider_name: Provider name to validate

        Returns:
            Normalized provider name

        Raises:
            ValueError: If provider name is invalid
        """
        if not provider_name or len(provider_name) > 50:
            raise ValueError("Provider name must be 1-50 characters")
        return provider_name.lower().strip()

    @validates('selected_model')
    def validate_selected_model(self, key: str, model: str) -> str:
        """
        Validate selected model name.

        Args:
            key: Field name
            model: Model name to validate

        Returns:
            Validated model name

        Raises:
            ValueError: If model name is invalid
        """
        if not model or len(model) > 100:
            raise ValueError("Model name must be 1-100 characters")
        return model.strip()

    @property
    def has_custom_key(self) -> bool:
        """
        Check if user has provided a custom API key.

        Returns:
            True if user has a custom API key, False otherwise
        """
        return self.custom_api_key_encrypted is not None
