# Experienced ROS Developer Guide

This guide is for ROS developers who are familiar with ROS concepts and want to leverage ROSA to streamline their workflows.

## Learning Objectives

By the end of this guide, you will:
- Understand how ROSA maps to familiar ROS workflows
- Know how to integrate ROSA into existing projects
- Be able to create custom tools and agents
- Understand production deployment considerations

**Estimated Time**: 45 minutes  
**Prerequisites**: ROS experience, Python proficiency, ROSA installed

## ROSA for ROS Experts

### Mapping ROSA to ROS Workflows

If you're familiar with ROS command-line tools, here's how ROSA maps to them:

| ROS Command | ROSA Query | ROSA Tool |
|-------------|------------|-----------|
| `rostopic list` | "List all topics" | `rostopic_list` |
| `rosnode info /node` | "Tell me about /node" | `rosnode_info` |
| `rosservice call /srv` | "Call service /srv" | `rosservice_call` |
| `rosparam get /param` | "Get parameter /param" | `rosparam_get` |
| `rosmsg show Type` | "Show message Type" | `rosmsg_info` |

### Advantages Over Traditional ROS Workflows

1. **Compositional Queries**: Combine multiple ROS operations in one query
   ```python
   rosa.invoke("List all topics without subscribers and show their types")
   # Equivalent to multiple commands + filtering
   ```

2. **Intelligent Filtering**: Use natural language conditions
   ```python
   rosa.invoke("Show me nodes that publish to navigation topics")
   ```

3. **Reasoning**: ROSA can reason about system state
   ```python
   rosa.invoke("Why might the robot not be moving? Check nodes, topics, and services")
   ```

## Advanced Configuration

### Custom LLM Setup

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

# Optimized for production
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,  # Deterministic
    max_tokens=2000,
    timeout=30,
    max_retries=3,
)

rosa = ROSA(
    ros_version=1,
    llm=llm,
    streaming=False,  # Better for automation
    verbose=False,
    max_iterations=50,  # Prevent runaway
)
```

### Enterprise Deployment

```python
from rosa import ROSA
from rosa.prompts import RobotSystemPrompts

# Enterprise configuration
enterprise_prompts = RobotSystemPrompts(
    critical_instructions="Always log actions to /enterprise/log",
    constraints_and_guardrails="Require confirmation for destructive operations",
    about_your_operators="Factory floor operators with basic training"
)

rosa = ROSA(
    ros_version=1,
    llm=llm,
    prompts=enterprise_prompts,
    blacklist=["emergency_stop", "shutdown", "reboot"],
    accumulate_chat_history=False,  # Stateless for compliance
    show_token_usage=True  # Cost tracking
)
```

## Custom Tool Development

### Tool Design Patterns

#### Pattern 1: Direct ROS Wrapper

```python
from langchain.agents import tool
import rospy

@tool
def get_diagnostic_status(component: str) -> dict:
    """Get diagnostic status for a specific component.
    
    Args:
        component: Name of component (e.g., 'battery', 'motors', 'sensors')
    
    Returns:
        Diagnostic status dictionary
    """
    try:
        msg = rospy.wait_for_message(
            f"/diagnostics/{component}",
            DiagnosticArray,
            timeout=5.0
        )
        return {
            "component": component,
            "status": msg.status[0].level,
            "message": msg.status[0].message,
            "values": {kv.key: kv.value for kv in msg.status[0].values}
        }
    except Exception as e:
        return {"error": str(e), "component": component}
```

#### Pattern 2: Multi-Step Operation

```python
@tool
def execute_mission(waypoints: List[dict]) -> str:
    """Execute a navigation mission through waypoints.
    
    Args:
        waypoints: List of {x, y, z, yaw} waypoint dictionaries
    
    Returns:
        Mission execution summary
    """
    results = []
    for i, wp in enumerate(waypoints):
        try:
            # Send navigation goal
            result = send_nav_goal(wp)
            results.append(f"Waypoint {i}: Success")
        except Exception as e:
            results.append(f"Waypoint {i}: Failed - {e}")
            break
    
    return "\n".join(results)
```

#### Pattern 3: Safety Wrapper

```python
@tool
def emergency_stop_tool() -> str:
    """Trigger emergency stop (requires confirmation).
    
    This tool requires explicit confirmation and logs the action.
    """
    # Log the action
    rospy.logwarn("Emergency stop requested via ROSA")
    
    # Send emergency stop
    pub = rospy.Publisher("/emergency_stop", Empty, queue_size=1)
    pub.publish(Empty())
    
    return "Emergency stop triggered. All motors halted."
```

### Tool Testing

```python
import unittest
from rosa.tools import inject_blacklist

