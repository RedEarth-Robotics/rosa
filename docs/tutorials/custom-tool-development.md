# Custom Tool Development Tutorial

Learn to create custom tools that extend ROSA's capabilities for your specific robot.

## Learning Objectives

- Understand the @tool decorator pattern
- Create simple and complex custom tools
- Integrate custom tools with ROSA
- Test and debug custom tools

**Time**: 60 minutes  
**Prerequisites**: Basic ROS Operations Tutorial, Python proficiency

## Part 1: Tool Basics (15 minutes)

### Understanding Tools

ROSA tools are Python functions that:
1. Perform a specific action
2. Accept typed parameters
3. Return structured results
4. Have clear documentation

### Exercise 1.1: Your First Tool

Create `my_first_tool.py`:

```python
from langchain.agents import tool

@tool
def greet(name: str) -> str:
    """Greet a person by name.
    
    Args:
        name: The person's name
    
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Welcome to ROSA tool development."
```

**Test it**:
```python
# test_tool.py
from my_first_tool import greet

result = greet("Researcher")
print(result)
# Output: Hello, Researcher! Welcome to ROSA tool development.
```

### Exercise 1.2: ROS-Integrated Tool

```python
from langchain.agents import tool
import rospy
from std_msgs.msg import String

@tool
def announce_status(message: str) -> str:
    """Publish a status announcement to the robot.
    
    Args:
        message: Status message to announce
    
    Returns:
        Confirmation of announcement
    """
    try:
        pub = rospy.Publisher('/status/announce', String, queue_size=10)
        rospy.sleep(0.1)  # Allow connection
        pub.publish(String(data=message))
        return f"Announced: {message}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Exercise 1.3: Parameter Validation

```python
from typing import Optional
from langchain.agents import tool

@tool
def move_distance(
    distance: float,
    speed: float = 1.0,
    direction: str = "forward"
) -> dict:
    """Move the robot a specific distance.
    
    Args:
        distance: Distance to move in meters (0.1 to 10.0)
        speed: Movement speed in m/s (0.1 to 2.0)
        direction: Movement direction ("forward", "backward")
    
    Returns:
        Movement result with status and final position
    """
    # Validate parameters
    if not (0.1 <= distance <= 10.0):
        return {"error": "Distance must be between 0.1 and 10.0 meters"}
    
    if not (0.1 <= speed <= 2.0):
        return {"error": "Speed must be between 0.1 and 2.0 m/s"}
    
    if direction not in ["forward", "backward"]:
        return {"error": "Direction must be 'forward' or 'backward'"}
    
    # Calculate duration
    duration = distance / speed
    
    return {
        "status": "success",
        "distance": distance,
        "speed": speed,
        "direction": direction,
        "duration": duration,
        "message": f"Moving {direction} {distance}m at {speed}m/s"
    }
```

## Part 2: Advanced Tool Patterns (20 minutes)

### Exercise 2.1: Multi-Step Tool

```python
from langchain.agents import tool
from typing import List, Dict
import time

@tool
def scan_environment(
    num_readings: int = 10,
    interval: float = 0.5
) -> List[Dict]:
    """Scan the environment by reading sensor data multiple times.
    
    Args:
        num_readings: Number of sensor readings to collect (1-50)
        interval: Time between readings in seconds
    
    Returns:
        List of sensor readings with timestamps
    """
    readings = []
    
    for i in range(num_readings):
        try:
            # Simulate sensor reading
            reading = {
                "timestamp": time.time(),
                "reading_number": i + 1,
                "value": read_sensor()  # Your sensor function
            }
            readings.append(reading)
            time.sleep(interval)
        except Exception as e:
            readings.append({
                "timestamp": time.time(),
                "reading_number": i + 1,
                "error": str(e)
            })
    
    return readings
```

### Exercise 2.2: Tool with Safety Checks

```python
from langchain.agents import tool
from typing import List

@tool
def emergency_stop(confirmation: str, reason: str) -> str:
    """Trigger emergency stop with confirmation.
    
    This tool requires explicit confirmation and logs the reason.
    
    Args:
        confirmation: Must be exactly "CONFIRM_EMERGENCY_STOP"
        reason: Reason for emergency stop
    
    Returns:
        Status of emergency stop
    """
    # Safety check
    if confirmation != "CONFIRM_EMERGENCY_STOP":
        return "Emergency stop NOT triggered. Confirmation phrase incorrect."
    
    if not reason or len(reason) < 10:
        return "Emergency stop NOT triggered. Reason must be at least 10 characters."
    
    # Log the emergency
    log_emergency(reason)
    
    # Trigger emergency stop
    try:
        trigger_estop()
        return f"EMERGENCY STOP TRIGGERED. Reason: {reason}"
    except Exception as e:
        return f"Emergency stop FAILED: {str(e)}"
```

### Exercise 2.3: Tool Composition

```python
from langchain.agents import tool
from typing import List, Tuple

