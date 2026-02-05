"""
Rule engine tests.

Tests for LanguageTool-based grammar checking functionality.
"""

import pytest
from pipeline.rule_engine import (
    RuleEngine,
    GrammarError,
    ErrorType,
    Severity,
    RuleEngineError,
)


class TestRuleEngineInitialization:
    """Test RuleEngine initialization and singleton pattern."""

    def test_rule_engine_creates_successfully(self):
        """Test that RuleEngine initializes without errors."""
        engine = RuleEngine()
        assert engine is not None
        assert engine.language == "en-US"
        assert engine.max_errors == 100

    def test_rule_engine_singleton_pattern(self):
        """Test that multiple instances share the same LanguageTool instance."""
        engine1 = RuleEngine()
        engine2 = RuleEngine()
        # Both should share the same underlying tool instance
        assert engine1.tool is engine2.tool

    def test_rule_engine_custom_config(self):
        """Test RuleEngine with custom configuration."""
        custom_rules = {ErrorType.GRAMMAR, ErrorType.SPELLING}
        engine = RuleEngine(
            language="en-US",
            enabled_rules=custom_rules,
            max_errors=50
        )
        assert engine.enabled_rules == custom_rules
        assert engine.max_errors == 50


class TestGrammarErrorDetection:
    """Test grammar error detection functionality."""

    def test_detect_subject_verb_agreement_error(self):
        """Test detection of subject-verb agreement errors."""
        engine = RuleEngine()
        text = "She don't like pizza."
        errors = engine.check(text)

        assert len(errors) > 0
        # LanguageTool detects "do" as the error and suggests "does" or "did"
        error = errors[0]
        assert error.original_span in ["do", "don't", "She don't"]
        assert "does" in error.suggestions or "doesn't" in error.suggestions

    def test_detect_tense_error(self):
        """Test detection of tense errors."""
        engine = RuleEngine()
        text = "He have been working here since 2020."
        errors = engine.check(text)

        assert len(errors) > 0
        # Should detect "have" -> "has" (subject-verb agreement with auxiliary verb)
        has_agreement_error = any(
            "have" in error.original_span and "has" in error.suggestions
            for error in errors
        )
        assert has_agreement_error

    def test_detect_article_error(self):
        """Test detection of article usage errors."""
        engine = RuleEngine()
        text = "I need a advice."
        errors = engine.check(text)

        assert len(errors) > 0
        # Should detect "a advice" -> "advice" or "some advice"
        has_article_error = any("advice" in error.original_span for error in errors)
        assert has_article_error

    def test_detect_multiple_errors(self):
        """Test detection of multiple errors in one sentence."""
        engine = RuleEngine()
        text = "She dont like pizza and he dont like bananas."
        errors = engine.check(text)

        # Should detect multiple errors (at least 2 "dont" instances)
        assert len(errors) >= 2

    def test_no_errors_in_correct_text(self):
        """Test that correct text returns no errors."""
        engine = RuleEngine()
        text = "She likes apples and bananas."
        errors = engine.check(text)

        # Correct text should have no errors
        assert len(errors) == 0


class TestSpellingErrorDetection:
    """Test spelling error detection functionality."""

    def test_detect_spelling_error(self):
        """Test detection of spelling errors."""
        engine = RuleEngine()
        text = "I recieved your mesage yesterday."
        errors = engine.check(text)

        assert len(errors) > 0
        # Should detect "recieved" -> "received" and "mesage" -> "message"
        spelling_errors = [e for e in errors if e.error_type == ErrorType.SPELLING]
        assert len(spelling_errors) > 0

    def test_spelling_suggestions(self):
        """Test that spelling errors include suggestions."""
        engine = RuleEngine()
        text = "This is definately wrong."
        errors = engine.check(text)

        # Should detect "definately" -> "definitely"
        spelling_errors = [e for e in errors if "definately" in e.original_span]
        if spelling_errors:
            error = spelling_errors[0]
            assert len(error.suggestions) > 0
            assert "definitely" in error.suggestions


