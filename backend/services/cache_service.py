"""
Cache service.

Handles in-memory caching for MVP version (no Redis required).
"""

from typing import Optional, Any, Dict, List
import json
import hashlib
from datetime import datetime, timedelta


class CacheService:
    """
    In-memory cache service (MVP version).

    Provides simple caching without Redis dependency.
    Suitable for V1 deployment and development.

    Attributes:
        cache: In-memory cache dictionary
        default_ttl: Default time-to-live in seconds
        max_size: Maximum number of cache entries
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize cache service.

        Args:
            default_ttl: Default TTL in seconds
            max_size: Maximum number of cache entries
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None

        Example:
            ```python
            service = CacheService()
            value = await service.get("user:123")
            ```
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]

        if datetime.utcnow() > entry["expires"]:
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (uses default if not specified)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            await service.set("user:123", {"name": "John"}, ttl=60)
            ```
        """
        if len(self.cache) >= self.max_size:
            self._evict_expired()

        expires = datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl)

        self.cache[key] = {"value": value, "created": datetime.utcnow(), "expires": expires}

        return True

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise

        Example:
            ```python
            await service.delete("user:123")
            ```
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if key not in self.cache:
            return False

        entry = self.cache[key]

        if datetime.utcnow() > entry["expires"]:
            del self.cache[key]
            return False

        return True

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary mapping keys to values

        Example:
            ```python
            values = await service.get_many(["user:123", "user:456"])
            ```
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if all successful, False otherwise

        Example:
            ```python
            await service.set_many({"user:123": data1, "user:456": data2})
            ```
        """
        for key, value in mapping.items():
            self.set(key, value, ttl)
        return True

    def clear(self) -> bool:
        """
        Clear all cached data.

        WARNING: Use with caution.

        Returns:
            True if successful
        """
        self.cache.clear()
        return True

    def clear_expired(self) -> int:
        """
        Clear only expired entries from cache.

        Returns:
            Number of entries cleared
        """
        expired_keys = []

        for key, entry in self.cache.items():
            if datetime.utcnow() > entry["expires"]:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        now = datetime.utcnow()

        active_count = sum(1 for entry in self.cache.values() if now <= entry["expires"])

        expired_count = len(self.cache) - active_count

        return {
            "total_entries": len(self.cache),
            "active_entries": active_count,
            "expired_entries": expired_count,
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        }

    def _evict_expired(self) -> int:
        """
        Remove expired entries to free space.

        Returns:
            Number of entries evicted
        """
        evicted = 0
        now = datetime.utcnow()

        keys_to_remove = []

        for key, entry in self.cache.items():
            if now > entry["expires"]:
                keys_to_remove.append(key)
                evicted += 1

        for key in keys_to_remove:
            del self.cache[key]

        if evicted > 0:
            keys_to_remove = []
            now = datetime.utcnow()

            for key, entry in self.cache.items():
                if now > entry["expires"]:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.cache[key]

        return evicted


class CacheServiceError(Exception):
    """Exception raised for cache service errors."""

    pass
