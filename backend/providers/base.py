"""
Base LLM Provider interface.

This module defines the abstract base class that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class CorrectionMode(Enum):
    """Text correction modes."""

    ACCURACY = "accuracy"  # Fix grammatical errors only, preserve style
    NATURAL = "natural"    # Rewrite for naturalness


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class AuthenticationError(LLMProviderError):
    """Raised when API key authentication fails."""
    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded."""
    pass


class ModelNotFoundError(LLMProviderError):
    """Raised when specified model is not found."""
    pass


class InvalidRequestError(LLMProviderError):
    """Raised when request parameters are invalid."""
    pass


@dataclass
class OptimizationResult:
    """
    Result from LLM text optimization.

    Attributes:
        optimized_text: The optimized/corrected text
        corrections: List of corrections made
        explanation: Explanation of changes
        token_usage: Token usage statistics
        model: Model used for optimization
        processing_time_ms: Processing time in milliseconds
        metadata: Additional provider-specific metadata
    """

    optimized_text: str
    corrections: List[Dict[str, Any]]
    explanation: str
    token_usage: Dict[str, int]
    model: str
    processing_time_ms: int
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize default values."""
        if self.corrections is None:
            self.corrections = []
        if self.token_usage is None:
            self.token_usage = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ModelInfo:
    """
    Information about a supported model.

    Attributes:
        name: Internal model name (e.g., "glm-4-flashx", "gpt-4")
        display_name: Human-readable display name
        is_default: Whether this is the default model for the provider
        description: Description of model capabilities
        max_tokens: Maximum token limit (optional)
        cost_per_1k_tokens: Cost per 1000 tokens (optional)
    """

    name: str
    display_name: str
    is_default: bool = False
    description: str = ""
    max_tokens: Optional[int] = None
    cost_per_1k_tokens: Optional[float] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All concrete LLM providers (Zhipu AI, OpenAI, Anthropic) must implement
    this interface to ensure consistent behavior across providers.
    """

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get the provider name (e.g., "zhipu", "openai", "anthropic").

        Returns:
            Provider name as string
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Get the human-readable provider display name.

        Returns:
            Display name as string (e.g., "Zhipu AI", "OpenAI")
        """
        pass

    @abstractmethod
    def get_models(self) -> List[ModelInfo]:
        """
        Get list of supported models for this provider.

        Returns:
            List of ModelInfo objects describing available models
        """
        pass

    @abstractmethod
    def optimize(
        self,
        text: str,
        mode: CorrectionMode,
        model: Optional[str] = None,
        **kwargs
    ) -> OptimizationResult:
        """
        Optimize text using the LLM.

        Args:
            text: Text to optimize/correct
            mode: Correction mode (accuracy or natural)
            model: Specific model to use (uses default if None)
            **kwargs: Additional provider-specific parameters

        Returns:
            OptimizationResult containing optimized text and metadata

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            ModelNotFoundError: If specified model doesn't exist
            InvalidRequestError: If request parameters are invalid
            LLMProviderError: For other provider-specific errors
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the API connection with a minimal request.

        Returns:
            True if connection is successful, False otherwise

        Raises:
            AuthenticationError: If API key is invalid
            LLMProviderError: For other connection errors
        """
        pass

    def get_default_model(self) -> str:
        """
        Get the default model name for this provider.

        Returns:
            Default model name as string
        """
        models = self.get_models()
        for model in models:
            if model.is_default:
                return model.name

        # Fallback to first model if no default set
        if models:
            return models[0].name

        raise LLMProviderError(f"No models available for {self.provider_name}")

    def validate_model(self, model_name: str) -> bool:
        """
        Validate that a model name is supported by this provider.

        Args:
            model_name: Model name to validate

        Returns:
            True if model is supported, False otherwise
        """
        supported_models = [m.name for m in self.get_models()]
        return model_name in supported_models

    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(provider={self.provider_name})"
