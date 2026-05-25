import hashlib
import subprocess
import threading
import time
from typing import Any, List, Optional


class ROSStateCache:
    """Cache for ROS system state with change detection and invalidation."""

    def __init__(
        self,
        ros_version: int,
        enabled: bool = True,
        ttl: float = 2.0,
        checksum_interval: float = 1.0,
    ):
        self._ros_version = ros_version
        self._enabled = enabled
        self._ttl = ttl
        self._checksum_interval = checksum_interval
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = threading.RLock()
        self._last_checksum_check = 0.0
        self._current_checksum = ""

    def _is_expired(self, entry_time: float) -> bool:
        return time.time() > entry_time

    def _get_cached(self, key: str) -> Optional[Any]:
        if not self._enabled:
            return None
        with self._lock:
            if key not in self._cache:
                return None
            value, expiry = self._cache[key]
            if self._is_expired(expiry):
                del self._cache[key]
                return None
            return value

    def _set_cached(self, key: str, value: Any, ttl: Optional[float] = None):
        if not self._enabled:
            return
        with self._lock:
            self._cache[key] = (value, time.time() + (ttl if ttl else self._ttl))

    def _compute_checksum_ros1(self) -> str:
        """Compute checksum from ROS1 master system state."""
        try:
            import rosgraph
            master = rosgraph.masterapi.Master("/rosout")
            pubs, subs, srvs = master.getSystemState()
            # Create deterministic string representation
            data = []
            for topic, nodes in sorted(pubs):
                data.append(f"P:{topic}:{','.join(sorted(nodes))}")
            for topic, nodes in sorted(subs):
                data.append(f"S:{topic}:{','.join(sorted(nodes))}")
            for service, nodes in sorted(srvs):
                data.append(f"V:{service}:{','.join(sorted(nodes))}")
            return hashlib.md5("\n".join(data).encode()).hexdigest()
        except Exception:
            return ""

    def _compute_checksum_ros2(self) -> str:
        """Compute checksum from ROS2 command outputs."""
        try:
            parts = []
            for cmd in ["ros2 topic list", "ros2 node list", "ros2 service list"]:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=5
                )
                if result.returncode != 0:
                    return ""
                parts.append(result.stdout)
            return hashlib.md5("\n".join(parts).encode()).hexdigest()
        except Exception:
            return ""

    def _compute_checksum(self) -> str:
        if self._ros_version == 1:
            return self._compute_checksum_ros1()
        return self._compute_checksum_ros2()

    def _check_for_changes(self) -> bool:
        """Check if ROS system state has changed. Returns True if changed."""
        now = time.time()
        if now - self._last_checksum_check < self._checksum_interval:
            return False

        new_checksum = self._compute_checksum()
        self._last_checksum_check = now

        with self._lock:
            if not new_checksum:
                cached = self._cache.get("checksum")
                if cached:
                    new_checksum = cached[0]

            if new_checksum != self._current_checksum:
                old_checksum = self._current_checksum
                self._current_checksum = new_checksum
                # Only invalidate if we've seen a previous checksum
                if old_checksum:
                    for key in list(self._cache.keys()):
                        if key not in ("checksum",):
                            if key in ("topics", "nodes", "services"):
                                self._cache[key] = ([], time.time() + self._ttl)
                            else:
                                del self._cache[key]
                    return True
                return False
            return False

    def get_topics(self) -> Optional[List[str]]:
        self._check_for_changes()
        return self._get_cached("topics")

    def set_topics(self, topics: List[str]):
        self._set_cached("topics", topics)

    def get_nodes(self) -> Optional[List[str]]:
        self._check_for_changes()
        return self._get_cached("nodes")

    def set_nodes(self, nodes: List[str]):
        self._set_cached("nodes", nodes)

    def get_services(self) -> Optional[List[str]]:
        self._check_for_changes()
        return self._get_cached("services")

    def set_services(self, services: List[str]):
        self._set_cached("services", services)

    def get_params(self, namespace: str = "/") -> Optional[List[str]]:
        self._check_for_changes()
        return self._get_cached(f"params:{namespace}")

    def set_params(self, namespace: str, params: List[str]):
        self._set_cached(f"params:{namespace}", params)

    def get_topic_info(self, topic: str) -> Optional[dict]:
        return self._get_cached(f"topic_info:{topic}")

    def set_topic_info(self, topic: str, info: dict):
        self._set_cached(f"topic_info:{topic}", info, ttl=3.0)

    def get_node_info(self, node: str) -> Optional[str]:
        return self._get_cached(f"node_info:{node}")

    def set_node_info(self, node: str, info: str):
        self._set_cached(f"node_info:{node}", info, ttl=5.0)

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._current_checksum = ""

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if not enabled:
            self.clear()
