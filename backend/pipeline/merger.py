"""
Result merger module.

This module handles the fourth stage of the text correction pipeline:
merging rule-based and LLM results while handling overlapping corrections.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from .rule_engine import GrammarError, ErrorType, Severity
from .llm_engine import LLMResult


class ConflictResolution(Enum):
    """Strategies for resolving overlapping corrections."""
    RULE_ENGINE_PRIORITY = "rule_engine_priority"
    LLM_PRIORITY = "llm_priority"
    MERGE = "merge"
    HIGHEST_CONFIDENCE = "highest_confidence"


@dataclass
class OverlapInfo:
    """
    Information about overlapping corrections.

    Attributes:
        rule_error: Error from rule engine
        llm_correction: Correction from LLM
        overlap_type: Type of overlap (identical/partial/conflicting)
        overlap_start: Start position of overlap
        overlap_end: End position of overlap
    """

    rule_error: Optional[GrammarError]
    llm_correction: Optional[Dict[str, Any]]
    overlap_type: str
    overlap_start: int
    overlap_end: int


@dataclass
class MergedResult:
    """
    Merged correction result.

    Attributes:
        corrected_text: Final corrected text
        errors: List of merged error details
        rule_engine_errors: Errors from rule engine
        llm_corrections: Corrections from LLM
        overlaps: List of detected overlaps
        statistics: Correction statistics
        metadata: Additional metadata
    """

    corrected_text: str
    errors: List[Dict[str, Any]]
    rule_engine_errors: List[GrammarError]
    llm_corrections: List[Dict[str, Any]]
    overlaps: List[OverlapInfo]
    statistics: Dict[str, Any]
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize default values."""
        if self.errors is None:
            self.errors = []
        if self.rule_engine_errors is None:
            self.rule_engine_errors = []
        if self.llm_corrections is None:
            self.llm_corrections = []
        if self.overlaps is None:
            self.overlaps = []
        if self.statistics is None:
            self.statistics = {}
        if self.metadata is None:
            self.metadata = {}


