"""
Analysis-related schemas.

Pydantic models for text analysis requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalyzeRequest(BaseModel):
    """Text analysis request."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    mode: str = Field(default="accuracy", description="Correction mode (accuracy/natural)")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "text": "She don't like apples.",
                "mode": "accuracy"
            }
        }


class ErrorDetailResponse(BaseModel):
    """Single error detail."""
    error_type: str = Field(..., description="Error type")
    error_subtype: Optional[str] = Field(None, description="Error subtype")
    original_span: str = Field(..., description="Original text with error")
    corrected_span: str = Field(..., description="Corrected text")
    start_index: int = Field(..., description="Start position in original text")
    end_index: int = Field(..., description="End position in original text")
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    rule_description: Optional[str] = Field(None, description="Technical rule description")
    severity: str = Field(default="medium", description="Error severity (low/medium/high)")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error_type": "tense",
                "error_subtype": "subject_verb_agreement",
                "original_span": "don't",
                "corrected_span": "doesn't",
                "start_index": 4,
                "end_index": 9,
                "explanation": "Third-person singular requires 'doesn't'",
                "rule_description": "Subject-verb agreement",
                "severity": "high"
            }
        }


class AnalyzeResponse(BaseModel):
    """Text analysis response."""
    analysis_id: str = Field(..., description="Analysis record ID")
    original_text: str = Field(..., description="Original input text")
    corrected_text: str = Field(..., description="Corrected text")
    mode: str = Field(..., description="Correction mode used")
    errors: List[ErrorDetailResponse] = Field(default_factory=list, description="List of errors")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Analysis statistics")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    token_usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage statistics")
    created_at: datetime = Field(..., description="Analysis timestamp")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                "original_text": "She don't like apples.",
                "corrected_text": "She doesn't like apples.",
                "mode": "accuracy",
                "errors": [
                    {
                        "error_type": "tense",
                        "error_subtype": "subject_verb_agreement",
                        "original_span": "don't",
                        "corrected_span": "doesn't",
                        "start_index": 4,
                        "end_index": 9,
                        "explanation": "Third-person singular requires 'doesn't'",
                        "rule_description": "Subject-verb agreement",
                        "severity": "high"
                    }
                ],
                "statistics": {
                    "total_errors": 1,
                    "error_types": {"tense": 1}
                },
                "processing_time_ms": 523,
                "token_usage": {
                    "input_tokens": 5,
                    "output_tokens": 10,
                    "total_tokens": 15
                },
                "created_at": "2026-01-22T10:00:00Z"
            }
        }
