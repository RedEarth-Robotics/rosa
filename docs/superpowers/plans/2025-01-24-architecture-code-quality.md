# Architecture & Code Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor oversized ros1.py/ros2.py into focused modules, extract shared utilities, improve type safety and error handling — all with zero breaking changes.

**Architecture:** Split monolithic tool files into packages by domain (topics, nodes/services, graph/params, packages, bag/actions, logs). Extract shared helpers into `utils.py`. Replace scattered module globals with `_ToolContext`. Keep original files as thin re-export shims.

**Tech Stack:** Python 3.9+, dataclasses, typing, langchain

---

## File Structure

### New Files
| File | Responsibility |
|------|---------------|
| `src/rosa/tools/utils.py` | Shared helpers: safe_tool_execute, filter_by_pattern, format_tool_response |
| `src/rosa/tools/ros1/__init__.py` | Package init, re-exports, _ToolContext |
| `src/rosa/tools/ros1/topics.py` | rostopic_list, rostopic_info, rostopic_echo |
| `src/rosa/tools/ros1/nodes_services.py` | rosnode_list, rosnode_info, rosservice_list/info/call |
| `src/rosa/tools/ros1/graph_params.py` | rosgraph_get, rosparam_list/get/set |
| `src/rosa/tools/ros1/packages.py` | rospkg_list, rosmsg_info, rossrv_info |
| `src/rosa/tools/ros1/bag_actions.py` | rosbag_record/info/play, actionclient_list, roslaunch_find |
| `src/rosa/tools/ros1/utils.py` | ROS1-specific helpers (get_entities) |
| `src/rosa/tools/ros2/__init__.py` | Package init, re-exports, _ToolContext |
| `src/rosa/tools/ros2/topics.py` | ros2_topic_list, ros2_topic_echo, ros2_topic_info |
| `src/rosa/tools/ros2/nodes_services.py` | ros2_node_list/info, ros2_service_list/info/call |
| `src/rosa/tools/ros2/params.py` | ros2_param_list/get/set |
| `src/rosa/tools/ros2/bag_actions.py` | ros2_bag_record/info/play, ros2_launch_list, ros2_action_list |
| `src/rosa/tools/ros2/logs.py` | roslog_list |
| `src/rosa/tools/ros2/utils.py` | ROS2-specific helpers (execute_ros_command, get_entities) |

### Modified Files
| File | Changes |
|------|---------|
| `src/rosa/tools/ros1.py` | Convert to re-export shim |
| `src/rosa/tools/ros2.py` | Convert to re-export shim |
| `src/rosa/tools/__init__.py` | Update to import from new packages |

---

## Phase 1: Shared Utilities

### Task 1: Create `src/rosa/tools/utils.py`

**Files:**
- Create: `src/rosa/tools/utils.py`

- [ ] **Step 1: Create the shared utilities module**

Create `src/rosa/tools/utils.py`:
```python
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

import regex
from typing import Any, Callable, Dict, List, Optional


def filter_by_pattern(
    items: List[str],
    pattern: Optional[str] = None,
    blacklist: Optional[List[str]] = None,
) -> List[str]:
    """Filter a list of items by pattern and blacklist."""
    result = items
    if blacklist:
        result = list(
            filter(
                lambda x: not any(regex.match(f".*{bl}.*", x) for bl in blacklist),
                result,
            )
        )
    if pattern:
        result = list(filter(lambda x: regex.match(f".*{pattern}.*", x), result))
    return result


def format_tool_response(
    data: Any = None,
    error: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> Dict[str, Any]:
    """Format a consistent response dictionary for tool functions."""
    response: Dict[str, Any] = {}
    if data is not None:
        response["data"] = data
    if error:
        response["error"] = error
    if suggestion:
        response["suggestion"] = suggestion
    return response


def safe_tool_execute(
    operation_name: str,
    func: Callable,
    *args,
    **kwargs,
) -> Dict[str, Any]:
    """Execute a tool function with standardized error handling."""
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        return format_tool_response(
            error=f"Failed to {operation_name}: {e}",
            suggestion="Check that the ROS system is running and the target exists.",
        )
```

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/utils.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/utils.py
git commit -m "refactor(tools): add shared utilities module

