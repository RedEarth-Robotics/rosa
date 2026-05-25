# Architecture & Code Quality Design

**Date**: 2025-01-24
**Status**: Approved for Implementation
**Constraint**: Zero breaking changes — all existing APIs preserved

---

## 1. Goals

- **Reduce file sizes**: No implementation file >500 lines
- **Eliminate duplication**: Shared utilities for common patterns
- **Improve maintainability**: Clear file responsibilities, consistent patterns
- **Add type safety**: Consistent type hints across all tools
- **Zero breaking changes**: All existing APIs preserved exactly

---

## 2. Hybrid File Splitting

### ROS1 Tools (currently 1,105 lines)
New package: `src/rosa/tools/ros1/`

| Module | Contents | Est. Lines |
|--------|----------|------------|
| `__init__.py` | Re-exports all tools, `_ToolContext` | 60 |
| `topics.py` | rostopic_list, rostopic_info, rostopic_echo | 180 |
| `nodes_services.py` | rosnode_list, rosnode_info, rosservice_list/info/call | 180 |
| `graph_params.py` | rosgraph_get, rosparam_list/get/set | 150 |
| `packages.py` | rospkg_list, rosmsg_info, rossrv_info | 130 |
| `bag_actions.py` | rosbag_record/info/play, actionclient_list, roslaunch_find | 120 |
| `utils.py` | Shared helpers (get_entities, filter logic) | 80 |

Original `src/rosa/tools/ros1.py` becomes a thin re-export shim.

### ROS2 Tools (currently 802 lines)
New package: `src/rosa/tools/ros2/`

| Module | Contents | Est. Lines |
|--------|----------|------------|
| `__init__.py` | Re-exports all tools, `_ToolContext` | 60 |
| `topics.py` | ros2_topic_list, ros2_topic_echo, ros2_topic_info | 120 |
| `nodes_services.py` | ros2_node_list/info, ros2_service_list/info/call | 150 |
| `params.py` | ros2_param_list/get/set | 100 |
| `bag_actions.py` | ros2_bag_record/info/play, ros2_launch_list, ros2_action_list | 130 |
| `logs.py` | roslog_list | 60 |
| `utils.py` | Shared helpers (execute_ros_command, get_entities) | 60 |

Original `src/rosa/tools/ros2.py` becomes a thin re-export shim.

---

## 3. Shared Utilities (`src/rosa/tools/utils.py`)

New shared module for cross-cutting concerns:

```python
def safe_tool_execute(operation_name: str, func: Callable, *args, **kwargs) -> dict:
    """Standardized try/except wrapper with consistent error formatting."""

def filter_by_pattern(items: List[str], pattern: Optional[str], blacklist: Optional[List[str]]) -> List[str]:
    """Regex filtering with blacklist support."""

def format_tool_response(data: Any = None, error: str = None, suggestion: str = None) -> dict:
    """Consistent dict response structure for all tools."""
```

---

## 4. Interface Improvement

Replace scattered module-level globals with organized context:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class _ToolContext:
    ros_state_cache: Optional[ROSStateCache] = None
    profiler: Optional[ROSAProfiler] = None

_context = _ToolContext()

def set_tool_context(ctx: _ToolContext):
    global _context
    _context = ctx
```

Tools access cache via `_context.ros_state_cache` instead of direct module globals.

---

## 5. Type Safety Improvements

- Add return type `-> dict` to all tool functions
- Use `Optional[List[str]]` instead of `List[str] = None`
- Standardize on `Dict[str, Any]` for tool returns
- Add consistent param types in docstrings

---

## 6. Error Handling Standardization

All tools follow this pattern:

```python
try:
    result = do_work()
    return format_tool_response(data=result)
except SpecificError as e:
    return format_tool_response(error=str(e), suggestion="...")
except Exception as e:
    return format_tool_response(error=f"Unexpected error: {e}")
```

---

## 7. Backward Compatibility Strategy

| File | Action | Compatibility |
|------|--------|--------------|
| `src/rosa/tools/ros1.py` | Keep as re-export shim | All imports work |
| `src/rosa/tools/ros2.py` | Keep as re-export shim | All imports work |
| `ROSA.__init__` | No changes | Same constructor |
| Tool signatures | Unchanged | Same params/defaults |
| `ROSATools` | No changes | Same class API |

---

## 8. Implementation Order

1. **Phase 1**: Create `src/rosa/tools/utils.py` with shared helpers
2. **Phase 2**: Create `src/rosa/tools/ros1/` package, split ros1.py
3. **Phase 3**: Create `src/rosa/tools/ros2/` package, split ros2.py
4. **Phase 4**: Convert ros1.py/ros2.py to re-export shims
5. **Phase 5**: Add type hints to all tool functions
6. **Phase 6**: Standardize error handling patterns
7. **Phase 7**: Update docs and ROADMAP

---

*Design approved. Proceed to writing-plans skill for task breakdown.*
