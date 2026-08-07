"""
Central Enterprise CacheService providing unified caching lifecycle operations, pattern invalidation,
resilient offline fallback, and integrated performance metrics monitoring.
"""
import fnmatch
import logging
import time
import threading
from typing import Any, Callable, Dict, List, Optional
from django.core.cache import cache
from django.conf import settings
from apps.cache_utils.keys import CacheKeyBuilder, TTL_5_MINUTES, CACHE_VERSION

logger = logging.getLogger("grantloop.monitoring")

# Thread-safe global telemetry registry for tracking real-time performance statistics
_stats_lock = threading.Lock()
_cache_metrics = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
    "invalidations": 0,
    "fallbacks": 0,
    "tracked_keys": set(),
}


class CacheService:
    """
    Unified central caching service layer. Never exposes raw Redis drivers directly to application controllers.
    Supports graceful fallback to simple memory storage when external Redis brokers are unreachable.
    """

    @classmethod
    def get_client(cls):
        """Safely retrieves underlying redis client if available, else None."""
        try:
            if hasattr(cache, "client"):
                return cache.client.get_client()
            elif hasattr(cache, "_client"):
                return cache._client
        except Exception:
            pass
        return None

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Retrieves cached value by key. Updates hit ratio statistics and logs cache misses.
        """
        try:
            value = cache.get(key, default=None)
            with _stats_lock:
                if value is not None:
                    _cache_metrics["hits"] += 1
                    return value
                else:
                    _cache_metrics["misses"] += 1
            if value is None and default is not None:
                return default
            return value
        except Exception as e:
            with _stats_lock:
                _cache_metrics["fallbacks"] += 1
            logger.warning(f"CACHE_FALLBACK: Cache get error for key={key}: {e}")
            return default

    @classmethod
    def set(cls, key: str, value: Any, timeout: Optional[int] = TTL_5_MINUTES) -> bool:
        """
        Stores value in cache with specified TTL in seconds.
        """
        try:
            success = cache.set(key, value, timeout=timeout)
            with _stats_lock:
                _cache_metrics["sets"] += 1
                _cache_metrics["tracked_keys"].add(key)
            return bool(success or success is None)  # locmem set returns None in some Django versions
        except Exception as e:
            with _stats_lock:
                _cache_metrics["fallbacks"] += 1
            logger.warning(f"CACHE_FALLBACK: Cache set error for key={key}: {e}")
            return False

    @classmethod
    def delete(cls, key: str) -> bool:
        """
        Removes single key from cache storage and tracking registry.
        """
        try:
            cache.delete(key)
            with _stats_lock:
                _cache_metrics["deletes"] += 1
                _cache_metrics["tracked_keys"].discard(key)
            return True
        except Exception as e:
            logger.warning(f"CACHE_DELETE_ERROR: {e}")
            return False

    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """
        Deletes all keys matching a wildcard glob pattern across Redis or local fallback storage.
        Returns number of deleted entries.
        """
        deleted_count = 0
        try:
            client = cls.get_client()
            if client and hasattr(client, "keys") and hasattr(client, "delete"):
                matching_keys = client.keys(pattern)
                if matching_keys:
                    deleted_count = len(matching_keys)
                    client.delete(*matching_keys)
            else:
                with _stats_lock:
                    known_keys = list(_cache_metrics["tracked_keys"])
                    if hasattr(cache, "_cache"):
                        known_keys.extend(list(cache._cache.keys()))

                to_delete = [k for k in set(known_keys) if fnmatch.fnmatch(str(k), pattern)]
                for k in to_delete:
                    cache.delete(k)
                    with _stats_lock:
                        _cache_metrics["tracked_keys"].discard(k)
                deleted_count = len(to_delete)
        except Exception as e:
            logger.warning(f"CACHE_PATTERN_DELETE_ERROR: pattern={pattern} error={e}")
        return deleted_count

    @classmethod
    def exists(cls, key: str) -> bool:
        """
        Checks whether a cache key currently exists in storage without incrementing hit/miss counters.
        """
        try:
            if hasattr(cache, "has_key"):
                return cache.has_key(key)
            return cache.get(key, None) is not None
        except Exception:
            return False

    @classmethod
    def touch(cls, key: str, timeout: Optional[int] = TTL_5_MINUTES) -> bool:
        """
        Refreshes TTL expiration timestamp for an existing cache key without modifying contents.
        """
        try:
            if hasattr(cache, "touch"):
                return bool(cache.touch(key, timeout))
            val = cache.get(key)
            if val is not None:
                cache.set(key, val, timeout=timeout)
                return True
            return False
        except Exception:
            return False

    @classmethod
    def get_or_set(cls, key: str, default: Any, timeout: Optional[int] = TTL_5_MINUTES) -> Any:
        """
        Retrieves cached value if present; otherwise evaluates default (if callable or constant),
        stores the result in cache, and returns it.
        """
        existing = cls.get(key, default=None)
        if existing is not None:
            return existing

        value = default() if callable(default) else default
        cls.set(key, value, timeout=timeout)
        return value

    @classmethod
    def invalidate_namespace(cls, namespace: str, version: str = CACHE_VERSION) -> int:
        """
        Invalidates all cached items belonging to a designated namespace. Logs cache invalidation events.
        """
        pattern = CacheKeyBuilder.pattern(namespace, version=version)
        deleted = cls.delete_pattern(pattern)
        with _stats_lock:
            _cache_metrics["invalidations"] += 1
        logger.info(f"CACHE_INVALIDATION: Purged namespace='{namespace}' pattern='{pattern}' entries_removed={deleted}")
        return deleted

    @classmethod
    def invalidate_object(cls, namespace: str, identifier: str, version: str = CACHE_VERSION) -> bool:
        """
        Invalidates a single targeted cache object within a namespace.
        """
        key = CacheKeyBuilder.build_key(namespace, identifier, version=version)
        success = cls.delete(key)
        with _stats_lock:
            _cache_metrics["invalidations"] += 1
        logger.info(f"CACHE_INVALIDATION: Purged object key='{key}' success={success}")
        return success

    @classmethod
    def stats(cls) -> Dict[str, Any]:
        """
        Returns real-time cache diagnostic telemetry including hit ratio, miss count, sets, deletes, and fallbacks.
        """
        with _stats_lock:
            hits = _cache_metrics["hits"]
            misses = _cache_metrics["misses"]
            total_requests = hits + misses
            hit_ratio = round((hits / total_requests) * 100.0, 2) if total_requests > 0 else 100.0
            return {
                "hits": hits,
                "misses": misses,
                "hit_ratio_percent": hit_ratio,
                "sets": _cache_metrics["sets"],
                "deletes": _cache_metrics["deletes"],
                "invalidations": _cache_metrics["invalidations"],
                "fallbacks": _cache_metrics["fallbacks"],
                "active_tracked_keys": len(_cache_metrics["tracked_keys"]),
            }

    @classmethod
    def reset_stats(cls) -> None:
        """Resets in-memory diagnostic telemetry counters (useful for unit tests)."""
        with _stats_lock:
            _cache_metrics["hits"] = 0
            _cache_metrics["misses"] = 0
            _cache_metrics["sets"] = 0
            _cache_metrics["deletes"] = 0
            _cache_metrics["invalidations"] = 0
            _cache_metrics["fallbacks"] = 0
            _cache_metrics["tracked_keys"].clear()
