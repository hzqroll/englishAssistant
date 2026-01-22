"""
Token counting service.

Handles token counting and cost estimation for LLM usage.
"""

from typing import Dict, Any
import re


class TokenCounter:
    """
    Token counting and pricing service.

    Estimates token counts and costs for LLM API calls.

    Attributes:
        pricing: Dictionary of model pricing per 1K tokens
        token_to_word_ratio: Approximate ratio of tokens to words
    """

    def __init__(self):
        """Initialize the token counter."""
        self.pricing = {
            'glm-4-flash': {'input': 0.0001, 'output': 0.0001},  # ¥ per 1K tokens
            'glm-4': {'input': 0.001, 'output': 0.001},
            'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
            'gpt-4': {'input': 0.03, 'output': 0.06}
        }
        self.token_to_word_ratio = 0.75  # Approx 1 token per 1.33 words

    def count_tokens(self, text: str, model: str = "glm-4-flash") -> int:
        """
        Estimate token count for text.

        Args:
            text: Input text
            model: Model name for tokenization

        Returns:
            Estimated token count

        Example:
            ```python
            counter = TokenCounter()
            count = counter.count_tokens("Hello world!")
            assert count > 0
            ```
        """
        # TODO: Implement actual token counting
        # Use tiktoken or model-specific tokenizer for accuracy
        # For now, use word-based approximation

        words = len(text.split())
        tokens = int(words / self.token_to_word_ratio)

        # Add overhead for special tokens
        tokens += 10

        return max(tokens, 1)

    def count_messages_tokens(
        self,
        messages: list,
        model: str = "glm-4-flash"
    ) -> Dict[str, int]:
        """
        Count tokens for chat messages.

        Args:
            messages: List of message dictionaries
            model: Model name

        Returns:
            Dictionary with token counts per message and total
        """
        # TODO: Implement message-based token counting
        total_tokens = 0
        message_tokens = []

        for message in messages:
            content = message.get('content', '')
            role = message.get('role', '')

            # Count content tokens
            content_tokens = self.count_tokens(content, model)

            # Add role tokens (small overhead)
            role_tokens = self.count_tokens(role, model)

            total = content_tokens + role_tokens + 4  # Add formatting overhead
            message_tokens.append(total)
            total_tokens += total

        return {
            'messages': message_tokens,
            'total': total_tokens
        }

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "glm-4-flash"
    ) -> float:
        """
        Calculate estimated cost for API call.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name

        Returns:
            Estimated cost in currency (CNY)

        Example:
            ```python
            cost = counter.calculate_cost(100, 200, "glm-4-flash")
            assert cost > 0
            ```
        """
        # TODO: Implement cost calculation
        pricing = self.pricing.get(model, {'input': 0, 'output': 0})

        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']

        return input_cost + output_cost

    def estimate_response_cost(
        self,
        text: str,
        model: str = "glm-4-flash",
        expected_response_ratio: float = 2.0
    ) -> Dict[str, Any]:
        """
        Estimate total cost for text analysis.

        Args:
            text: Input text
            model: Model name
            expected_response_ratio: Expected output/input token ratio

        Returns:
            Dictionary with cost breakdown
        """
        # TODO: Implement cost estimation
        input_tokens = self.count_tokens(text, model)
        estimated_output_tokens = int(input_tokens * expected_response_ratio)

        cost = self.calculate_cost(input_tokens, estimated_output_tokens, model)

        return {
            'input_tokens': input_tokens,
            'estimated_output_tokens': estimated_output_tokens,
            'estimated_total_tokens': input_tokens + estimated_output_tokens,
            'estimated_cost': cost,
            'currency': 'CNY',
            'model': model
        }

    def get_pricing(self, model: str) -> Dict[str, float]:
        """
        Get pricing for a model.

        Args:
            model: Model name

        Returns:
            Dictionary with input and output pricing
        """
        return self.pricing.get(model, {'input': 0, 'output': 0})

    def update_pricing(self, model: str, input_price: float, output_price: float) -> None:
        """
        Update pricing for a model.

        Args:
            model: Model name
            input_price: Price per 1K input tokens
            output_price: Price per 1K output tokens
        """
        self.pricing[model] = {
            'input': input_price,
            'output': output_price
        }


class TokenCounterError(Exception):
    """Exception raised for token counter errors."""

    pass
