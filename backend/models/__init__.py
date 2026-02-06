"""
Database models package.

This package contains all SQLAlchemy database models.
"""

from .base import Base, TimestampMixin, SoftDeleteMixin, get_uuid
from .user import User, UserSettings, APICredit
from .analysis import (
    Analysis,
    ErrorDetail,
    Tag,
    AnalysisTag,
    AnalysisCache
)
from .session import get_db, engine, SessionLocal, init_db, drop_db

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "get_uuid",

    # User models
    "User",
    "UserSettings",
    "APICredit",

    # Analysis models
    "Analysis",
    "ErrorDetail",
    "Tag",
    "AnalysisTag",
    "AnalysisCache",

    # LLM Provider models
    "LLMProvider",
    "UserLLMConfig",

    # Session management
    "get_db",
    "engine",
    "SessionLocal",
    "init_db",
    "drop_db",
]
