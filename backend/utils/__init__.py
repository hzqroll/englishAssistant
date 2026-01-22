"""
Utilities package.

This package contains utility functions and helpers.
"""

from .logger import JSONFormatter, setup_logging
from .helpers import (
    generate_hash,
    sanitize_html,
    truncate_text,
    format_datetime,
    calculate_age,
    merge_dicts,
    chunk_list,
    is_valid_email
)

__all__ = [
    "JSONFormatter",
    "setup_logging",
    "generate_hash",
    "sanitize_html",
    "truncate_text",
    "format_datetime",
    "calculate_age",
    "merge_dicts",
    "chunk_list",
    "is_valid_email",
]
