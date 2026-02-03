"""
Anthropic LLM Provider implementation.

This module provides the concrete implementation of BaseLLMProvider for Anthropic,
supporting Claude-3-Opus, Claude-3-Sonnet, and Claude-3-Haiku models.
"""

import time
from typing import List, Optional, Dict, Any
import anthropic
from anthropic import Anthropic

from .base import (
    BaseLLMProvider,
    CorrectionMode,
    OptimizationResult,
    ModelInfo,
    LLMProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    InvalidRequestError,
)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic LLM provider implementation.

    Supports Claude-3 model series:
    - Claude-3 Opus: Most powerful model for complex reasoning (default)
    - Claude-3 Sonnet: Balanced model for most tasks
    - Claude-3 Haiku: Fastest model for simple tasks
    """

    # Supported models configuration
    MODELS = [
        ModelInfo(
            name="claude-3-opus-20240229",
            display_name="Claude 3 Opus",
            is_default=True,
            description="Most powerful model for complex reasoning",
            max_tokens=4096,
            cost_per_1k_tokens=0.015,  # $0.015/1K tokens (input)
        ),
        ModelInfo(
            name="claude-3-sonnet-20240229",
            display_name="Claude 3 Sonnet",
            is_default=False,
            description="Balanced model for most tasks",
            max_tokens=4096,
            cost_per_1k_tokens=0.003,  # $0.003/1K tokens (input)
        ),
        ModelInfo(
            name="claude-3-haiku-20240307",
            display_name="Claude 3 Haiku",
            is_default=False,
            description="Fastest model for simple tasks",
            max_tokens=4096,
            cost_per_1k_tokens=0.00025,  # $0.00025/1K tokens (input)
        ),
    ]

    # Model aliases for backwards compatibility
    MODEL_ALIASES = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-opus-20240229": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-sonnet-20240229": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-3-haiku-20240307": "claude-3-haiku-20240307",
    }

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Raises:
            ValueError: If api_key is empty
            AuthenticationError: If API key initialization fails
        """
        super().__init__(api_key, timeout, max_retries)

        try:
            self._client = Anthropic(api_key=api_key, timeout=timeout)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Anthropic client: {str(e)}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"

    @property
    def display_name(self) -> str:
        """Get provider display name."""
        return "Anthropic"

    def get_models(self) -> List[ModelInfo]:
        """Get list of supported models."""
        return self.MODELS.copy()

    def optimize(
        self,
        text: str,
        mode: CorrectionMode,
        model: Optional[str] = None,
        **kwargs
    ) -> OptimizationResult:
        """
        Optimize text using Anthropic Claude.

        Args:
            text: Text to optimize/correct
            mode: Correction mode (accuracy or natural)
            model: Specific model to use (uses default if None)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            OptimizationResult with optimized text and metadata

        Raises:
            ModelNotFoundError: If specified model is not supported
            InvalidRequestError: If text is empty or invalid
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            LLMProviderError: For other errors
        """
        if not text or not text.strip():
            raise InvalidRequestError("Input text cannot be empty")

        # Determine which model to use
        model_name = model or self.get_default_model()
        model_name = self.MODEL_ALIASES.get(model_name, model_name)

        if not self.validate_model(model_name):
            raise ModelNotFoundError(f"Model '{model_name}' not supported by {self.display_name}")

        start_time = time.time()

        try:
            # Build prompt based on correction mode
            prompt = self._build_prompt(text, mode)

            # Get additional parameters
            temperature = kwargs.get("temperature", 0.3 if mode == CorrectionMode.ACCURACY else 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)

            # Make API call with retry logic
            response = self._call_api_with_retry(
                model=model_name,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract optimized text
            optimized_text = response.content[0].text.strip()

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Extract token usage
            token_usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            return OptimizationResult(
                optimized_text=optimized_text,
                corrections=self._extract_corrections(text, optimized_text, mode),
                explanation="Text optimized using Anthropic Claude",
                token_usage=token_usage,
                model=model_name,
                processing_time_ms=processing_time_ms,
                metadata={
                    "provider": self.provider_name,
                    "mode": mode.value,
                    "temperature": temperature,
                },
            )

        except AuthenticationError as e:
            raise
        except RateLimitError as e:
            raise
        except ModelNotFoundError as e:
            raise
        except InvalidRequestError as e:
            raise
        except Exception as e:
            raise LLMProviderError(f"Optimization failed: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test the API connection with a minimal request.

        Returns:
            True if connection is successful

        Raises:
            AuthenticationError: If API key is invalid
            LLMProviderError: For other connection errors
        """
        try:
            response = self._client.messages.create(
                model=self.get_default_model(),
                max_tokens=5,
                messages=[
                    {"role": "user", "content": "Hello"},
                ],
            )
            return bool(response.content)
        except anthropic.AuthenticationError as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
        except Exception as e:
            raise LLMProviderError(f"Connection test failed: {str(e)}")

    def _get_system_prompt(self, mode: CorrectionMode) -> str:
        """
        Get system prompt based on correction mode.

        Args:
            mode: Correction mode

        Returns:
            System prompt string
        """
        if mode == CorrectionMode.ACCURACY:
            return "You are an expert English grammar and spelling editor. Fix only grammatical errors, preserve the original style and structure."
        else:
            return "You are an expert English editor. Improve the naturalness and flow of the text while preserving the original meaning."

    def _build_prompt(self, text: str, mode: CorrectionMode) -> str:
        """
        Build user prompt for text optimization.

        Args:
            text: Input text
            mode: Correction mode

        Returns:
            Formatted prompt string
        """
        if mode == CorrectionMode.ACCURACY:
            return f"""Fix grammatical and spelling errors in the following English text.

Guidelines:
1. Fix only grammatical, spelling, and punctuation errors
2. Preserve the original wording, style, and structure
3. Return ONLY the corrected text, no explanations

Text: "{text}"

Corrected text:"""
        else:  # NATURAL mode
            return f"""Improve the naturalness and flow of this English text while preserving the original meaning.

Guidelines:
1. Improve sentence flow and word choice for natural expression
2. Maintain the original tone and style
3. Return ONLY the improved text, no explanations

Text: "{text}"

Improved text:"""

    def _call_api_with_retry(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> Any:
        """
        Call Anthropic API with retry logic.

        Args:
            model: Model name
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            API response

        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            LLMProviderError: For other errors
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self._client.messages.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response

            except anthropic.AuthenticationError as e:
                raise AuthenticationError(f"Authentication failed: {str(e)}")

            except anthropic.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")

            except anthropic.APIError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue

        # All retries exhausted
        raise LLMProviderError(f"API call failed after {self.max_retries} attempts: {str(last_error)}")

    def _extract_corrections(
        self,
        original: str,
        optimized: str,
        mode: CorrectionMode
    ) -> List[Dict[str, Any]]:
        """
        Extract corrections made by comparing original and optimized text.

        This is a simplified implementation. A more sophisticated version would
        use diff algorithms to identify specific changes.

        Args:
            original: Original text
            optimized: Optimized text
            mode: Correction mode used

        Returns:
            List of correction dictionaries
        """
        # Simple comparison - mark as changed if text is different
        if original == optimized:
            return []

        return [{
            "type": mode.value,
            "original": original,
            "optimized": optimized,
            "description": f"Text optimized in {mode.value} mode",
        }]
