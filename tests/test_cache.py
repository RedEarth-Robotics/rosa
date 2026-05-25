import time
import pytest
from src.rosa.cache.tool_cache import ToolResultCache


def test_cache_basic_get_set():
    cache = ToolResultCache()
    cache.set("tool1", {"args": {"x": 1}}, "result1")
    assert cache.get("tool1", {"args": {"x": 1}}) == "result1"


def test_cache_miss_returns_none():
    cache = ToolResultCache()
    assert cache.get("nonexistent", {}) is None


def test_cache_ttl_expiration():
    cache = ToolResultCache(default_ttl=0.1)
    cache.set("tool1", {}, "result1")
    assert cache.get("tool1", {}) == "result1"
    time.sleep(0.15)
    assert cache.get("tool1", {}) is None


def test_cache_per_key_ttl():
    cache = ToolResultCache(default_ttl=60)
    cache.set("tool1", {}, "result1", ttl=0.1)
    assert cache.get("tool1", {}) == "result1"
    time.sleep(0.15)
    assert cache.get("tool1", {}) is None


def test_cache_lru_eviction():
    cache = ToolResultCache(max_entries=2)
    cache.set("tool1", {}, "result1")
    cache.set("tool2", {}, "result2")
    cache.set("tool3", {}, "result3")
    assert cache.get("tool1", {}) is None  # Evicted
    assert cache.get("tool2", {}) == "result2"
    assert cache.get("tool3", {}) == "result3"


def test_cache_max_entry_size():
    cache = ToolResultCache(max_entry_size=10)
    cache.set("tool1", {}, "small")
    assert cache.get("tool1", {}) == "small"
    cache.set("tool2", {}, "x" * 100)  # Too large
    assert cache.get("tool2", {}) is None


def test_cache_clear():
    cache = ToolResultCache()
    cache.set("tool1", {}, "result1")
    cache.clear()
    assert cache.get("tool1", {}) is None


def test_cache_disabled():
    cache = ToolResultCache(enabled=False)
    cache.set("tool1", {}, "result1")
    assert cache.get("tool1", {}) is None


import threading
from src.rosa.cache.in_flight_requests import RequestCoalescer


def test_coalescer_single_request():
    coalescer = RequestCoalescer()
    result = coalescer.execute("key1", lambda: "result1")
    assert result == "result1"


def test_coalescer_dedupes_concurrent_requests():
    coalescer = RequestCoalescer()
    call_count = [0]
    def slow_op():
        call_count[0] += 1
        time.sleep(0.05)
        return "shared_result"

    results = []
    def worker():
        results.append(coalescer.execute("key1", slow_op))

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert call_count[0] == 1
    assert results[0] == "shared_result"
    assert results[1] == "shared_result"


def test_coalescer_different_keys_not_deduped():
    coalescer = RequestCoalescer()
    call_count = [0]
    def op():
        call_count[0] += 1
        return f"result{call_count[0]}"

    r1 = coalescer.execute("key1", op)
    r2 = coalescer.execute("key2", op)
    assert call_count[0] == 2
    assert r1 == "result1"
    assert r2 == "result2"


from unittest.mock import Mock, patch
from src.rosa.cache.ros_state_cache import ROSStateCache


def test_ros_cache_topic_list():
    cache = ROSStateCache(ros_version=1, enabled=True)
    cache._cache["topics"] = (["/topic1", "/topic2"], time.time() + 60)
    cache._cache["checksum"] = ("abc123", time.time() + 60)
    assert cache.get_topics() == ["/topic1", "/topic2"]


def test_ros_cache_checksum_changed_invalidates():
    cache = ROSStateCache(ros_version=1, enabled=True)
    cache._current_checksum = "old"
    cache._cache["topics"] = (["/old"], time.time() + 60)
    cache._cache["checksum"] = ("old", time.time() + 60)

    # Simulate changed checksum
    cache._cache["checksum"] = ("new", time.time() + 60)
    result = cache.get_topics()
    # Should return empty because we don't have topics for new checksum
    assert result == []


def test_ros_cache_ros2_mode():
    cache = ROSStateCache(ros_version=2, enabled=True)
    cache._cache["topics"] = (["/topic1"], time.time() + 60)
    cache._cache["checksum"] = ("checksum", time.time() + 60)
    assert cache.get_topics() == ["/topic1"]


def test_ros_cache_disabled():
    cache = ROSStateCache(ros_version=1, enabled=False)
    assert cache.get_topics() is None
    assert cache.get_nodes() is None


def test_ros_cache_ttl_expiration():
    cache = ROSStateCache(ros_version=1, enabled=True, ttl=0.1)
    cache._cache["topics"] = (["/topic1"], time.time() + 0.1)
    assert cache.get_topics() == ["/topic1"]
    time.sleep(0.15)
    assert cache.get_topics() is None
