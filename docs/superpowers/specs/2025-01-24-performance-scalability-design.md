# Performance & Scalability Design: Comprehensive Multi-Layer Optimization

**Date**: 2025-01-24
**Status**: Approved for Implementation
**Approach**: Comprehensive Multi-Layer Optimization (Approach A)

---

## 1. Goals & Success Criteria

### Primary Goals
1. **Reduce redundant ROS system queries** by 80% through intelligent caching
2. **Achieve <100ms response time** for cached tool operations
3. **Cap memory overhead** at configurable limit (default: 256MB for chat history + caches)
4. **Ensure linear scaling** with ROS system size (nodes/topics)
5. **Maintain compatibility** with all existing ROSA APIs and tool signatures

### Target Environments
- Local development (laptops/desktops)
- On-board robot computers (resource-constrained embedded systems)
- Mixed deployments across small (1-10 nodes) to very large (200+ nodes) systems

---

## 2. Architecture Overview

### Three-Layer Optimization Stack

```
┌─────────────────────────────────────────┐
│  Layer 3: Agent Memory Management       │
│  - Chat history compaction              │
│  - Token budget enforcement             │
│  - Streaming optimization               │
├─────────────────────────────────────────┤
│  Layer 2: Tool Result Caching           │
│  - Tool output cache with TTL           │
│  - Query batching/coalescing            │
│  - Large dataset pagination             │
├─────────────────────────────────────────┤
│  Layer 1: ROS System State Cache        │
│  - Graph topology cache                 │
│  - Change detection & invalidation      │
│  - Memory-efficient data structures     │
└─────────────────────────────────────────┘
```

### Key Design Principles
- **Backward compatibility**: All existing tool signatures and ROSA class API remain unchanged
- **Opt-in configurability**: Performance features enabled by default but configurable/disablable
- **Graceful degradation**: Cache misses fall back to current behavior without errors
- **Resource awareness**: Self-monitoring memory usage with automatic cleanup triggers

---

## 3. Layer 1: ROS System State Cache

### 3.1 ROSStateCache Class

**Location**: `src/rosa/cache/ros_state_cache.py`

**Responsibility**: Cache ROS graph topology and provide change detection for cache invalidation.

**Cache Entries**:
| Key | Data | TTL | Invalidation Trigger |
|-----|------|-----|----------------------|
| `topics` | List of topic names | 2s | ROS master system state change (ROS1), checksum diff (ROS2) |
| `nodes` | List of node names | 2s | Same as above |
| `services` | List of service names | 5s | Same as above |
| `params` | Parameter list by namespace | 5s | Same as above |
| `topic_info:{name}` | Topic type, pubs, subs | 3s | Topic not in cached topic list |
| `node_info:{name}` | Node info text | 5s | Node not in cached node list |

**Change Detection (ROS1)**:
- Use `rosgraph.masterapi.Master('/rosout').getSystemState()` to get a hash of the system state
- Compare hash with cached hash; if different, invalidate all topology caches
- Hash computed from sorted tuples of (topic, publisher_set, subscriber_set)

**Change Detection (ROS2)**:
- Compute checksum of `ros2 topic list` + `ros2 node list` + `ros2 service list` outputs
- Compare with cached checksum; if different, invalidate all topology caches
- Poll interval: 1s (configurable)

**Thread Safety**:
- All cache operations protected by `threading.RLock`
- Background change detection runs in daemon thread

### 3.2 Integration Points

**ros1.py modifications**:
- `get_entities()` checks ROSStateCache first for topic/node lists
- `rostopic_info()` checks cache for individual topic info
- `rosnode_info()` checks cache for individual node info
- `rosgraph_get()` uses cached topology + rebuilds graph from cache when possible

**ros2.py modifications**:
- `get_entities()` checks ROSStateCache first
- `ros2_topic_info()` checks cache
- `ros2_node_info()` checks cache
- All `execute_ros_command()` calls for list operations check cache first

### 3.3 Memory-Efficient Data Structures

**Problem**: `rosgraph_get` builds full connection graph as list of tuples; for 200 nodes / 1000 topics this is huge.