class Merger:
    """
    Merger for combining rule-based and LLM correction results.

    Handles overlapping corrections and produces final merged result.

    Attributes:
        conflict_resolution: Strategy for resolving conflicts
        allow_overlap: Whether to allow overlapping corrections
        min_confidence: Minimum confidence threshold
    """

    def __init__(
        self,
        conflict_resolution: ConflictResolution = ConflictResolution.HIGHEST_CONFIDENCE,
        allow_overlap: bool = False,
        min_confidence: float = 0.5
    ):
        """
        Initialize the merger.

        Args:
            conflict_resolution: Strategy for resolving conflicts
            allow_overlap: Whether to allow overlapping corrections
            min_confidence: Minimum confidence threshold
        """
        self.conflict_resolution = conflict_resolution
        self.allow_overlap = allow_overlap
        self.min_confidence = min_confidence

    def merge(
        self,
        original_text: str,
        rule_errors: List[GrammarError],
        llm_result: LLMResult
    ) -> MergedResult:
        """
        Merge rule-based and LLM correction results.

        Args:
            original_text: Original input text
            rule_errors: Errors detected by rule engine
            llm_result: Result from LLM optimization

        Returns:
            MergedResult with final corrections

        Example:
            ```python
            merger = Merger()
            result = merger.merge(original_text, rule_errors, llm_result)
            assert result.corrected_text
            assert len(result.errors) > 0
            ```

        Raises:
            MergerError: If merging fails
        """
        # TODO: Implement actual merging logic
        # 1. Detect overlaps between rule errors and LLM corrections
        # 2. Resolve conflicts based on strategy
        # 3. Merge non-overlapping corrections
        # 4. Generate final corrected text
        # 5. Calculate statistics

        overlaps = self._detect_overlaps(rule_errors, llm_result)
        errors = self._resolve_conflicts(rule_errors, llm_result, overlaps)
        corrected_text = self._apply_corrections(original_text, errors)

        statistics = self._calculate_statistics(rule_errors, llm_result, errors)

        return MergedResult(
            corrected_text=corrected_text,
            errors=errors,
            rule_engine_errors=rule_errors,
            llm_corrections=llm_result.corrections,
            overlaps=overlaps,
            statistics=statistics,
            metadata={}
        )

    def _detect_overlaps(
        self,
        rule_errors: List[GrammarError],
        llm_result: LLMResult
    ) -> List[OverlapInfo]:
        """
        Detect overlapping corrections.

        Args:
            rule_errors: Rule engine errors
            llm_result: LLM result

        Returns:
            List of overlap information
        """
        # TODO: Implement overlap detection
        # 1. Compare positions of rule errors and LLM corrections
        # 2. Classify overlap type (identical/partial/conflicting)
        # 3. Calculate overlap boundaries

        overlaps = []

        # Placeholder: Simulate overlap detection
        for rule_error in rule_errors:
            for llm_correction in llm_result.corrections:
                # Check if positions overlap
                if self._positions_overlap(
                    rule_error.start_index,
                    rule_error.end_index,
                    llm_correction.get('start_index', 0),
                    llm_correction.get('end_index', 0)
                ):
                    overlap_type = self._classify_overlap(rule_error, llm_correction)
                    overlaps.append(
                        OverlapInfo(
                            rule_error=rule_error,
                            llm_correction=llm_correction,
                            overlap_type=overlap_type,
                            overlap_start=max(
                                rule_error.start_index,
                                llm_correction.get('start_index', 0)
                            ),
                            overlap_end=min(
                                rule_error.end_index,
                                llm_correction.get('end_index', 0)
                            )
                        )
                    )

        return overlaps

    def _positions_overlap(
        self,
        start1: int,
        end1: int,
        start2: int,
        end2: int
    ) -> bool:
        """
        Check if two position ranges overlap.

        Args:
            start1: Start of first range
            end1: End of first range
            start2: Start of second range
            end2: End of second range

        Returns:
            True if ranges overlap
        """
        return not (end1 <= start2 or end2 <= start1)

    def _classify_overlap(
        self,
        rule_error: GrammarError,
        llm_correction: Dict[str, Any]
    ) -> str:
        """
        Classify type of overlap.

        Args:
            rule_error: Rule engine error
            llm_correction: LLM correction

        Returns:
            Overlap type (identical/partial/conflicting)
        """
        # TODO: Implement overlap classification
        # 1. Check if corrections are identical
        # 2. Check if corrections are partial overlap
        # 3. Check if corrections conflict

        if rule_error.corrected_span == llm_correction.get('corrected_span'):
            return "identical"

        return "partial"

    def _resolve_conflicts(
        self,
        rule_errors: List[GrammarError],
        llm_result: LLMResult,
        overlaps: List[OverlapInfo]
    ) -> List[Dict[str, Any]]:
        """
        Resolve conflicting corrections.

        Args:
            rule_errors: Rule engine errors
            llm_result: LLM result
            overlaps: Detected overlaps

        Returns:
            List of resolved corrections
        """
        # TODO: Implement conflict resolution
        # 1. Apply resolution strategy
        # 2. Filter by confidence threshold
        # 3. Handle edge cases

        if self.conflict_resolution == ConflictResolution.RULE_ENGINE_PRIORITY:
            return [e.to_dict() for e in rule_errors]
        elif self.conflict_resolution == ConflictResolution.LLM_PRIORITY:
            return llm_result.corrections
        elif self.conflict_resolution == ConflictResolution.HIGHEST_CONFIDENCE:
            # Select corrections with highest confidence
            return self._select_highest_confidence(rule_errors, llm_result.corrections)
        else:
            return self._merge_corrections(rule_errors, llm_result.corrections)

    def _select_highest_confidence(
        self,
        rule_errors: List[GrammarError],
        llm_corrections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Select corrections with highest confidence.

        Args:
            rule_errors: Rule engine errors
            llm_corrections: LLM corrections

        Returns:
            Selected corrections
        """
        # TODO: Implement highest confidence selection
        selected = []

        for error in rule_errors:
            if error.confidence >= self.min_confidence:
                selected.append(error.to_dict())

        for correction in llm_corrections:
            if correction.get('confidence', 0) >= self.min_confidence:
                selected.append(correction)

        return selected

    def _merge_corrections(
        self,
        rule_errors: List[GrammarError],
        llm_corrections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge corrections from both sources.

        Args:
            rule_errors: Rule engine errors
            llm_corrections: LLM corrections

        Returns:
            Merged corrections
        """
        # TODO: Implement correction merging
        # Combine corrections from both sources, removing duplicates
        merged = {}

        for error in rule_errors:
            key = (error.start_index, error.end_index)
            merged[key] = error.to_dict()

        for correction in llm_corrections:
            key = (correction.get('start_index'), correction.get('end_index'))
            if key not in merged:
                merged[key] = correction

        return list(merged.values())

    def _apply_corrections(
        self,
        original_text: str,
        corrections: List[Dict[str, Any]]
    ) -> str:
        """
        Apply corrections to text.

        Args:
            original_text: Original text
            corrections: List of corrections to apply

        Returns:
            Corrected text
        """
        # TODO: Implement correction application
        # Apply corrections from right to left to preserve positions
        corrected = original_text

        # Sort corrections by position (reverse order)
        sorted_corrections = sorted(
            corrections,
            key=lambda x: x.get('start_index', 0),
            reverse=True
        )

        for correction in sorted_corrections:
            start = correction.get('start_index', 0)
            end = correction.get('end_index', 0)
            corrected_span = correction.get('corrected_span', '')

            corrected = corrected[:start] + corrected_span + corrected[end:]

        return corrected

    def _calculate_statistics(
        self,
        rule_errors: List[GrammarError],
        llm_result: LLMResult,
        merged_errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate correction statistics.

        Args:
            rule_errors: Rule engine errors
            llm_result: LLM result
            merged_errors: Merged errors

        Returns:
            Statistics dictionary
        """
        # TODO: Implement statistics calculation
        return {
            'total_errors': len(merged_errors),
            'rule_engine_errors': len(rule_errors),
            'llm_corrections': len(llm_result.corrections),
            'overlaps_resolved': len([e for e in merged_errors if e.get('from_overlap')]),
            'error_types': self._count_error_types(merged_errors),
            'severity_distribution': self._count_severity(merged_errors)
        }

    def _count_error_types(self, errors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count errors by type."""
        counts = {}
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts

    def _count_severity(self, errors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count errors by severity."""
        counts = {}
        for error in errors:
            severity = error.get('severity', 'unknown')
            counts[severity] = counts.get(severity, 0) + 1
        return counts


class MergerError(Exception):
    """Exception raised when merger operations fail."""

    pass
