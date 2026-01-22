"""
Rule-based grammar checking module.

This module handles the second stage of the text correction pipeline:
grammar, spelling, and tense checking using LanguageTool.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ErrorType(Enum):
    """Error type categories."""
    GRAMMAR = "grammar"
    SPELLING = "spelling"
    TENSE = "tense"
    WORD_CHOICE = "word_choice"
    PUNCTUATION = "punctuation"
    STYLE = "style"
    MIXED_LANGUAGE = "mixed_language"


class Severity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class GrammarError:
    """
    Represents a single grammar error detected by LanguageTool.

    Attributes:
        error_type: Type of error
        error_subtype: Specific error subtype
        original_span: Original text containing the error
        corrected_span: Corrected text
        start_index: Start position in original text
        end_index: End position in original text
        explanation: Human-readable explanation
        rule_description: Technical rule description
        severity: Error severity level
        suggestions: List of alternative corrections
        confidence: Confidence score (0-1)
        metadata: Additional error metadata
    """

    error_type: ErrorType
    error_subtype: Optional[str]
    original_span: str
    corrected_span: str
    start_index: int
    end_index: int
    explanation: str
    rule_description: Optional[str]
    severity: Severity
    suggestions: List[str]
    confidence: float
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
        if self.suggestions is None:
            self.suggestions = []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary.

        Returns:
            Dictionary representation of the error
        """
        return {
            'error_type': self.error_type.value,
            'error_subtype': self.error_subtype,
            'original_span': self.original_span,
            'corrected_span': self.corrected_span,
            'start_index': self.start_index,
            'end_index': self.end_index,
            'explanation': self.explanation,
            'rule_description': self.rule_description,
            'severity': self.severity.value,
            'suggestions': self.suggestions,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class RuleEngine:
    """
    Rule-based grammar checking engine.

    Uses LanguageTool to detect grammar, spelling, and tense errors.

    Attributes:
        language: Language code for checking (default: en-US)
        enabled_rules: Set of enabled rule categories
        max_errors: Maximum number of errors to detect
    """

    def __init__(
        self,
        language: str = "en-US",
        enabled_rules: Optional[set] = None,
        max_errors: int = 100
    ):
        """
        Initialize the rule engine.

        Args:
            language: Language code for checking
            enabled_rules: Set of rule categories to enable
            max_errors: Maximum errors to detect
        """
        # TODO: Initialize LanguageTool client
        self.language = language
        self.enabled_rules = enabled_rules or {
            ErrorType.GRAMMAR,
            ErrorType.SPELLING,
            ErrorType.TENSE,
            ErrorType.PUNCTUATION
        }
        self.max_errors = max_errors

    def check(self, text: str) -> List[GrammarError]:
        """
        Check text for grammar errors using LanguageTool.

        Args:
            text: Text to check

        Returns:
            List of detected GrammarError objects

        Example:
            ```python
            engine = RuleEngine()
            errors = engine.check("She don't like apples.")
            assert len(errors) > 0
            assert errors[0].error_type == ErrorType.TENSE
            ```

        Raises:
            RuleEngineError: If checking fails
        """
        # TODO: Implement actual LanguageTool integration
        # 1. Call LanguageTool API
        # 2. Parse results
        # 3. Convert to GrammarError objects
        # 4. Filter by enabled_rules
        # 5. Sort by severity/confidence

        errors = []

        # Placeholder: Simulate error detection
        # In production, this would call LanguageTool
        if "don't" in text.lower() and "she" in text.lower():
            errors.append(
                GrammarError(
                    error_type=ErrorType.TENSE,
                    error_subtype="subject_verb_agreement",
                    original_span="don't",
                    corrected_span="doesn't",
                    start_index=text.lower().find("don't"),
                    end_index=text.lower().find("don't") + len("don't"),
                    explanation="Subject-verb agreement error",
                    rule_description="Third-person singular requires 'doesn't'",
                    severity=Severity.HIGH,
                    suggestions=["doesn't"],
                    confidence=0.95,
                    metadata={}
                )
            )

        return errors[:self.max_errors]

    def check_sentence(self, sentence: str) -> List[GrammarError]:
        """
        Check a single sentence for errors.

        Args:
            sentence: Sentence to check

        Returns:
            List of detected GrammarError objects
        """
        # TODO: Implement sentence-level checking
        return self.check(sentence)

    def get_suggestions(self, error: GrammarError) -> List[str]:
        """
        Get correction suggestions for an error.

        Args:
            error: GrammarError object

        Returns:
            List of suggested corrections
        """
        # TODO: Implement suggestion generation
        return error.suggestions

    def filter_errors(
        self,
        errors: List[GrammarError],
        error_types: Optional[List[ErrorType]] = None,
        min_severity: Optional[Severity] = None,
        min_confidence: float = 0.0
    ) -> List[GrammarError]:
        """
        Filter errors by type, severity, and confidence.

        Args:
            errors: List of errors to filter
            error_types: Allowed error types (None = all)
            min_severity: Minimum severity level
            min_confidence: Minimum confidence threshold

        Returns:
            Filtered list of errors
        """
        filtered = errors

        if error_types:
            filtered = [e for e in filtered if e.error_type in error_types]

        if min_severity:
            severity_order = {Severity.LOW: 1, Severity.MEDIUM: 2, Severity.HIGH: 3}
            filtered = [
                e for e in filtered
                if severity_order.get(e.severity, 0) >= severity_order.get(min_severity, 0)
            ]

        if min_confidence > 0:
            filtered = [e for e in filtered if e.confidence >= min_confidence]

        return filtered


class RuleEngineError(Exception):
    """Exception raised when rule engine operations fail."""

    pass