class TestErrorFiltering:
    """Test error filtering functionality."""

    def test_filter_by_error_type(self):
        """Test filtering errors by error type."""
        engine = RuleEngine()
        text = "She dont like apples and I recieved it."
        all_errors = engine.check(text)

        # Filter only grammar errors
        grammar_errors = engine.filter_errors(
            all_errors,
            error_types=[ErrorType.GRAMMAR, ErrorType.TENSE]
        )

        assert all(
            e.error_type in [ErrorType.GRAMMAR, ErrorType.TENSE]
            for e in grammar_errors
        )

    def test_filter_by_severity(self):
        """Test filtering errors by severity level."""
        engine = RuleEngine()
        text = "She dont like apples."
        all_errors = engine.check(text)

        if len(all_errors) > 0:
            # Filter high severity errors only
            high_severity_errors = engine.filter_errors(
                all_errors,
                min_severity=Severity.HIGH
            )

            assert all(e.severity == Severity.HIGH for e in high_severity_errors)

    def test_filter_by_confidence(self):
        """Test filtering errors by confidence threshold."""
        engine = RuleEngine()
        text = "She dont like apples."
        all_errors = engine.check(text)

        if len(all_errors) > 0:
            # Filter errors with high confidence
            confident_errors = engine.filter_errors(
                all_errors,
                min_confidence=0.9
            )

            assert all(e.confidence >= 0.9 for e in confident_errors)

    def test_max_errors_limit(self):
        """Test that max_errors limit is respected."""
        engine = RuleEngine(max_errors=2)
        # Text with multiple errors
        text = "she dont like apples and he dont like banana and they doesnt care"
        errors = engine.check(text)

        # Should return at most 2 errors
        assert len(errors) <= 2


class TestErrorMetadata:
    """Test error metadata and structure."""

    def test_error_has_position_info(self):
        """Test that errors include position information."""
        engine = RuleEngine()
        text = "She don't like pizza."
        errors = engine.check(text)

        if len(errors) > 0:
            error = errors[0]
            assert error.start_index >= 0
            assert error.end_index > error.start_index
            assert error.end_index <= len(text)

    def test_error_has_explanation(self):
        """Test that errors include explanations."""
        engine = RuleEngine()
        text = "She don't like pizza."
        errors = engine.check(text)

        if len(errors) > 0:
            error = errors[0]
            assert error.explanation
            assert len(error.explanation) > 0

    def test_error_has_suggestions(self):
        """Test that errors include correction suggestions."""
        engine = RuleEngine()
        text = "She don't like pizza."
        errors = engine.check(text)

        if len(errors) > 0:
            error = errors[0]
            assert error.suggestions is not None
            assert isinstance(error.suggestions, list)

    def test_error_has_metadata(self):
        """Test that errors include metadata."""
        engine = RuleEngine()
        text = "She don't like pizza."
        errors = engine.check(text)

        if len(errors) > 0:
            error = errors[0]
            assert error.metadata is not None
            assert isinstance(error.metadata, dict)
            assert "rule_id" in error.metadata
            assert "category" in error.metadata


class TestGrammarErrorDataClass:
    """Test GrammarError dataclass functionality."""

    def test_grammar_error_to_dict(self):
        """Test converting GrammarError to dictionary."""
        error = GrammarError(
            error_type=ErrorType.GRAMMAR,
            error_subtype="subject_verb_agreement",
            original_span="don't",
            corrected_span="doesn't",
            start_index=4,
            end_index=9,
            explanation="Subject-verb agreement error",
            rule_description="SUBJECT_VERB_AGREEMENT",
            severity=Severity.HIGH,
            suggestions=["doesn't", "does not"],
            confidence=0.95,
            metadata={"rule_id": "EN_A_VS_AN"}
        )

        error_dict = error.to_dict()

        assert error_dict["error_type"] == "grammar"
        assert error_dict["error_subtype"] == "subject_verb_agreement"
        assert error_dict["original_span"] == "don't"
        assert error_dict["corrected_span"] == "doesn't"
        assert error_dict["start_index"] == 4
        assert error_dict["end_index"] == 9
        assert error_dict["severity"] == "high"
        assert error_dict["confidence"] == 0.95

    def test_grammar_error_default_initialization(self):
        """Test GrammarError initialization with defaults."""
        error = GrammarError(
            error_type=ErrorType.GRAMMAR,
            error_subtype=None,
            original_span="test",
            corrected_span="test",
            start_index=0,
            end_index=4,
            explanation="Test",
            rule_description=None,
            severity=Severity.LOW,
            suggestions=[],
            confidence=0.5,
            metadata=None
        )

        # Check default initialization
        assert error.metadata == {}
        assert error.suggestions == []


