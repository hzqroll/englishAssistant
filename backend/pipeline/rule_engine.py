"""
Rule-based grammar checking module.

This module handles second stage of text correction pipeline:
grammar, spelling, and tense checking using LanguageTool.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import language_tool_python


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
        original_span: Original text containing error
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
            "error_type": self.error_type.value,
            "error_subtype": self.error_subtype,
            "original_span": self.original_span,
            "corrected_span": self.corrected_span,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "explanation": self.explanation,
            "rule_description": self.rule_description,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class RuleEngine:
    """
    Rule-based grammar checking engine.

    Uses LanguageTool to detect grammar, spelling, and tense errors.

    Attributes:
        language: Language code for checking (default: en-US)
        enabled_rules: Set of enabled rule categories
        max_errors: Maximum number of errors to detect
        tool: LanguageTool client instance
    """

    def __init__(
        self, language: str = "en-US", enabled_rules: Optional[set] = None, max_errors: int = 100
    ):
        """
        Initialize the rule engine.

        Args:
            language: Language code for checking
            enabled_rules: Set of rule categories to enable
            max_errors: Maximum errors to detect
        """
        self.language = language
        self.enabled_rules = enabled_rules or {
            ErrorType.GRAMMAR,
            ErrorType.SPELLING,
            ErrorType.TENSE,
            ErrorType.PUNCTUATION,
        }
        self.max_errors = max_errors

        try:
            self.tool = language_tool_python.LanguageTool(language)
        except Exception as e:
            raise RuleEngineError(f"Failed to initialize LanguageTool: {str(e)}")

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
        try:
            matches = self.tool.check(text)
        except Exception as e:
            raise RuleEngineError(f"LanguageTool check failed: {str(e)}")

        errors = []
        for match in matches:
            error = self._convert_match_to_error(text, match)

            if error.error_type in self.enabled_rules:
                errors.append(error)

        errors = errors[: self.max_errors]

        return errors

    def check_sentence(self, sentence: str) -> List[GrammarError]:
        """
        Check a single sentence for errors.

        Args:
            sentence: Sentence to check

        Returns:
            List of detected GrammarError objects
        """
        return self.check(sentence)

    def get_suggestions(self, error: GrammarError) -> List[str]:
        """
        Get correction suggestions for an error.

        Args:
            error: GrammarError object

        Returns:
            List of suggested corrections
        """
        return error.suggestions

    def filter_errors(
        self,
        errors: List[GrammarError],
        error_types: Optional[List[ErrorType]] = None,
        min_severity: Optional[Severity] = None,
        min_confidence: float = 0.0,
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
                e
                for e in filtered
                if severity_order.get(e.severity, 0) >= severity_order.get(min_severity, 0)
            ]

        if min_confidence > 0:
            filtered = [e for e in filtered if e.confidence >= min_confidence]

        return filtered

    def _convert_match_to_error(
        self, text: str, match: language_tool_python.utils.Match
    ) -> GrammarError:
        """
        Convert LanguageTool match to GrammarError.

        Args:
            text: Original text
            match: LanguageTool match object

        Returns:
            GrammarError object
        """
        original_span = text[match.offset : match.offset + match.errorLength]
        corrected_span = match.replacements[0] if match.replacements else original_span

        error_type = self._map_category(match)
        error_subtype = self._get_subtype(match)
        severity = self._assess_severity(match)
        explanation = self._generate_explanation(match)

        return GrammarError(
            error_type=error_type,
            error_subtype=error_subtype,
            original_span=original_span,
            corrected_span=corrected_span,
            start_index=match.offset,
            end_index=match.offset + match.errorLength,
            explanation=explanation,
            rule_description=match.ruleId or match.message,
            severity=severity,
            suggestions=match.replacements[:3],
            confidence=self._estimate_confidence(match),
            metadata={
                "rule_id": match.ruleId,
                "category": match.category,
                "context": match.context,
            },
        )

    def _map_category(self, match: language_tool_python.utils.Match) -> ErrorType:
        """
        Map LanguageTool category to ErrorType.

        Args:
            match: LanguageTool match object

        Returns:
            Mapped ErrorType
        """
        category = match.category or ""
        rule_id = match.ruleId or ""

        if "TENSE" in rule_id.upper():
            return ErrorType.TENSE

        if "SPELLING" in category.upper() or "TYPOS" in category.upper():
            return ErrorType.SPELLING

        if "WORD" in category.upper() or "VOCABULARY" in category.upper():
            return ErrorType.WORD_CHOICE

        if "PUNCTUATION" in category.upper():
            return ErrorType.PUNCTUATION

        if "STYLE" in category.upper():
            return ErrorType.STYLE

        return ErrorType.GRAMMAR

    def _get_subtype(self, match: language_tool_python.utils.Match) -> Optional[str]:
        """
        Get error subtype from rule ID.

        Args:
            match: LanguageTool match object

        Returns:
            Error subtype or None
        """
        if not match.ruleId:
            return None

        rule_id = match.ruleId.upper()

        if "AGREEMENT" in rule_id:
            return "subject_verb_agreement"
        elif "TENSE" in rule_id:
            return "tense_error"
        elif "ARTICLE" in rule_id:
            return "article_usage"
        elif "PREPOSITION" in rule_id:
            return "preposition_usage"
        elif "PRONOUN" in rule_id:
            return "pronoun_usage"
        elif "CONJUNCTION" in rule_id:
            return "conjunction_usage"
        else:
            return rule_id.lower().replace("_", "-")

    def _assess_severity(self, match: language_tool_python.utils.Match) -> Severity:
        """
        Assess error severity.

        Args:
            match: LanguageTool match object

        Returns:
            Severity level
        """
        if "TYPOS" in match.category or "SPELLING" in match.category:
            return Severity.LOW

        if "TENSE" in match.ruleId or "AGREEMENT" in match.ruleId:
            return Severity.HIGH

        if "STYLE" in match.category:
            return Severity.MEDIUM

        return Severity.MEDIUM

    def _generate_explanation(self, match: language_tool_python.utils.Match) -> str:
        """
        Generate human-readable explanation.

        Args:
            match: LanguageTool match object

        Returns:
            Explanation string
        """
        return match.message or "Grammar error detected"

    def _estimate_confidence(self, match: language_tool_python.utils.Match) -> float:
        """
        Estimate confidence score for the error.

        Args:
            match: LanguageTool match object

        Returns:
            Confidence score (0-1)
        """
        base_confidence = 0.8

        if match.replacements and len(match.replacements) > 0:
            base_confidence += 0.1

        if "TENSE" in match.ruleId or "AGREEMENT" in match.ruleId:
            base_confidence += 0.1

        return min(base_confidence, 1.0)


class RuleEngineError(Exception):
    """Exception raised when rule engine operations fail."""

    pass
