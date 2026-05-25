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
import pytest
from src.rosa.performance.profiler import ROSAProfiler


def test_profiler_context_manager_timing():
    profiler = ROSAProfiler()
    with profiler.time_operation("test_op"):
        time.sleep(0.01)
    metrics = profiler.get_metrics()
    assert "test_op" in metrics
    assert metrics["test_op"]["count"] == 1
    assert metrics["test_op"]["total_time"] >= 0.01


def test_profiler_multiple_calls():
    profiler = ROSAProfiler()
    for _ in range(3):
        with profiler.time_operation("multi_op"):
            pass
    metrics = profiler.get_metrics()
    assert metrics["multi_op"]["count"] == 3


def test_profiler_cache_metrics():
    profiler = ROSAProfiler()
    profiler.record_cache_hit("tool_cache")
    profiler.record_cache_miss("tool_cache")
    profiler.record_cache_hit("tool_cache")
    metrics = profiler.get_metrics()
    assert metrics["tool_cache"]["hits"] == 2
    assert metrics["tool_cache"]["misses"] == 1
    assert metrics["tool_cache"]["hit_rate"] == 2 / 3


def test_profiler_reset():
    profiler = ROSAProfiler()
    with profiler.time_operation("op"):
        pass
    profiler.reset()
    assert profiler.get_metrics() == {}