- filter_by_pattern: regex filtering with blacklist
- format_tool_response: consistent dict response structure
- safe_tool_execute: standardized try/except wrapper"
```

---

## Phase 2: ROS1 Package

### Task 2: Create `src/rosa/tools/ros1/utils.py`

**Files:**
- Create: `src/rosa/tools/ros1/utils.py`

- [ ] **Step 1: Create ROS1-specific utilities**

Create `src/rosa/tools/ros1/utils.py`:
```python
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

from typing import List, Optional

import regex
import rosnode
import rostopic


def get_entities(
    type: str,
    pattern: Optional[str],
    namespace: Optional[str],
    blacklist: List[str] = None,
):
    """Convenience function because topic and node retrieval basically do the same thing."""
    entities = []

    if type == "topic":
        pub, sub = rostopic.get_topic_list()
        pub = list(map(lambda x: x[0], pub))
        sub = list(map(lambda x: x[0], sub))
        entities = sorted(list(set(pub + sub)))
    elif type == "node":
        entities = rosnode.get_node_names()
    total = len(entities)

    if namespace:
        if namespace == "/":
            pass
        else:
            entities = list(filter(lambda x: x.startswith(namespace + "/"), entities))
    in_namespace = len(entities)

    if pattern:
        entities = list(filter(lambda x: regex.match(f".*{pattern}.*", x), entities))
    match_pattern = len(entities)

    if blacklist:
        entities = list(
            filter(
                lambda x: not any(regex.match(f".*{bl}.*", x) for bl in blacklist),
                entities,
            )
        )

    if total == 0:
        entities = [f"There are currently no {type}s available in the system."]
    elif in_namespace == 0:
        entities = [
            f"There are currently no {type}s available using the '{namespace}' namespace."
        ]
    elif match_pattern == 0:
        entities = [
            f"There are currently no {type}s available matching the specified pattern."
        ]

    return total, in_namespace, match_pattern, sorted(entities)
```

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/utils.py`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/utils.py
git commit -m "refactor(ros1): add ros1-specific utilities module

- Extract get_entities helper from monolithic ros1.py"
```

---

### Task 3: Create `src/rosa/tools/ros1/topics.py`

**Files:**
- Create: `src/rosa/tools/ros1/topics.py`

- [ ] **Step 1: Move topic-related tools from ros1.py**

Read the current `src/rosa/tools/ros1.py` to extract `rostopic_list`, `rostopic_info`, and `rostopic_echo`.

Create `src/rosa/tools/ros1/topics.py` with these three functions, preserving their exact signatures and docstrings. Import needed modules (`rostopic`, `rospy`, `time`, `typing`) and `from .utils import get_entities`.

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/topics.py`

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/topics.py
git commit -m "refactor(ros1): extract topic tools to topics.py

- rostopic_list, rostopic_info, rostopic_echo"
```

---

### Task 4: Create `src/rosa/tools/ros1/nodes_services.py`

**Files:**
- Create: `src/rosa/tools/ros1/nodes_services.py`

- [ ] **Step 1: Move node and service tools**

Read current `src/rosa/tools/ros1.py`.

Create `src/rosa/tools/ros1/nodes_services.py` with: `rosnode_list`, `rosnode_info`, `rosservice_list`, `rosservice_info`, `rosservice_call`.

Import needed modules (`rosnode`, `rosservice`, `regex`, `typing`) and `from .utils import get_entities`.

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/nodes_services.py`

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/nodes_services.py
git commit -m "refactor(ros1): extract node and service tools

- rosnode_list, rosnode_info, rosservice_list, rosservice_info, rosservice_call"
```

---

### Task 5: Create `src/rosa/tools/ros1/graph_params.py`

**Files:**
- Create: `src/rosa/tools/ros1/graph_params.py`

- [ ] **Step 1: Move graph and param tools**

Read current `src/rosa/tools/ros1.py`.

Create `src/rosa/tools/ros1/graph_params.py` with: `rosgraph_get`, `rosparam_list`, `rosparam_get`, `rosparam_set`.

Import needed modules (`rosgraph`, `rosparam`, `regex`, `typing`).

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/graph_params.py`

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/graph_params.py
git commit -m "refactor(ros1): extract graph and param tools

