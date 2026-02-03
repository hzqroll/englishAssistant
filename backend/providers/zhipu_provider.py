"""
Zhipu AI LLM Provider implementation.

This module provides the concrete implementation of BaseLLMProvider for Zhipu AI,
supporting GLM-4-FlashX, GLM-4-Flash, GLM-4-Plus, and GLM-4-Air models.
"""

import time
from typing import List, Optional, Dict, Any
from zhipuai import ZhipuAI

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


class ZhipuProvider(BaseLLMProvider):
    """
    Zhipu AI LLM provider implementation.

    Supports GLM-4 model series:
    - GLM-4-FlashX: Fastest model with excellent quality (default)
    - GLM-4-Flash: Fast and cost-effective
    - GLM-4-Plus: Balanced performance and speed
    - GLM-4-Air: Lightweight model for simple tasks
    """

    # Supported models configuration
    MODELS = [
        ModelInfo(
            name="glm-4-flashx",
            display_name="GLM-4-FlashX",
            is_default=True,
            description="Fastest model with excellent quality",
            max_tokens=8192,
            cost_per_1k_tokens=0.0001,
        ),
        ModelInfo(
            name="glm-4-flash",
            display_name="GLM-4-Flash",
            is_default=False,
            description="Fast and cost-effective model",
            max_tokens=8192,
            cost_per_1k_tokens=0.0001,
        ),
        ModelInfo(
            name="glm-4-plus",
            display_name="GLM-4-Plus",
            is_default=False,
            description="Balanced performance and speed",
            max_tokens=128000,
            cost_per_1k_tokens=0.0005,
        ),
        ModelInfo(
            name="glm-4-air",
            display_name="GLM-4-Air",
            is_default=False,
            description="Lightweight model for simple tasks",
            max_tokens=128000,
            cost_per_1k_tokens=0.0001,
        ),
    ]

    # Model aliases for backwards compatibility
    MODEL_ALIASES = {
        "glm-4-flashx": "glm-4-flashx",
        "glm-4-flash": "glm-4-flash",
        "glm-4-plus": "glm-4-plus",
        "glm-4-air": "glm-4-air",
    }

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize Zhipu AI provider.

        Args:
            api_key: Zhipu AI API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Raises:
            ValueError: If api_key is empty
            AuthenticationError: If API key initialization fails
        """
        super().__init__(api_key, timeout, max_retries)

        try:
            self._client = ZhipuAI(api_key=api_key)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Zhipu AI client: {str(e)}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "zhipu"

    @property
    def display_name(self) -> str:
        """Get provider display name."""
        return "Zhipu AI"

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
        Optimize text using Zhipu AI.

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
                messages=[
                    {"role": "system", "content": self._get_system_prompt(mode)},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract optimized text
            optimized_text = response.choices[0].message.content.strip()

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Extract token usage
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return OptimizationResult(
                optimized_text=optimized_text,
                corrections=self._extract_corrections(text, optimized_text, mode),
                explanation="Text optimized using Zhipu AI",
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
            response = self._client.chat.completions.create(
                model=self.get_default_model(),
                messages=[
                    {"role": "user", "content": "Hello"},
                ],
                max_tokens=5,
            )
            return bool(response.choices)
        except Exception as e:
            error_msg = str(e).lower()
            if "auth" in error_msg or "key" in error_msg or "401" in error_msg:
                raise AuthenticationError(f"Authentication failed: {str(e)}")
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
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Any:
        """
        Call Zhipu AI API with retry logic.

        Args:
            model: Model name
            messages: Message list
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
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )
                return response

            except Exception as e:
                last_error = e
                error_msg = str(e).lower()

                # Check for authentication errors
                if "auth" in error_msg or "key" in error_msg or "401" in error_msg:
                    raise AuthenticationError(f"Authentication failed: {str(e)}")

                # Check for rate limit errors
                if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise RateLimitError(f"Rate limit exceeded: {str(e)}")

                # For other errors, retry if attempts remain
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
