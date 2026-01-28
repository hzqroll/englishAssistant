"""
LLM-based text optimization module.

This module handles third stage of text correction pipeline:
naturalness improvement using Zhipu AI (GLM-4-Flash).
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import time
from zhipuai import ZhipuAI


class TextType(Enum):
    """Text type categories."""

    DIALOGUE = "dialogue"
    EMAIL = "email"
    ESSAY = "essay"
    MESSAGE = "message"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class Tone(Enum):
    """Tone categories."""

    FORMAL = "formal"
    INFORMAL = "informal"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    NEUTRAL = "neutral"


@dataclass
class Intent:
    """
    Detected intent of text.

    Attributes:
        text_type: Type of text (dialogue, email, etc.)
        tone: Tone of text
        speakers: List of detected speakers (for dialogues)
        has_chinese: Whether text contains Chinese characters
        confidence: Confidence score (0-1)
    """

    text_type: TextType
    tone: Tone
    speakers: List[str]
    has_chinese: bool
    confidence: float

    def __post_init__(self):
        """Initialize default values."""
        if self.speakers is None:
            self.speakers = []


@dataclass
class LLMResult:
    """
    Result from LLM optimization.

    Attributes:
        optimized_text: Text optimized by LLM
        detected_intent: Detected text intent
        corrections: List of corrections made
        explanation: Explanation of changes
        token_usage: Token usage statistics
        model: Model used for optimization
        processing_time_ms: Processing time in milliseconds
        metadata: Additional metadata
    """

    optimized_text: str
    detected_intent: Intent
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "optimized_text": self.optimized_text,
            "detected_intent": {
                "text_type": self.detected_intent.text_type.value,
                "tone": self.detected_intent.tone.value,
                "speakers": self.detected_intent.speakers,
                "has_chinese": self.detected_intent.has_chinese,
                "confidence": self.detected_intent.confidence,
            },
            "corrections": self.corrections,
            "explanation": self.explanation,
            "token_usage": self.token_usage,
            "model": self.model,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata,
        }


class LLMError(Exception):
    """Exception raised when LLM operations fail."""

    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize LLM error.

        Args:
            message: Error message
            error_code: Optional error code
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class LLMEngine:
    """
    LLM-based text optimization engine.

    Uses Zhipu AI (GLM-4-Flash) for naturalness improvement and
    Chinese-English mixing correction.

    Attributes:
        model: Model name to use (default: glm-4-flash)
        api_key: Zhipu AI API key
        client: Zhipu AI client instance
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        model: str = "glm-4-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        timeout: int = 30,
    ):
        """
        Initialize LLM engine.

        Args:
            model: Model name
            api_key: Zhipu AI API key (None to disable LLM features)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens
            timeout: Request timeout
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.client = None
        self.enabled = bool(api_key)

        if api_key:
            try:
                self.client = ZhipuAI(api_key=api_key)
            except Exception as e:
                raise LLMError(f"Failed to initialize Zhipu AI client: {str(e)}")

    def optimize(
        self, text: str, mode: str = "accuracy", intent: Optional[Intent] = None
    ) -> LLMResult:
        """
        Optimize text using LLM.

        Args:
            text: Text to optimize
            mode: Optimization mode (accuracy/natural)
            intent: Pre-detected intent (optional)

        Returns:
            LLMResult with optimized text and metadata

        Example:
            ```python
            engine = LLMEngine(api_key="your-key")
            result = engine.optimize("He go to school yesterday.")
            assert "went" in result.optimized_text.lower()
            ```

        Raises:
            LLMError: If optimization fails or LLM is not configured
        """
        if not self.enabled:
            raise LLMError("LLM engine is not enabled (no API key configured)")

        start_time = time.time()

        try:
            detected_intent = intent or self._detect_intent(text)

            if mode == "natural":
                optimized = self._optimize_natural(text, detected_intent)
            else:
                optimized = self._optimize_accuracy(text, detected_intent)

            processing_time = int((time.time() - start_time) * 1000)

            return LLMResult(
                optimized_text=optimized,
                detected_intent=detected_intent,
                corrections=self._extract_corrections(text, optimized, mode),
                explanation="",
                token_usage=self._estimate_tokens(text, optimized),
                model=self.model,
                processing_time_ms=processing_time,
                metadata={"mode": mode},
            )

        except Exception as e:
            raise LLMError(f"Optimization failed: {str(e)}")

    def _detect_intent(self, text: str) -> Intent:
        """
        Detect text intent using LLM.

        Args:
            text: Input text

        Returns:
            Detected Intent object
        """
        prompt = f"""
Analyze the following English text and detect its intent.

Text: "{text}"

Return a JSON object with this structure:
{{
  "text_type": "dialogue|email|essay|message|document|unknown",
  "tone": "formal|informal|friendly|professional|neutral",
  "speakers": ["speaker1", "speaker2"],
  "has_chinese": true/false,
  "confidence": 0.95
}}

