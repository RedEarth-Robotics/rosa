#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time
import threading
from contextlib import contextmanager
from typing import Dict, Any


class ROSAProfiler:
    """Performance profiler for ROSA operations."""

    def __init__(self):
        self._lock = threading.Lock()
        self._metrics: Dict[str, Any] = {}
        self._enabled = True

    @contextmanager
    def time_operation(self, name: str):
        """Context manager to time an operation."""
        if not self._enabled:
            yield
            return

        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            with self._lock:
                if name not in self._metrics:
                    self._metrics[name] = {
                        "count": 0,
                        "total_time": 0.0,
                        "min_time": float("inf"),
                        "max_time": 0.0,
                    }
                self._metrics[name]["count"] += 1
                self._metrics[name]["total_time"] += elapsed
                self._metrics[name]["min_time"] = min(
                    self._metrics[name]["min_time"], elapsed
                )
                self._metrics[name]["max_time"] = max(
                    self._metrics[name]["max_time"], elapsed
                )

    def record_cache_hit(self, cache_name: str):
        """Record a cache hit."""
        if not self._enabled:
            return
        with self._lock:
            if cache_name not in self._metrics:
                self._metrics[cache_name] = {"hits": 0, "misses": 0}
            self._metrics[cache_name]["hits"] += 1

    def record_cache_miss(self, cache_name: str):
        """Record a cache miss."""
        if not self._enabled:
            return
        with self._lock:
            if cache_name not in self._metrics:
                self._metrics[cache_name] = {"hits": 0, "misses": 0}
            self._metrics[cache_name]["misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        with self._lock:
            metrics = {}
            for name, data in self._metrics.items():
                metrics[name] = dict(data)
                if "hits" in data and "misses" in data:
                    total = data["hits"] + data["misses"]
                    metrics[name]["hit_rate"] = (
                        data["hits"] / total if total > 0 else 0.0
                    )
                if "count" in data and data["count"] > 0:
                    metrics[name]["avg_time"] = data["total_time"] / data["count"]
            return metrics

    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._metrics = {}

    def set_enabled(self, enabled: bool):
        """Enable or disable profiling."""
        self._enabled = enabled


def get_performance_metrics(profiler: ROSAProfiler) -> Dict[str, Any]:
    """Get formatted performance metrics for tool output."""
    metrics = profiler.get_metrics()
    return {
        "performance_metrics": metrics,
        "profiling_enabled": profiler._enabled,
    }