- rosgraph_get, rosparam_list, rosparam_get, rosparam_set"
```

---

### Task 6: Create `src/rosa/tools/ros1/packages.py`

**Files:**
- Create: `src/rosa/tools/ros1/packages.py`

- [ ] **Step 1: Move package and message tools**

Read current `src/rosa/tools/ros1.py`.

Create `src/rosa/tools/ros1/packages.py` with: `rospkg_list`, `rosmsg_info`, `rossrv_info`.

Import needed modules (`rospkg`, `rosmsg`, `typing`).

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/packages.py`

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/packages.py
git commit -m "refactor(ros1): extract package and message tools

- rospkg_list, rosmsg_info, rossrv_info"
```

---

### Task 7: Create `src/rosa/tools/ros1/bag_actions.py`

**Files:**
- Create: `src/rosa/tools/ros1/bag_actions.py`

- [ ] **Step 1: Move bag and action tools**

Read current `src/rosa/tools/ros1.py`.

Create `src/rosa/tools/ros1/bag_actions.py` with: `rosbag_record`, `rosbag_info`, `rosbag_play`, `actionclient_list`, `roslaunch_find`.

Import needed modules (`os`, `time`, `subprocess`, `datetime`, `typing`, `rospkg`).

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/bag_actions.py`

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/bag_actions.py
git commit -m "refactor(ros1): extract bag and action tools

- rosbag_record, rosbag_info, rosbag_play, actionclient_list, roslaunch_find"
```

---

### Task 8: Create `src/rosa/tools/ros1/__init__.py` and convert `ros1.py` to shim

**Files:**
- Create: `src/rosa/tools/ros1/__init__.py`
- Modify: `src/rosa/tools/ros1.py`

- [ ] **Step 1: Create package init with re-exports**

Create `src/rosa/tools/ros1/__init__.py`:
```python
#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

from .topics import rostopic_list, rostopic_info, rostopic_echo
from .nodes_services import rosnode_list, rosnode_info, rosservice_list, rosservice_info, rosservice_call
from .graph_params import rosgraph_get, rosparam_list, rosparam_get, rosparam_set
from .packages import rospkg_list, rosmsg_info, rossrv_info
from .bag_actions import rosbag_record, rosbag_info, rosbag_play, actionclient_list, roslaunch_find
```

- [ ] **Step 2: Convert ros1.py to re-export shim**

Replace the contents of `src/rosa/tools/ros1.py` with:
```python
#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.

# This module is a backward-compatible shim.
# All tools have been moved to the src/rosa/tools/ros1/ package.
# Import from there for new code.

from .ros1 import (
    rostopic_list,
    rostopic_info,
    rostopic_echo,
    rosnode_list,
    rosnode_info,
    rosservice_list,
    rosservice_info,
    rosservice_call,
    rosgraph_get,
    rosparam_list,
    rosparam_get,
    rosparam_set,
    rospkg_list,
    rosmsg_info,
    rossrv_info,
    rosbag_record,
    rosbag_info,
    rosbag_play,
    actionclient_list,
    roslaunch_find,
)

# Keep the cache setter for backward compatibility
from .ros1.topics import _ros_state_cache, set_ros_state_cache
```

- [ ] **Step 3: Verify imports work**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python -c "from src.rosa.tools import ros1; print('OK')"`

- [ ] **Step 4: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/ src/rosa/tools/ros1.py
git commit -m "refactor(ros1): convert ros1.py to package with re-export shim

- Split into topics, nodes_services, graph_params, packages, bag_actions
- Original ros1.py now re-exports from new package
- Zero breaking changes: all imports work as before"
```

---

## Phase 3: ROS2 Package (mirrors ROS1 pattern)

### Task 9: Create `src/rosa/tools/ros2/utils.py`

**Files:**
- Create: `src/rosa/tools/ros2/utils.py`

- [ ] **Step 1: Create ROS2-specific utilities**

Read current `src/rosa/tools/ros2.py`.

Create `src/rosa/tools/ros2/utils.py` with `execute_ros_command()` and `get_entities()` functions, preserving exact behavior.

- [ ] **Step 2: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros2/utils.py`

- [ ] **Step 3: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros2/utils.py
git commit -m "refactor(ros2): add ros2-specific utilities module

