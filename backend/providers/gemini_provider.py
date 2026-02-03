"""
Google Gemini LLM Provider implementation.

This module provides the concrete implementation of BaseLLMProvider for Google Gemini,
supporting Gemini 2.0 Flash, Gemini 1.5 Flash, and Gemini 1.5 Pro models.
"""

import time
from typing import List, Optional, Dict, Any
import google.generativeai as genai

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


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider implementation.

    Supports Gemini model series:
    - Gemini 2.0 Flash: Fastest, multimodal (default)
    - Gemini 1.5 Flash: Fast and efficient
    - Gemini 1.5 Pro: Most capable for complex tasks
    """

    # Supported models configuration
    MODELS = [
        ModelInfo(
            name="gemini-2.0-flash-exp",
            display_name="Gemini 2.0 Flash (Experimental)",
            is_default=True,
            description="Fastest multimodal model with excellent performance",
            max_tokens=1000000,
        ),
        ModelInfo(
            name="gemini-1.5-flash",
            display_name="Gemini 1.5 Flash",
            is_default=False,
            description="Fast and efficient model for most tasks",
            max_tokens=1000000,
        ),
        ModelInfo(
            name="gemini-1.5-flash-8b",
            display_name="Gemini 1.5 Flash (8B)",
            is_default=False,
            description="Lightweight version for quick responses",
            max_tokens=1000000,
        ),
        ModelInfo(
            name="gemini-1.5-pro",
            display_name="Gemini 1.5 Pro",
            is_default=False,
            description="Most capable model for complex reasoning tasks",
            max_tokens=2000000,
        ),
    ]

    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Raises:
            ValueError: If api_key is empty
            AuthenticationError: If API key initialization fails
        """
        super().__init__(api_key, timeout, max_retries)

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Gemini client: {str(e)}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "gemini"

    @property
    def display_name(self) -> str:
        """Get provider display name."""
        return "Google Gemini"

    def get_models(self) -> List[ModelInfo]:
        """Get list of supported models."""
        return self.MODELS

    def optimize(
        self,
        text: str,
        mode: CorrectionMode,
        model: Optional[str] = None,
        **kwargs
    ) -> OptimizationResult:
        """
        Optimize text using Gemini.

        Args:
            text: Text to optimize/correct
            mode: Correction mode (accuracy or natural)
            model: Specific model to use (uses default if None)
            **kwargs: Additional parameters (temperature, top_p, etc.)

        Returns:
            OptimizationResult containing optimized text and metadata

        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            ModelNotFoundError: If specified model doesn't exist
            InvalidRequestError: If request parameters are invalid
            LLMProviderError: For other provider-specific errors
        """
        # Use default model if not specified
        if not model:
            model = self.get_default_model()

        # Validate model
        if not self.validate_model(model):
            raise ModelNotFoundError(
                f"Model '{model}' not found for provider '{self.provider_name}'. "
                f"Available models: {', '.join([m.name for m in self.MODELS])}"
            )

        start_time = time.time()

        try:
            # Build prompt based on mode
            prompt = self._build_prompt(text, mode)

            # Configure generation parameters
            generation_config = {
                "temperature": kwargs.get("temperature", 0.3 if mode == CorrectionMode.ACCURACY else 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_output_tokens", 2000),
            }

            # Create model instance
            gemini_model = genai.GenerativeModel(model)

            # Generate response
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**generation_config),
            )

            processing_time = int((time.time() - start_time) * 1000)

            # Extract optimized text
            optimized_text = response.text.strip()

            # Extract corrections if mode is accuracy
            corrections = self._extract_corrections(text, optimized_text, mode)

            # Estimate token usage
            input_tokens = self._estimate_tokens(text)
            output_tokens = self._estimate_tokens(optimized_text)

            token_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }

            return OptimizationResult(
                optimized_text=optimized_text,
                corrections=corrections,
                explanation=self._generate_explanation(mode),
                token_usage=token_usage,
                model=model,
                processing_time_ms=processing_time,
                metadata={
                    "mode": mode.value,
                    "finish_reason": getattr(response, "finish_reason", "stop"),
                },
            )

        except Exception as e:
            error_str = str(e).lower()

            # Parse error type
            if "api key" in error_str or "authentication" in error_str or "unauthorized" in error_str:
                raise AuthenticationError(f"Gemini API key authentication failed: {str(e)}")
            elif "quota" in error_str or "rate limit" in error_str:
                raise RateLimitError(f"Gemini rate limit exceeded: {str(e)}")
            elif "model" in error_str or "not found" in error_str:
                raise ModelNotFoundError(f"Gemini model not found: {str(e)}")
            elif "invalid" in error_str or "parameter" in error_str:
                raise InvalidRequestError(f"Invalid request to Gemini API: {str(e)}")
            else:
                raise LLMProviderError(f"Gemini optimization failed: {str(e)}")

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
            # Use the default model which is guaranteed to exist
            model = genai.GenerativeModel(self.get_default_model())
            response = model.generate_content("Hello")
            return response.text is not None
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "authentication" in error_str:
                raise AuthenticationError(f"Gemini API key authentication failed: {str(e)}")
            raise LLMProviderError(f"Gemini connection test failed: {str(e)}")

    def _build_prompt(self, text: str, mode: CorrectionMode) -> str:
        """
        Build prompt for text optimization.

        Args:
            text: Input text
            mode: Correction mode

        Returns:
            Prompt string
        """
        if mode == CorrectionMode.ACCURACY:
            return f"""Fix grammatical, spelling, and tense errors in this English text.

Text: "{text}"

Guidelines:
1. Fix ONLY actual errors (grammar, spelling, tense)
2. Do NOT change the style or tone unless it's an error
3. Return ONLY the corrected text, no explanations

Corrected text:"""
        else:  # NATURAL mode
            return f"""Improve the naturalness and flow of this English text while preserving the original meaning.

Text: "{text}"

Guidelines:
1. Improve sentence flow and word choice for natural expression
2. Maintain the original tone and style
3. Return ONLY the improved text, no explanations

Improved text:"""

    def _extract_corrections(
        self,
        original: str,
        corrected: str,
        mode: CorrectionMode
    ) -> List[Dict[str, Any]]:
        """
        Extract corrections by comparing original and corrected text.

        Args:
            original: Original text
            corrected: Corrected text
            mode: Optimization mode

        Returns:
            List of correction dictionaries
        """
        if original == corrected:
            return []

        # Simple difference detection (can be enhanced with diff algorithm)
        corrections = []

        # Find words that changed
        original_words = original.split()
        corrected_words = corrected.split()

        # Track positions
        original_pos = 0
        corrected_pos = 0

        while original_pos < len(original_words) and corrected_pos < len(corrected_words):
            orig_word = original_words[original_pos]
            corr_word = corrected_words[corrected_pos]

            if orig_word.lower() == corr_word.lower():
                original_pos += 1
                corrected_pos += 1
            else:
                # Found a correction
                corrections.append({
                    "original": orig_word,
                    "corrected": corr_word,
                    "type": "grammar" if mode == CorrectionMode.ACCURACY else "style",
                    "severity": "medium",
                    "explanation": "Corrected for better accuracy" if mode == CorrectionMode.ACCURACY else "Improved for naturalness",
                })
                original_pos += 1
                corrected_pos += 1

        return corrections

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough estimate: ~1.3 tokens per word for English
        return int(len(text.split()) * 1.3)

    def _generate_explanation(self, mode: CorrectionMode) -> str:
        """
        Generate explanation for the optimization.

        Args:
            mode: Correction mode used

        Returns:
            Explanation string
        """
        if mode == CorrectionMode.ACCURACY:
            return "Grammatical errors have been corrected while preserving the original style."
        else:
            return "Text has been optimized for naturalness and flow."