class TestSentenceChecking:
    """Test sentence-level checking."""

    def test_check_sentence(self):
        """Test checking a single sentence."""
        engine = RuleEngine()
        sentence = "She don't like pizza."
        errors = engine.check_sentence(sentence)

        assert len(errors) > 0
        assert all(isinstance(e, GrammarError) for e in errors)

    def test_check_empty_sentence(self):
        """Test checking an empty sentence."""
        engine = RuleEngine()
        errors = engine.check_sentence("")

        assert errors == []

    def test_check_very_long_text(self):
        """Test checking very long text."""
        engine = RuleEngine()
        # Create a long text with errors
        long_text = "She don't like pizza. " * 100
        errors = engine.check(long_text)

        # Should detect errors but respect max_errors limit
        assert len(errors) > 0
        assert len(errors) <= engine.max_errors


class TestGetSuggestions:
    """Test suggestion retrieval functionality."""

    def test_get_suggestions_for_error(self):
        """Test getting suggestions for a specific error."""
        engine = RuleEngine()
        text = "She don't like pizza."
        errors = engine.check(text)

        if len(errors) > 0:
            error = errors[0]
            suggestions = engine.get_suggestions(error)

            assert isinstance(suggestions, list)
            assert suggestions == error.suggestions


class TestEnabledRules:
    """Test enabled rules filtering."""

    def test_only_grammar_rules_enabled(self):
        """Test with only grammar rules enabled."""
        engine = RuleEngine(enabled_rules={ErrorType.GRAMMAR})
        text = "She dont like pizza and I recieved it."
        errors = engine.check(text)

        # All errors should be grammar type
        assert all(e.error_type == ErrorType.GRAMMAR for e in errors)

    def test_multiple_rule_types_enabled(self):
        """Test with multiple rule types enabled."""
        engine = RuleEngine(
            enabled_rules={ErrorType.GRAMMAR, ErrorType.SPELLING, ErrorType.TENSE}
        )
        text = "She dont like pizza."
        errors = engine.check(text)

        # All errors should be one of the enabled types
        enabled_types = {ErrorType.GRAMMAR, ErrorType.SPELLING, ErrorType.TENSE}
        assert all(e.error_type in enabled_types for e in errors)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_check_with_special_characters(self):
        """Test checking text with special characters."""
        engine = RuleEngine()
        text = "Hello! How are you? I'm fine, thanks."
        errors = engine.check(text)

        # Should handle special characters without crashing
        assert isinstance(errors, list)

    def test_check_with_numbers(self):
        """Test checking text with numbers."""
        engine = RuleEngine()
        text = "I have 3 apples and 5 oranges."
        errors = engine.check(text)

        # Should handle numbers without crashing
        assert isinstance(errors, list)

    def test_check_with_mixed_case(self):
        """Test checking text with mixed case."""
        engine = RuleEngine()
        text = "SHE DONT LIKE PIZZA."
        errors = engine.check(text)

        # Should still detect errors in uppercase
        assert len(errors) > 0

    def test_check_single_word(self):
        """Test checking a single word."""
        engine = RuleEngine()
        errors = engine.check("Hello")

        # Single correct word should have no errors
        assert len(errors) == 0


@pytest.mark.integration
class TestRealWorldExamples:
    """Test with real-world text examples."""

    def test_business_email(self):
        """Test checking a business email."""
        engine = RuleEngine()
        text = """
        Dear Sir,
        I am writing to inform you that we has received your request.
        We will process it as soon as possible.
        Best regards
        """
        errors = engine.check(text)

        # Should detect "we has" -> "we have"
        assert len(errors) > 0

    def test_casual_conversation(self):
        """Test checking casual conversation."""
        engine = RuleEngine()
        text = "Hey! Whats up? I didnt see you yesterday."
        errors = engine.check(text)

        # Should detect missing apostrophes
        assert len(errors) > 0

    def test_technical_writing(self):
        """Test checking technical writing."""
        engine = RuleEngine()
        text = "The algorithms performs better when the datasets is larger."
        errors = engine.check(text)

        # Should detect subject-verb agreement errors
        assert len(errors) > 0