- Extract execute_ros_command and get_entities helpers"
```

---

### Task 10: Create `src/rosa/tools/ros2/topics.py`

**Files:**
- Create: `src/rosa/tools/ros2/topics.py`

- [ ] **Step 1: Move topic tools**

Read current `src/rosa/tools/ros2.py`.

Create `src/rosa/tools/ros2/topics.py` with: `ros2_topic_list`, `ros2_topic_echo`, `ros2_topic_info`.

Import `from .utils import execute_ros_command, get_entities`.

- [ ] **Step 2: Verify syntax and commit**

Run py_compile, then commit.

---

### Task 11: Create `src/rosa/tools/ros2/nodes_services.py`

**Files:**
- Create: `src/rosa/tools/ros2/nodes_services.py`

- [ ] **Step 1: Move node and service tools**

Read current `src/rosa/tools/ros2.py`.

Create `src/rosa/tools/ros2/nodes_services.py` with: `ros2_node_list`, `ros2_node_info`, `ros2_service_list`, `ros2_service_info`, `ros2_service_call`.

- [ ] **Step 2: Verify syntax and commit**

---

### Task 12: Create `src/rosa/tools/ros2/params.py`

**Files:**
- Create: `src/rosa/tools/ros2/params.py`

- [ ] **Step 1: Move param tools**

Read current `src/rosa/tools/ros2.py`.

Create `src/rosa/tools/ros2/params.py` with: `ros2_param_list`, `ros2_param_get`, `ros2_param_set`.

- [ ] **Step 2: Verify syntax and commit**

---

### Task 13: Create `src/rosa/tools/ros2/bag_actions.py`

**Files:**
- Create: `src/rosa/tools/ros2/bag_actions.py`

- [ ] **Step 1: Move bag and action tools**

Read current `src/rosa/tools/ros2.py`.

Create `src/rosa/tools/ros2/bag_actions.py` with: `ros2_bag_record`, `ros2_bag_info`, `ros2_bag_play`, `ros2_launch_list`, `ros2_action_list`.

- [ ] **Step 2: Verify syntax and commit**

---

### Task 14: Create `src/rosa/tools/ros2/logs.py`

**Files:**
- Create: `src/rosa/tools/ros2/logs.py`

- [ ] **Step 1: Move log tools**

Read current `src/rosa/tools/ros2.py`.

Create `src/rosa/tools/ros2/logs.py` with: `ros2_log_directories` (helper), `roslog_list`.

- [ ] **Step 2: Verify syntax and commit**

---

### Task 15: Create `src/rosa/tools/ros2/__init__.py` and convert `ros2.py` to shim

**Files:**
- Create: `src/rosa/tools/ros2/__init__.py`
- Modify: `src/rosa/tools/ros2.py`

- [ ] **Step 1: Create package init with re-exports**

Create `src/rosa/tools/ros2/__init__.py`:
```python
from .topics import ros2_topic_list, ros2_topic_echo, ros2_topic_info
from .nodes_services import ros2_node_list, ros2_node_info, ros2_service_list, ros2_service_info, ros2_service_call
from .params import ros2_param_list, ros2_param_get, ros2_param_set
from .bag_actions import ros2_bag_record, ros2_bag_info, ros2_bag_play, ros2_launch_list, ros2_action_list
from .logs import roslog_list
```

- [ ] **Step 2: Convert ros2.py to re-export shim**

Replace contents of `src/rosa/tools/ros2.py`:
```python
# Backward-compatible shim.
# All tools moved to src/rosa/tools/ros2/ package.

from .ros2 import (
    ros2_topic_list, ros2_topic_echo, ros2_topic_info,
    ros2_node_list, ros2_node_info,
    ros2_service_list, ros2_service_info, ros2_service_call,
    ros2_param_list, ros2_param_get, ros2_param_set,
    ros2_bag_record, ros2_bag_info, ros2_bag_play,
    ros2_launch_list, ros2_action_list,
    roslog_list,
)

from .ros2.topics import _ros_state_cache, set_ros_state_cache
```

- [ ] **Step 3: Verify imports**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python -c "from src.rosa.tools import ros2; print('OK')"`

- [ ] **Step 4: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros2/ src/rosa/tools/ros2.py
git commit -m "refactor(ros2): convert ros2.py to package with re-export shim