@tool
def navigate_to_waypoints(waypoints: List[Tuple[float, float]]) -> str:
    """Navigate through a series of waypoints.
    
    Args:
        waypoints: List of (x, y) coordinate tuples
    
    Returns:
        Navigation summary
    """
    if not waypoints:
        return "Error: No waypoints provided"
    
    results = []
    for i, (x, y) in enumerate(waypoints):
        try:
            # Navigate to waypoint
            navigate_to(x, y)
            results.append(f"Waypoint {i+1}: ({x}, {y}) - Reached")
        except Exception as e:
            results.append(f"Waypoint {i+1}: ({x}, {y}) - Failed: {e}")
            break
    
    return "\n".join(results)
```

## Part 3: Integration with ROSA (15 minutes)

### Exercise 3.1: Register Custom Tools

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

# Import your custom tools
from my_first_tool import greet
from my_ros_tools import announce_status, move_distance

# Initialize LLM
llm = ChatOpenAI(model="gpt-4")

# Create ROSA with custom tools
rosa = ROSA(
    ros_version=1,
    llm=llm,
    tools=[greet, announce_status, move_distance]
)

# Test custom tools
print("=== Testing Custom Tools ===")

# Simple tool
response = rosa.invoke("Greet Dr. Smith")
print(response)

# ROS-integrated tool
response = rosa.invoke("Announce that the experiment is starting")
print(response)

# Parameterized tool
response = rosa.invoke("Move the robot forward 2 meters at 1.5 speed")
print(response)
```

### Exercise 3.2: Tool Packages

Create `robot_tools/__init__.py`:

```python
# robot_tools/__init__.py
from .navigation import move_to, rotate_to
from .manipulation import grasp, release
from .sensors import read_lidar, read_camera

__all__ = [
    'move_to',
    'rotate_to', 
    'grasp',
    'release',
    'read_lidar',
    'read_camera'
]
```

Create `robot_tools/navigation.py`:

```python
# robot_tools/navigation.py
from langchain.agents import tool

@tool
def move_to(x: float, y: float) -> str:
    """Move robot to specific coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
    """
    # Implementation
    return f"Moving to ({x}, {y})"

@tool
def rotate_to(angle: float) -> str:
    """Rotate robot to specific angle.
    
    Args:
        angle: Target angle in radians
    """
    # Implementation
    return f"Rotating to {angle} radians"
```

Use the package:

```python
import robot_tools

rosa = ROSA(
    ros_version=1,
    llm=llm,
    tool_packages=[robot_tools]
)
```

### Exercise 3.3: Tool Testing

```python
# test_custom_tools.py
import unittest
from my_first_tool import greet
from my_ros_tools import move_distance

class TestCustomTools(unittest.TestCase):
    def test_greet(self):
        result = greet("Test")
        self.assertIn("Hello, Test!", result)
    
    def test_move_distance_valid(self):
        result = move_distance(5.0, 1.0, "forward")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
    
    def test_move_distance_invalid(self):
        result = move_distance(100.0, 1.0, "forward")
        self.assertIn("error", result)
    
    def test_move_distance_invalid_direction(self):
        result = move_distance(5.0, 1.0, "sideways")
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()
```

## Best Practices

### Documentation

Always write clear docstrings:

```python
@tool
def my_tool(param1: str, param2: int = 10) -> dict:
    """Clear, one-sentence description of what the tool does.
    
    More detailed explanation if needed. Describe the purpose
    and when to use this tool.
    
    Args:
        param1: Description of first parameter
        param2: Description with default value (default: 10)
    
    Returns:
        Description of return value format
    
    Example:
        >>> my_tool("example", param2=20)
        {"status": "success", "result": "example"}
    """
```

### Error Handling

Always handle errors gracefully:

```python
@tool
def safe_tool(parameter: str) -> str:
    """Tool with comprehensive error handling."""
    try:
        # Validate input
        if not parameter:
            return "Error: Parameter cannot be empty"
        
        # Execute operation
        result = perform_operation(parameter)
        
        # Validate result
        if result is None:
            return "Error: Operation returned no result"
        
        return f"Success: {result}"
        
    except ValueError as e:
        return f"Error: Invalid parameter - {e}"
    except RuntimeError as e:
        return f"Error: Operation failed - {e}"
    except Exception as e:
        return f"Error: Unexpected error - {e}"
```

### Type Safety

Use type hints for all parameters:

```python
from typing import List, Optional, Dict, Union

@tool
def complex_tool(
    required_param: str,
    optional_param: Optional[int] = None,
    list_param: List[str] = None,
    dict_param: Dict[str, float] = None
) -> Union[Dict, str]:
    """Tool demonstrating type hints."""
    pass
```

## What's Next?

Continue your learning:

1. **Advanced Agent Customization Tutorial** - Create production-ready agents
2. **Code Examples** - See practical tool implementations
3. **API Reference** - Detailed tool creation API

## Summary

In this tutorial, you:
- ✅ Created simple and complex custom tools
- ✅ Learned advanced tool patterns (safety, composition)
- ✅ Integrated tools with ROSA
- ✅ Wrote tests for custom tools

**Key Takeaways**:
- Use `@tool` decorator for all custom tools
- Write clear docstrings with Args and Returns
- Validate all parameters
- Handle errors gracefully
- Test tools independently before integration
