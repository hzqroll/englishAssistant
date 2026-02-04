"""
Main analysis pipeline controller.

This module orchestrates the 4-stage text correction pipeline.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import time

from .preprocessor import Preprocessor, PreprocessedText
from .rule_engine import RuleEngine, GrammarError
from .llm_engine import LLMEngine, LLMResult, LLMError, Intent, TextType, Tone
from .merger import Merger, MergedResult
from core.config import settings


@dataclass
class PipelineResult:
    """
    Result from the complete analysis pipeline.

    Attributes:
        original_text: Original input text
        corrected_text: Final corrected text
        preprocessed: Preprocessing result
        rule_errors: Errors from rule engine
        llm_result: Result from LLM optimization
        merged_result: Final merged result
        mode: Correction mode used
        processing_time_ms: Total processing time
        stage_times: Timing for each stage
        metadata: Additional metadata
    """

    original_text: str
    corrected_text: str
    preprocessed: PreprocessedText
    rule_errors: list
    llm_result: LLMResult
    merged_result: MergedResult
    mode: str
    processing_time_ms: int
    stage_times: Dict[str, int]
    metadata: Dict[str, Any]

    def __post_init__(self):
        """Initialize default values."""
        if self.stage_times is None:
            self.stage_times = {}
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "original_text": self.original_text,
            "corrected_text": self.corrected_text,
            "mode": self.mode,
            "processing_time_ms": self.processing_time_ms,
            "stage_times": self.stage_times,
            "statistics": self.merged_result.statistics,
            "errors": self.merged_result.errors,
            "token_usage": self.llm_result.token_usage,
            "metadata": self.metadata,
        }


class AnalysisPipeline:
    """
    Main analysis pipeline orchestrator.

    Coordinates the 4-stage pipeline:
    1. Preprocessing (sentence splitting, speaker detection)
    2. Rule-based checking (LanguageTool)
    3. LLM optimization (Zhipu AI)
    4. Merging (combine results)

    Attributes:
        preprocessor: Text preprocessor
        rule_engine: Rule-based grammar checker
        llm_engine: LLM optimization engine
        merger: Result merger
        enable_caching: Whether to enable caching
        enable_llm: Whether to use LLM stage
    """

    def __init__(
        self,
        preprocessor: Optional[Preprocessor] = None,
        rule_engine: Optional[RuleEngine] = None,
        llm_engine: Optional[LLMEngine] = None,
        merger: Optional[Merger] = None,
        enable_caching: bool = True,
        enable_llm: bool = True,
    ):
        """
        Initialize the analysis pipeline.

        Args:
            preprocessor: Text preprocessor instance
            rule_engine: Rule engine instance
            llm_engine: LLM engine instance
            merger: Merger instance
            enable_caching: Whether to enable result caching
            enable_llm: Whether to enable LLM optimization
        """
        self.preprocessor = preprocessor or Preprocessor()
        self.rule_engine = rule_engine or RuleEngine()

        # Initialize LLM engine with API key from settings
        if llm_engine is None:
            api_key = settings.ZHIPUAI_API_KEY if settings.ZHIPUAI_API_KEY else None
            self.llm_engine = LLMEngine(api_key=api_key) if api_key else None
        else:
            self.llm_engine = llm_engine

        self.merger = merger or Merger()
        self.enable_caching = enable_caching
        self.enable_llm = enable_llm and bool(self.llm_engine)

    async def analyze(
        self, text: str, mode: str = "accuracy", user_id: Optional[str] = None
    ) -> PipelineResult:
        """
        Analyze and correct text using the 4-stage pipeline.

        Args:
            text: Input text to analyze
            mode: Correction mode (accuracy/natural)
            user_id: Optional user ID for caching

        Returns:
            PipelineResult with analysis results

        Example:
            ```python
            pipeline = AnalysisPipeline()
            result = await pipeline.analyze("She don't like apples.")
            print(result.corrected_text)  # "She doesn't like apples."
            ```

        Raises:
            PipelineError: If analysis fails
        """
        start_time = time.time()
        stage_times = {}

        try:
            # Stage 1: Preprocessing
            stage_start = time.time()
            preprocessed = self.preprocessor.preprocess(text)
            stage_times["preprocessing"] = int((time.time() - stage_start) * 1000)

            # Stage 2: Rule-based checking
            stage_start = time.time()
            rule_errors = self.rule_engine.check(text)
            stage_times["rule_engine"] = int((time.time() - stage_start) * 1000)

            # Stage 3: LLM optimization (optional)
            llm_result = None
            if self.enable_llm:
                stage_start = time.time()
                try:
                    llm_result = await self.llm_engine.optimize(
                        text, mode, preprocessed.metadata.get("intent")
                    )
                    stage_times["llm"] = int((time.time() - stage_start) * 1000)
                except LLMError as e:
                    # Graceful degradation: continue with rule-based results
                    stage_times["llm"] = int((time.time() - stage_start) * 1000)
                    stage_times["llm_error"] = str(e)
                    # Create default intent for rule-only results
                    default_intent = Intent(
                        text_type=TextType.DIALOGUE if preprocessed.is_dialogue else TextType.UNKNOWN,
                        tone=Tone.NEUTRAL,
                        speakers=[],
                        has_chinese=preprocessed.chinese_ratio > 0,
                        confidence=0.5
                    )
                    # Create empty LLM result
                    llm_result = LLMResult(
                        optimized_text=text,
                        detected_intent=default_intent,
                        corrections=[],
                        explanation="LLM optimization failed, using rule-based results only",
                        token_usage={},
                        model="",
                        processing_time_ms=0,
                        metadata={"error": str(e)},
                    )

            # Stage 4: Merging
            stage_start = time.time()
            if llm_result:
                merged_result = self.merger.merge(text, rule_errors, llm_result)
                corrected_text = merged_result.corrected_text
            else:
                # Use rule-based results only
                corrected_text = self._apply_rule_corrections(text, rule_errors)
                merged_result = self._create_rule_only_result(rule_errors)

            stage_times["merging"] = int((time.time() - stage_start) * 1000)

            # Calculate total time
            total_time = int((time.time() - start_time) * 1000)

            return PipelineResult(
                original_text=text,
                corrected_text=corrected_text,
                preprocessed=preprocessed,
                rule_errors=rule_errors,
                llm_result=llm_result,
                merged_result=merged_result,
                mode=mode,
                processing_time_ms=total_time,
                stage_times=stage_times,
                metadata={},
            )

        except Exception as e:
            raise PipelineError(f"Pipeline analysis failed: {str(e)}") from e

    def _apply_rule_corrections(self, text: str, errors: list) -> str:
        """
        Apply rule-based corrections to text.

        Args:
            text: Original text
            errors: List of GrammarError objects

        Returns:
            Corrected text
        """
        if not errors:
            return text

        corrected = text

        sorted_errors = sorted(errors, key=lambda x: x.start_index, reverse=True)

        for error in sorted_errors:
            if error.corrected_span and error.corrected_span != error.original_span:
                start = error.start_index
                end = error.end_index

                if start >= 0 and end <= len(corrected) and start < end:
                    corrected = corrected[:start] + error.corrected_span + corrected[end:]

        return corrected

    def _create_rule_only_result(self, errors: list) -> MergedResult:
        """
        Create MergedResult for rule-based only analysis.

        Args:
            errors: List of GrammarError objects

        Returns:
            MergedResult object
        """
        # TODO: Implement rule-only result creation
        return MergedResult(
            corrected_text="",
            errors=[e.to_dict() for e in errors],
            rule_engine_errors=errors,
            llm_corrections=[],
            overlaps=[],
            statistics={"total_errors": len(errors), "error_types": {}},
            metadata={"mode": "rule_only"},
        )

    async def analyze_batch(
        self, texts: list, mode: str = "accuracy", user_id: Optional[str] = None
    ) -> list:
        """
        Analyze multiple texts in batch.

        Args:
            texts: List of input texts
            mode: Correction mode
            user_id: Optional user ID

        Returns:
            List of PipelineResult objects
        """
        # TODO: Implement batch processing with parallelization
        results = []
        for text in texts:
            result = await self.analyze(text, mode, user_id)
            results.append(result)
        return results

    def get_supported_modes(self) -> list:
        """
        Get list of supported correction modes.

        Returns:
            List of mode names
        """
        return ["accuracy", "natural"]

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of pipeline components.

        Returns:
            Health status dictionary
        """
        # TODO: Implement health checks for each component
        return {
            "status": "healthy",
            "components": {
                "preprocessor": "ok",
                "rule_engine": "ok",
                "llm_engine": "ok" if self.enable_llm else "disabled",
                "merger": "ok",
            },
        }


class PipelineError(Exception):
    """Exception raised when pipeline operations fail."""

    pass
