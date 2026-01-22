"""
Base models and mixins for SQLAlchemy models.

This module provides base classes and mixins that are used across all database models.
"""

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base class for all models
Base = declarative_base()


class TimestampMixin:
    """
    Mixin class that adds timestamp fields to a model.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class SoftDeleteMixin:
    """
    Mixin class that adds soft delete functionality to a model.

    Instead of actually deleting records, this marks them as deleted.
    This allows for data recovery and maintains referential integrity.

    Attributes:
        deleted_at: Timestamp when the record was soft deleted (None if not deleted)
        is_deleted: Boolean flag indicating if the record is deleted

    Methods:
        soft_delete: Marks the record as deleted
    """

    deleted_at = Column(DateTime, nullable=True, index=True)
    is_deleted = Column(Boolean, default=False, index=True, nullable=False)

    def soft_delete(self) -> None:
        """
        Mark the record as deleted by setting the deleted_at timestamp
        and is_deleted flag.
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
