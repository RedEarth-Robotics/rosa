import hashlib
import json
import threading
import time
from collections import OrderedDict
from typing import Any, Optional


class ToolResultCache:
    """LRU cache for tool results with TTL support."""

    def __init__(
        self,
        enabled: bool = True,
        default_ttl: float = 2.0,
        max_entries: int = 500,
        max_entry_size: int = 1024 * 1024,  # 1MB
    ):
        self._enabled = enabled
        self._default_ttl = default_ttl
        self._max_entries = max_entries
        self._max_entry_size = max_entry_size
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._expiry: dict[str, float] = {}
        self._lock = threading.RLock()

    def _make_key(self, tool_name: str, params: dict) -> str:
        """Create a cache key from tool name and parameters."""
        param_str = json.dumps(params, sort_keys=True, default=str)
        return f"{tool_name}:{hashlib.md5(param_str.encode()).hexdigest()}"

    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry has expired."""
        if key not in self._expiry:
            return True
        return time.time() > self._expiry[key]

    def _cleanup_expired(self):
        """Remove expired entries."""
        now = time.time()
        expired = [k for k, expiry in self._expiry.items() if now > expiry]
        for key in expired:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)

    def get(self, tool_name: str, params: dict) -> Optional[Any]:
        """Get a cached result if available and not expired."""
        if not self._enabled:
            return None

        key = self._make_key(tool_name, params)
        with self._lock:
            self._cleanup_expired()
            if key not in self._cache or self._is_expired(key):
                self._cache.pop(key, None)
                self._expiry.pop(key, None)
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]

    def set(self, tool_name: str, params: dict, result: Any, ttl: Optional[float] = None) -> bool:
        """Cache a tool result. Returns True if cached, False if too large or disabled."""
        if not self._enabled:
            return False

        # Check entry size (rough estimate)
        try:
            result_size = len(json.dumps(result, default=str))
        except (TypeError, ValueError):
            result_size = 0
        if result_size > self._max_entry_size:
            return False

        key = self._make_key(tool_name, params)
        with self._lock:
            self._cleanup_expired()

            # Evict oldest if at capacity
            while len(self._cache) >= self._max_entries:
                oldest = next(iter(self._cache))
                self._cache.pop(oldest)
                self._expiry.pop(oldest, None)

            self._cache[key] = result
            self._expiry[key] = time.time() + (ttl if ttl is not None else self._default_ttl)
            self._cache.move_to_end(key)
            return True

    def clear(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()

    def set_enabled(self, enabled: bool):
        """Enable or disable caching."""
        self._enabled = enabled
        if not enabled:
            self.clear()