- Split into topics, nodes_services, params, bag_actions, logs
- Original ros2.py now re-exports from new package
- Zero breaking changes: all imports work as before"
```

---

## Phase 4: Type Safety Improvements

### Task 16: Add type hints to all new ROS1 tool functions

**Files:**
- Modify: `src/rosa/tools/ros1/topics.py`
- Modify: `src/rosa/tools/ros1/nodes_services.py`
- Modify: `src/rosa/tools/ros1/graph_params.py`
- Modify: `src/rosa/tools/ros1/packages.py`
- Modify: `src/rosa/tools/ros1/bag_actions.py`

- [ ] **Step 1: Add return type annotations**

Add `-> dict` return type to all `@tool` decorated functions in each file.
Add proper `Optional[...]` types for optional parameters.

- [ ] **Step 2: Add imports**

Add `from typing import Optional, List, Dict, Any` where needed.

- [ ] **Step 3: Verify syntax**

Run: `cd /home/frederichtran199/Code/robotics/rosa && python3 -m py_compile src/rosa/tools/ros1/*.py`

- [ ] **Step 4: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add src/rosa/tools/ros1/
git commit -m "refactor(ros1): add type hints to all tool functions

- Consistent return type annotations
- Optional parameter typing"
```

---

### Task 17: Add type hints to all new ROS2 tool functions

**Files:**
- Modify: `src/rosa/tools/ros2/topics.py`
- Modify: `src/rosa/tools/ros2/nodes_services.py`
- Modify: `src/rosa/tools/ros2/params.py`
- Modify: `src/rosa/tools/ros2/bag_actions.py`
- Modify: `src/rosa/tools/ros2/logs.py`

Same steps as Task 16 but for ROS2 files.

---

## Phase 5: Error Handling Standardization

### Task 18: Standardize error handling in ROS1 tools

**Files:**
- Modify: `src/rosa/tools/ros1/topics.py`
- Modify: `src/rosa/tools/ros1/nodes_services.py`
- Modify: `src/rosa/tools/ros1/graph_params.py`
- Modify: `src/rosa/tools/ros1/packages.py`
- Modify: `src/rosa/tools/ros1/bag_actions.py`

- [ ] **Step 1: Apply consistent error pattern**

For each tool function, ensure errors follow:
```python
try:
    # existing logic
except Exception as e:
    return {"error": f"Failed to {operation}: {e}"}
```

This should already be the case since we're preserving existing behavior. Verify and fix any inconsistencies.

- [ ] **Step 2: Commit**

```bash
git add src/rosa/tools/ros1/
git commit -m "refactor(ros1): standardize error handling patterns

- Consistent error formatting across all tool functions"
```

---

### Task 19: Standardize error handling in ROS2 tools

Same as Task 18 but for ROS2 files.

---

## Phase 6: Update ROSATools Integration

### Task 20: Update `src/rosa/tools/__init__.py`

**Files:**
- Modify: `src/rosa/tools/__init__.py`

- [ ] **Step 1: Verify imports still work**

The `ros1.py` and `ros2.py` shims should make this transparent, but verify:

```bash
cd /home/frederichtran199/Code/robotics/rosa
python -c "from src.rosa.tools import ROSATools; print('OK')"
```

- [ ] **Step 2: No changes needed**

If imports work, `ROSATools.__init__` already imports `ros1`/`ros2` modules and `__iterative_add` finds tools via `dir()`. The shim re-exports everything.

- [ ] **Step 3: Verify existing tests still pass**

Run existing tests to confirm no regressions.

---

## Phase 7: Documentation Update

### Task 21: Update ROADMAP

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Mark Architecture & Code Quality complete**

Update Sub-Project 4 header and checklist.
Add deliverables list.

- [ ] **Step 2: Commit**

```bash
cd /home/frederichtran199/Code/robotics/rosa
git add ROADMAP.md
git commit -m "docs: mark Architecture & Code Quality complete

- File splitting for ros1.py and ros2.py
- Shared utilities extraction
- Type hints and error handling standardization"
```

---

## Self-Review Checklist

### Spec Coverage
- [x] Shared utilities (utils.py) → Task 1
- [x] ROS1 package splitting → Tasks 2-8
- [x] ROS2 package splitting → Tasks 9-15
- [x] Re-export shims → Tasks 8, 15
- [x] Type hints → Tasks 16-17
- [x] Error handling → Tasks 18-19
- [x] Integration verification → Task 20
- [x] Documentation → Task 21

### Placeholder Scan
- [x] No TBD/TODO/implement later
- [x] Complete code where needed
- [x] Exact file paths

---

*Plan complete and ready for execution.*
