"""
Generic helper functions.

Common utility functions used across the application.
"""

import hashlib
import re
from typing import Optional, Any, Dict, List
from datetime import datetime


def generate_hash(content: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of content.

    Args:
        content: Content to hash
        algorithm: Hash algorithm (md5, sha256, sha512)

    Returns:
        Hexadecimal hash string

    Example:
        ```python
        hash = generate_hash("hello world")
        assert len(hash) == 64  # SHA-256 produces 64 hex chars
        ```
    """
    # TODO: Implement hash generation
    hash_func = getattr(hashlib, algorithm, hashlib.sha256)
    content_bytes = content.encode('utf-8')
    return hash_func(content_bytes).hexdigest()


def sanitize_html(html: str) -> str:
    """
    Sanitize HTML by removing dangerous tags and attributes.

    Args:
        html: HTML string to sanitize

    Returns:
        Sanitized HTML string

    Example:
        ```python
        clean = sanitize_html("<script>alert('xss')</script>")
        assert "<script>" not in clean
        ```
    """
    # TODO: Implement HTML sanitization
    # Use bleach or similar library in production
    # For now, remove script tags
    return re.sub(r'<script.*?>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text

    Example:
        ```python
        result = truncate_text("This is a very long text", 10)
        assert result == "This is..."
        ```
    """
    # TODO: Implement text truncation
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime object
        format: Format string

    Returns:
        Formatted datetime string

    Example:
        ```python
        formatted = format_datetime(datetime.utcnow())
        assert len(formatted) == 19
        ```
    """
    # TODO: Implement datetime formatting
    return dt.strftime(format)


def calculate_age(birthdate: datetime) -> int:
    """
    Calculate age from birthdate.

    Args:
        birthdate: Birth date

    Returns:
        Age in years

    Example:
        ```python
        from datetime import datetime, timedelta
        birth = datetime.utcnow() - timedelta(days=365*30)
        age = calculate_age(birth)
        assert age == 30
        ```
    """
    # TODO: Implement age calculation
    today = datetime.utcnow()
    years = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )
    return years


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries deeply.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary

    Example:
        ```python
        result = merge_dicts({"a": 1}, {"b": 2}, {"c": 3})
        assert result == {"a": 1, "b": 2, "c": 3}
        ```
    """
    # TODO: Implement deep merge
    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks

    Example:
        ```python
        chunks = chunk_list([1, 2, 3, 4, 5], 2)
        assert chunks == [[1, 2], [3, 4], [5]]
        ```
    """
    # TODO: Implement list chunking
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise

    Example:
        ```python
        assert is_valid_email("user@example.com") == True
        assert is_valid_email("invalid") == False
        ```
    """
    # TODO: Implement email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
