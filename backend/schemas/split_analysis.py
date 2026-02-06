from typing import Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from .analysis import ErrorDetailResponse

T = TypeVar("T")

class ApiResponse(GenericModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    data: T
    message: str | None = None

class RulesOnlyRequest(BaseModel):
    """Request for Phase 1: Rules-only analysis."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    mode: str = Field(default="accuracy", description="Correction mode (accuracy/natural)")
    language: str | None = Field(default="en-US", description="Language code")

class RulesOnlyData(BaseModel):
    """Data for Phase 1 response."""
    analysis_id: str
    original_text: str
    corrected_text: str
    mode: str
    status: str
    errors: list[ErrorDetailResponse]
    statistics: dict[str, Any]
    processing_time_ms: int
    stage_times: dict[str, int]
    created_at: datetime

class OptimizeLLMRequest(BaseModel):
    """Request for Phase 2: LLM optimization."""
    analysis_id: str = Field(..., description="UUID of the existing analysis")

class OptimizeLLMData(BaseModel):
    """Data for Phase 2 response."""
    analysis_id: str
    original_text: str
    corrected_text: str
    mode: str
    status: str
    token_usage: dict[str, Any]
    statistics: dict[str, Any]
    processing_time_ms: int
    stage_times: dict[str, int]
    created_at: datetime

class LearningAnalysis(BaseModel):
    """Learning analysis structure."""
    error_patterns: list[dict[str, Any]]
    ea_learning_recommendations: list[dict[str, Any]]
    personalized_tips: list[str]
    historical_trend: list[dict[str, Any]] | None = None

class RulesOnlyResponse(ApiResponse[RulesOnlyData]):
    """Response model for rules-only analysis."""
    pass

class OptimizeLLMResponse(ApiResponse[OptimizeLLMData]):
    """Response model for LLM optimization."""
    pass