class TestCustomTools(unittest.TestCase):
    def test_diagnostic_tool(self):
        result = get_diagnostic_status("battery")
        self.assertIn("status", result)
        self.assertIn("message", result)
    
    def test_safety_injection(self):
        # Test blacklist injection
        tool_func = inject_blacklist(["dangerous"])(my_tool)
        # Verify blacklist is injected
        self.assertIn("blacklist", tool_func.__code__.co_varnames)
```

## Agent Customization

### Custom Agent Class

```python
from rosa import ROSA
from rosa.prompts import RobotSystemPrompts

class WarehouseRobotAgent(ROSA):
    """Specialized agent for warehouse robots."""
    
    def __init__(self, streaming: bool = False):
        prompts = RobotSystemPrompts(
            embodiment_and_persona="Warehouse AGV with lifting capability",
            about_your_capabilities="Navigate, lift pallets, avoid obstacles",
            constraints_and_guardrails="Max speed 1.5 m/s, 500kg payload limit",
            mission_and_objectives="Transport materials between warehouse zones"
        )
        
        super().__init__(
            ros_version=1,
            llm=get_llm(),
            prompts=prompts,
            blacklist=["emergency_stop", "motor_override"],
            streaming=streaming
        )
        
        # Add warehouse-specific tools
        self.add_warehouse_tools()
    
    def add_warehouse_tools(self):
        # Add pallet manipulation tools
        # Add zone navigation tools
        pass
    
    def get_system_status(self) -> dict:
        """Get comprehensive warehouse robot status."""
        return {
            "battery": self.get_battery_level(),
            "location": self.get_current_zone(),
            "payload": self.get_current_payload(),
            "errors": self.get_error_log()
        }
```

### Tool Selection Strategies

Control which tools are available based on context:

```python
class ContextAwareAgent(ROSA):
    def __init__(self):
        super().__init__(ros_version=1, llm=llm)
        self.operation_mode = "normal"
    
    def set_mode(self, mode: str):
        """Change operation mode and update available tools."""
        self.operation_mode = mode
        
        if mode == "maintenance":
            # Enable diagnostic tools, disable movement
            self.enable_tools(["diagnostics", "logs"])
            self.disable_tools(["movement", "manipulation"])
        elif mode == "emergency":
            # Only allow emergency tools
            self.enable_tools(["emergency"])
```

## Production Considerations

### Monitoring and Logging

```python
import logging

# Configure ROSA logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Custom logging for production
logger = logging.getLogger("rosa.production")

def log_query(query: str, response: str, tools_used: List[str]):
    logger.info(f"Query: {query}")
    logger.info(f"Tools used: {tools_used}")
    logger.info(f"Response length: {len(response)}")
```

### CI/CD Integration

```yaml
# .github/workflows/rosa-tests.yml
name: ROSA Integration Tests

on: [push, pull_request]

jobs:
  test-rosa-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup ROS
        uses: ros-tooling/setup-ros@v0.6
        with:
          required-ros-distributions: noetic
      
      - name: Install ROSA
        run: pip install -e .
      
      - name: Run integration tests
        run: |
          source /opt/ros/noetic/setup.bash
          python -m pytest tests/integration/ -v
```

### Security Best Practices

```python
# Implement strict safety controls
SAFE_ROSA = ROSA(
    ros_version=1,
    llm=llm,
    blacklist=[
        "emergency_stop",
        "motor_kill", 
        "override_safety",
        "delete_param",
        "shutdown"
    ],
    prompts=RobotSystemPrompts(
        critical_instructions="Never execute destructive operations without human confirmation"
    ),
    max_iterations=20  # Limit execution time
)
```

## Performance Optimization

### Token Usage Management

```python
# Track and optimize token usage
rosa = ROSA(
    ros_version=1,
    llm=llm,
    show_token_usage=True,
    streaming=False
)

response = rosa.invoke("List all topics")
# Output includes: Prompt Tokens, Completion Tokens, Total Cost
```

### Response Caching

```python
from functools import lru_cache

class CachedROSA(ROSA):
    @lru_cache(maxsize=100)
    def cached_invoke(self, query: str) -> str:
        return self.invoke(query)
```

### Parallel Tool Execution (When Safe)

```python
# For independent tool operations
import asyncio

async def parallel_tools(self, queries: List[str]):
    tasks = [self.astream(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

## Next Steps

- [Advanced Agent Customization Tutorial](../tutorials/advanced-agent-customization.md) - Build production agents
- [Researcher Guide](researcher.md) - Academic and research applications
- [Custom Tool Development Tutorial](../tutorials/custom-tool-development.md) - Deep dive into tool creation