**Solution**:
- Store graph as adjacency lists (dictionary: topic -> {pubs: set, subs: set})
- Only materialize full tuple list on cache miss or when specifically requested
- Add `max_connections` parameter to `rosgraph_get` with early termination

---

## 4. Layer 2: Tool Result Caching & Batching

### 4.1 ToolResultCache Class

**Location**: `src/rosa/cache/tool_cache.py`

**Responsibility**: Cache expensive tool outputs with parameter-based cache keys.

**Cache Key Format**: `{tool_name}:{sorted_param_hash}`

**TTL by Tool Category**:
| Category | Tools | TTL |
|----------|-------|-----|
| Static info | rospkg_list, rosmsg_info, rossrv_info | 60s |
| Semi-static | rosparam_list, rosnode_list, rostopic_list | 3s |
| Dynamic | rostopic_echo, rosservice_call | 1s |
| System | get_system_health, check_disk_space | 10s |

**Cache Size Limits**:
- Max entries: 500 (configurable)
- Max entry size: 1MB
- LRU eviction when limits exceeded

### 4.2 Query Batching / Coalescing

**Problem**: Multiple rapid `rostopic_list` or `rosnode_list` calls from agent reasoning.

**Solution**:
- In-flight request coalescing: if identical request is in progress, wait for result instead of issuing duplicate
- Batch window: 50ms (configurable) to coalesce near-simultaneous identical requests

### 4.3 Large Dataset Pagination

**Problem**: `rosgraph_get` on large systems returns thousands of connections; LLM context window gets overwhelmed.

**Solution**:
- Add `max_results` parameter to all list/info tools (default: 100)
- Return paginated results with `page`, `total_pages`, `has_more` fields
- `rosgraph_get` already has `max_render_size=50`; expand this pattern consistently

---

## 5. Layer 3: Agent Memory Management

### 5.1 Chat History Strategies

**Location**: `src/rosa/memory/chat_history.py`

**Current Behavior**: All messages appended indefinitely to `__chat_history`.

**New Strategies** (configurable via `history_strategy` parameter):

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `accumulate` (default) | Current behavior - keep all messages | Short conversations |
| `window` | Keep last N message pairs (default: 20) | Medium conversations |
| `token_budget` | Keep messages within token budget (default: 8000) | Long conversations |
| `summarize` | Summarize older messages, keep recent N raw | Very long conversations |

**Implementation**:
- `ChatHistoryManager` class with pluggable strategies
- Strategy selected at ROSA initialization via `history_strategy` parameter
- Token counting uses tiktoken (if available) or rough character-based estimate

### 5.2 Token Budget Enforcement

**Problem**: Long chat history causes excessive token usage and LLM costs.

**Solution**:
- Track cumulative token usage (prompt + completion) per conversation
- When token budget exceeded, trigger history compaction based on strategy
- Provide warning to user when compaction occurs

### 5.3 Streaming Optimization

**Current**: `astream()` processes all event types; no prioritization.

**Optimization**:
- Add event buffering for high-frequency tool events
- Prioritize token events over tool events for responsiveness
- Add `stream_buffer_ms` parameter (default: 10ms)

---

## 6. Performance Monitoring & Profiling

### 6.1 Built-in Profiling

**Location**: `src/rosa/performance/profiler.py`

**Components**:
- `ROSAProfiler`: Context manager for timing tool executions
- Cache hit/miss metrics tracking
- Memory usage reporting
- Optional export to Prometheus-compatible metrics

### 6.2 New Tools for Self-Monitoring

| Tool | Purpose |
|------|---------|
| `get_performance_metrics()` | Returns cache hit rates, avg tool execution times, memory usage |
| `clear_caches()` | Manually invalidate all caches |
| `set_cache_ttl(tool_category, ttl_seconds)` | Dynamically adjust cache TTLs |

---

## 7. Configuration API

### 7.1 ROSA Class Extension

New parameters added to `ROSA.__init__` (all optional, backward compatible):