Response JSON:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a text analysis expert."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            content = response.choices[0].message.content
            result_data = self._parse_json_response(content)

            return Intent(
                text_type=TextType(result_data.get("text_type", "unknown")),
                tone=Tone(result_data.get("tone", "neutral")),
                speakers=result_data.get("speakers", []),
                has_chinese=result_data.get("has_chinese", False),
                confidence=result_data.get("confidence", 0.8),
            )

        except Exception as e:
            return self._fallback_intent_detection(text)

    def _optimize_natural(self, text: str, intent: Intent) -> str:
        """
        Improve text naturalness.

        Args:
            text: Input text
            intent: Detected intent

        Returns:
            Improved text
        """
        has_chinese = "Contains Chinese characters. " if intent.has_chinese else ""

        prompt = f"""
Improve the naturalness and flow of this English text while preserving the original meaning.

Text: "{text}"

Context:
- Text Type: {intent.text_type.value}
- Tone: {intent.tone.value}
- {has_chinese}

Guidelines:
1. Improve sentence flow and word choice for natural expression
2. Maintain the original tone and style
3. If there are Chinese characters, suggest appropriate English alternatives
4. Return ONLY the improved text, no explanations

Improved text:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert English editor."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=self.max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise LLMError(f"Naturalness optimization failed: {str(e)}")

    def _optimize_accuracy(self, text: str, intent: Intent) -> str:
        """
        Fix errors while preserving original style.

        Args:
            text: Input text
            intent: Detected intent

        Returns:
            Corrected text
        """
        has_chinese = "Contains Chinese characters. " if intent.has_chinese else ""

        prompt = f"""
Fix grammatical, spelling, and tense errors in this English text.

Text: "{text}"

Context:
- Text Type: {intent.text_type.value}
- {has_chinese}

Guidelines:
1. Fix ONLY actual errors (grammar, spelling, tense)
2. Do NOT change the style or tone unless it's an error
3. If there are Chinese characters, replace with appropriate English
4. Return ONLY the corrected text, no explanations

Corrected text:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a grammar expert."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=self.max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise LLMError(f"Accuracy optimization failed: {str(e)}")

    def _extract_corrections(
        self, original: str, corrected: str, mode: str
    ) -> List[Dict[str, Any]]:
        """
        Extract corrections from original and corrected text.

        Args:
            original: Original text
            corrected: Corrected text
            mode: Optimization mode

        Returns:
            List of corrections
        """
        if original == corrected:
            return []

        try:
            prompt = f"""
Compare these two texts and identify specific changes.

Original: "{original}"
Corrected: "{corrected}"

Return a JSON array of changes:
[
  {{
    "original": "original phrase",
    "corrected": "corrected phrase",
    "type": "grammar|tense|word_choice|mixed_language|style",
    "severity": "low|medium|high",
    "explanation": "brief explanation"
  }}
]

Response JSON:
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a text comparison expert."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            corrections_data = self._parse_json_response(content)

            if isinstance(corrections_data, list):
                return corrections_data

            return []

        except Exception:
            return []

    def _estimate_tokens(self, input_text: str, output_text: str) -> Dict[str, int]:
        """
        Estimate token usage.

        Args:
            input_text: Input text
            output_text: Output text

        Returns:
            Token usage statistics
        """
        input_tokens = len(input_text.split()) * 1.3
        output_tokens = len(output_text.split()) * 1.3

        return {
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "total_tokens": int(input_tokens + output_tokens),
        }

    def _fallback_intent_detection(self, text: str) -> Intent:
        """
        Fallback intent detection.

        Args:
            text: Input text

        Returns:
            Detected Intent object
        """
        has_chinese = any("\u4e00" <= char <= "\u9fff" for char in text)

        text_lower = text.lower()

        text_type = TextType.UNKNOWN
        if ":" in text or "\n" in text:
            text_type = TextType.DIALOGUE
        elif "@" in text_lower or "subject:" in text_lower:
            text_type = TextType.EMAIL
        elif len(text) > 500:
            text_type = TextType.ESSAY
        elif len(text) < 200:
            text_type = TextType.MESSAGE

        return Intent(
            text_type=text_type,
            tone=Tone.NEUTRAL,
            speakers=[],
            has_chinese=has_chinese,
            confidence=0.6,
        )

    def _parse_json_response(self, content: str) -> Any:
        """
        Parse JSON response from LLM.

        Args:
            content: Raw content from LLM

        Returns:
            Parsed JSON object
        """
        content = content.strip()

        json_match = None
        start_idx = content.find("{")
        end_idx = content.rfind("}")

        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_match = content[start_idx : end_idx + 1]
        else:
            start_idx = content.find("[")
            end_idx = content.rfind("]")
            if start_idx != -1 and end_idx != -1:
                json_match = content[start_idx : end_idx + 1]

        if json_match:
            try:
                return json.loads(json_match)
            except json.JSONDecodeError:
                pass

        return {}

    def batch_optimize(self, texts: List[str], mode: str = "accuracy") -> List[LLMResult]:
        """
        Optimize multiple texts in batch.

        Args:
            texts: List of texts to optimize
            mode: Optimization mode

        Returns:
            List of LLMResult objects
        """
        results = []
        for text in texts:
            result = self.optimize(text, mode)
            results.append(result)
        return results
