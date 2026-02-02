"""
Text correction pipeline package.

This package implements the 4-stage text correction pipeline:
1. Preprocessing
2. Rule-based checking
3. LLM optimization
4. Merging
"""

from .preprocessor import Preprocessor, PreprocessedText, Message
from .rule_engine import RuleEngine, GrammarError, ErrorType, Severity, RuleEngineError
from .llm_engine import LLMEngine, LLMResult, LLMError, Intent, TextType, Tone
from .merger import Merger, MergedResult, OverlapInfo, ConflictResolution, MergerError
from .pipeline import AnalysisPipeline, PipelineResult, PipelineError

__all__ = [
    # Preprocessor
    "Preprocessor",
    "PreprocessedText",
    "Message",

    # Rule Engine
    "RuleEngine",
    "GrammarError",
    "ErrorType",
    "Severity",
    "RuleEngineError",

    # LLM Engine
    "LLMEngine",
    "LLMResult",
    "LLMError",
    "Intent",
    "TextType",
    "Tone",

    # Merger
    "Merger",
    "MergedResult",
    "OverlapInfo",
    "ConflictResolution",
    "MergerError",

    # Pipeline
    "AnalysisPipeline",
    "PipelineResult",
    "PipelineError",
]