```python
ROSA(
    ros_version=1,
    llm=llm,
    # ... existing params ...
    # New performance params:
    enable_caching: bool = True,           # Master switch for all caching
    cache_ttl_override: Optional[dict] = None,  # Per-tool TTL overrides
    history_strategy: str = "accumulate",   # Chat history management strategy
    history_window_size: int = 20,         # For "window" strategy
    token_budget: int = 8000,              # For "token_budget" strategy
    max_cache_entries: int = 500,          # Tool cache size limit
    enable_profiling: bool = False,         # Performance profiling
)
```

### 7.2 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROSA_ENABLE_CACHING` | Enable/disable caching | `true` |
| `ROSA_CACHE_TTL_TOPICS` | Topic list cache TTL | `2` |
| `ROSA_CACHE_TTL_NODES` | Node list cache TTL | `2` |
| `ROSA_CACHE_TTL_SERVICES` | Service list cache TTL | `5` |
| `ROSA_HISTORY_STRATEGY` | Chat history strategy | `accumulate` |
| `ROSA_TOKEN_BUDGET` | Token budget for history | `8000` |
| `ROSA_MAX_CACHE_ENTRIES` | Max cache entries | `500` |

---

## 8. File Structure

```
src/rosa/
├── __init__.py
├── rosa.py                          # Extended with performance params
├── prompts.py
├── cache/
│   ├── __init__.py
│   ├── ros_state_cache.py           # Layer 1: ROS graph caching
│   ├── tool_cache.py                # Layer 2: Tool result caching
│   └── in_flight_requests.py        # Request coalescing
├── memory/
│   ├── __init__.py
│   └── chat_history.py              # Layer 3: History management
├── performance/
│   ├── __init__.py
│   └── profiler.py                  # Profiling & metrics
└── tools/
    ├── __init__.py                  # Updated to wire in caching
    ├── ros1.py                      # Use ROSStateCache
    ├── ros2.py                      # Use ROSStateCache
    ├── system.py                    # Add performance tools
    ├── calculation.py
    └── log.py
```

---

## 9. Implementation Order

1. **Phase 1: Foundation** (independent)
   - `ROSAProfiler` class
   - `ToolResultCache` class
   - Unit tests for cache components

2. **Phase 2: ROS State Cache** (depends on Phase 1)
   - `ROSStateCache` class (ROS1 + ROS2 change detection)
   - Integrate into `ros1.py` list/info tools
   - Integrate into `ros2.py` list/info tools

3. **Phase 3: Memory Management** (independent)
   - `ChatHistoryManager` with all strategies
   - Token budget enforcement
   - Integrate into `rosa.py`

4. **Phase 4: Polish** (depends on Phases 2-3)
   - Query coalescing
   - Large dataset pagination
   - Performance monitoring tools
   - Configuration via env vars
   - Documentation updates

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Cache hit/miss behavior
- TTL expiration
- LRU eviction
- Thread safety (concurrent access)
- Change detection accuracy

### 10.2 Integration Tests
- End-to-end with mock ROS system
- Memory usage benchmarks
- Response time benchmarks
- Large system simulation (1000+ topics)

### 10.3 Benchmarks
- Before/after comparison for:
  - `rostopic_list` repeated calls
  - `rosgraph_get` on large systems
  - Long conversation memory usage

---

## 11. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cache stale data | Short TTLs + change detection; cache invalidation on ROS system changes |
| Memory leaks | LRU eviction + max entry size + periodic cleanup |
| Thread safety bugs | RLock on all cache ops + comprehensive concurrency tests |
| Backward compatibility | All new params optional with sensible defaults; existing behavior preserved |
| Complex configuration | Sensible defaults for all options; enable_caching single master switch |

---

## 12. Future Extensions (Out of Scope)

- Persistent cache across ROSA restarts (Redis/file-based)
- Distributed caching for multi-agent deployments
- Predictive pre-fetching based on agent reasoning patterns
- Adaptive TTL based on system volatility

---

*Design approved for implementation. Proceed to writing-plans skill for detailed task breakdown.*
