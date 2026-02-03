"""
Analysis-related database models.

This module contains SQLAlchemy models for text analyses, error details,
tags, and caching.
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Index, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from datetime import datetime
import uuid

from .base import Base, TimestampMixin, SoftDeleteMixin


class Analysis(Base, TimestampMixin, SoftDeleteMixin):
    """
    Text analysis record model.

    Stores both original and corrected text, along with metadata
    about the analysis process.

    Attributes:
        id: Unique analysis identifier (UUID)
        user_id: User ID who created the analysis (foreign key, nullable)
        original_text: Original input text
        corrected_text: Corrected output text
        mode: Correction mode used (accuracy/natural)
        text_type: Detected text type (dialogue/email/essay/etc.)
        statistics: Analysis statistics (error counts, etc.) as JSONB
        processing_time_ms: Processing time in milliseconds
        is_cached: Whether result was retrieved from cache
        token_usage: Token usage statistics as JSONB
        user: Related User object
        errors: Error details (one-to-many relationship)

    Properties:
        token_count: Get token statistics

    Methods:
        validate_mode: Validate correction mode
    """

    __tablename__ = "ea_analyses"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User association (nullable for anonymous users)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ea_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Text content
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)

    # Analysis parameters
    mode = Column(String(50), nullable=False)  # accuracy, natural
    text_type = Column(String(50), default="unknown")  # dialogue, email, essay, etc.

    # Statistics (JSONB for flexibility)
    # Format: {
    #   "total_errors": 5,
    #   "error_types": {"grammar": 3, "tense": 2},
    #   "sentence_count": 10,
    #   "word_count": 150
    # }
    statistics = Column(JSONB, default=dict, nullable=False)

    # Performance metrics
    processing_time_ms = Column(Integer, default=0)
    is_cached = Column(Boolean, default=False)

    # Token usage statistics
    # Format: {
    #   "input_tokens": 150,
    #   "output_tokens": 300,
    #   "total_tokens": 450,
    #   "estimated_cost": 0.0009,
    #   "model": "glm-4-flash",
    #   "llm_tokens": {"input": 100, "output": 200, "total": 300}
    # }
    token_usage = Column(JSONB, nullable=False, default=dict)

    # Relationships
    user = relationship("User", back_populates="analyses")
    errors = relationship(
        "ErrorDetail",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )

    # Composite indexes
    __table_args__ = (
        Index('ix_ea_analysis_user_date', 'user_id', 'created_at'),
        Index('ix_ea_analysis_user_deleted', 'user_id', 'is_deleted', 'created_at'),
        Index('ix_ea_analysis_mode_type', 'mode', 'text_type'),
        Index('ix_ea_analysis_cache', 'is_cached', 'created_at'),
    )

    @validates('mode')
    def validate_mode(self, key: str, mode: str) -> str:
        """
        Validate correction mode.

        Args:
            key: Field name
            mode: Mode to validate

        Returns:
            Validated mode

        Raises:
            ValueError: If mode is invalid
        """
        if mode not in ['accuracy', 'natural']:
            raise ValueError("Mode must be 'accuracy' or 'natural'")
        return mode

    @property
    def token_count(self) -> dict:
        """
        Get token statistics with defaults.

        Returns:
            Dictionary with token usage stats
        """
        return self.token_usage or {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }

    @property
    def error_count(self) -> int:
        """Get total error count from statistics."""
        return self.statistics.get("total_errors", 0)


class ErrorDetail(Base):
    """
    Error detail model.

    Stores individual error information for each analysis.

    Attributes:
        id: Unique error identifier (UUID)
        analysis_id: Analysis ID (foreign key)
        error_type: Main error category (grammar/tense/word_choice/mixed_language)
        error_subtype: Specific error subtype
        original_span: Original text with error
        corrected_span: Corrected text
        start_index: Start position in original text
        end_index: End position in original text
        explanation: Human-readable explanation
        rule_description: Technical rule description
        severity: Error severity (low/medium/high)
        is_resolved: Whether error has been resolved
        analysis: Related Analysis object
    """

    __tablename__ = "ea_error_details"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Association
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ea_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Error classification
    error_type = Column(String(50), nullable=False, index=True)
    error_subtype = Column(String(100))

    # Error content
    original_span = Column(String(500), nullable=False)
    corrected_span = Column(String(500), nullable=False)

    # Position information
    start_index = Column(Integer, nullable=False)
    end_index = Column(Integer, nullable=False)

    # Explanations
    explanation = Column(Text)
    rule_description = Column(Text)

    # Status
    severity = Column(String(20), default="medium")
    is_resolved = Column(Boolean, default=False)

    # Relationship
    analysis = relationship("Analysis", back_populates="errors")

    # Indexes
    __table_args__ = (
        Index('ix_ea_error_analysis_severity', 'analysis_id', 'severity'),
        Index('ix_ea_error_type', 'error_type', 'error_subtype'),
    )

    @validates('error_type')
    def validate_error_type(self, key: str, error_type: str) -> str:
        """
        Validate error type.

        Args:
            key: Field name
            error_type: Error type to validate

        Returns:
            Validated error type

        Raises:
            ValueError: If error type is invalid
        """
        valid_types = {
            'grammar',
            'tense',
            'word_choice',
            'mixed_language',
            'spelling',
            'punctuation',
            'style'
        }
        if error_type not in valid_types:
            raise ValueError(f"Invalid error_type. Must be one of: {valid_types}")
        return error_type

    @validates('severity')
    def validate_severity(self, key: str, severity: str) -> str:
        """
        Validate severity level.

        Args:
            key: Field name
            severity: Severity to validate

        Returns:
            Validated severity

        Raises:
            ValueError: If severity is invalid
        """
        if severity not in ['low', 'medium', 'high']:
            raise ValueError("Severity must be 'low', 'medium', or 'high'")
        return severity


class Tag(Base):
    """
    User-defined tag model.

    Allows users to organize and categorize their analyses.

    Attributes:
        id: Unique tag identifier (UUID)
        user_id: User ID who owns the tag (foreign key)
        name: Tag name
        color: Tag color for UI display
        description: Optional tag description
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "ea_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ea_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name = Column(String(100), nullable=False)
    color = Column(String(20), default="blue")
    description = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index
    __table_args__ = (
        Index('ix_ea_tags_user_name', 'user_id', 'name'),
    )


class AnalysisTag(Base):
    """
    Many-to-many relationship between Analysis and Tag.

    Attributes:
        analysis_id: Analysis ID (foreign key, primary key)
        tag_id: Tag ID (foreign key, primary key)
        created_at: Timestamp when tag was assigned
    """

    __tablename__ = "ea_analysis_tags"

    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ea_analyses.id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ea_tags.id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisCache(Base):
    """
    Analysis result cache model.

    Caches analysis results based on content hash to avoid
    reprocessing identical text.

    Attributes:
        content_hash: SHA-256 hash of original text + mode (primary key)
        cached_result: Cached analysis result as JSONB
        created_at: Cache creation timestamp
        expires_at: Cache expiration timestamp

    Properties:
        is_valid: Whether cache entry is still valid
    """

    __tablename__ = "ea_analysis_cache"

    content_hash = Column(String(64), primary_key=True)
    cached_result = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    @property
    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        return datetime.utcnow() < self.expires_at
