# API Reference

Complete reference for the ROSA Python API.

## ROSA Class

The main interface for interacting with ROS systems using natural language.

### Constructor

```python
ROSA(
    ros_version: Literal[1, 2],
    llm: ChatModel,
    tools: Optional[list] = None,
    tool_packages: Optional[list] = None,
    prompts: Optional[RobotSystemPrompts] = None,
    verbose: bool = False,
    blacklist: Optional[list] = None,
    accumulate_chat_history: bool = True,
    show_token_usage: bool = False,
    streaming: bool = True,
    max_iterations: int = 100,
    return_intermediate_steps: bool = False,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ros_version` | `Literal[1, 2]` | Required | ROS version to interact with |
| `llm` | `ChatModel` | Required | Language model for generating responses |
| `tools` | `Optional[list]` | `None` | Additional LangChain tool functions |
| `tool_packages` | `Optional[list]` | `None` | Python packages containing tools |
| `prompts` | `Optional[RobotSystemPrompts]` | `None` | Custom system prompts |
| `verbose` | `bool` | `False` | Print verbose output |
| `blacklist` | `Optional[list]` | `None` | ROS tools to exclude |
| `accumulate_chat_history` | `bool` | `True` | Accumulate chat history |
| `show_token_usage` | `bool` | `False` | Show token usage (non-streaming only) |
| `streaming` | `bool` | `True` | Stream output |
| `max_iterations` | `int` | `100` | Maximum agent iterations |
| `return_intermediate_steps` | `bool` | `False` | Return execution trace |

### Methods

#### `invoke(query: str) -> str`

Process a user query and return the response.

```python
rosa = ROSA(ros_version=1, llm=llm)
response = rosa.invoke("List all ROS nodes")
print(response)
```

**Parameters**:
- `query`: User's natural language query

**Returns**: Agent's response as a string

**Raises**: Exceptions are caught and returned as error messages

#### `astream(query: str) -> AsyncIterable[Dict[str, Any]]`

Asynchronously stream the agent's response.

```python
async for event in rosa.astream("List all ROS nodes"):
    if event["type"] == "token":
        print(event["content"], end="")
    elif event["type"] == "tool_start":
        print(f"Tool: {event['name']}")
```

**Parameters**:
- `query`: User's natural language query

**Returns**: Async iterable of event dictionaries

**Event Types**:
- `token`: Generated token with `content`
- `tool_start`: Tool execution start with `name` and `input`
- `tool_end`: Tool execution end with `name` and `output`
- `final`: Final output with `content`
- `error`: Error with `content`

#### `clear_chat()`

Clear the chat history.

```python
rosa.clear_chat()
```

#### `chat_history` (property)

Get the current chat history.

```python
history = rosa.chat_history
for message in history:
    print(f"{message.type}: {message.content}")
```

## RobotSystemPrompts

Customize ROSA's behavior for specific robots.

### Constructor

```python
RobotSystemPrompts(
    embodiment_and_persona: Optional[str] = None,
    about_your_operators: Optional[str] = None,
    critical_instructions: Optional[str] = None,
    constraints_and_guardrails: Optional[str] = None,
    about_your_environment: Optional[str] = None,
    about_your_capabilities: Optional[str] = None,
    nuance_and_assumptions: Optional[str] = None,
    mission_and_objectives: Optional[str] = None,
    environment_variables: Optional[dict] = None,
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `embodiment_and_persona` | `Optional[str]` | Robot's identity and personality |
| `about_your_operators` | `Optional[str]` | Who works with the robot |
| `critical_instructions` | `Optional[str]` | Must-follow safety rules |
| `constraints_and_guardrails` | `Optional[str]` | Operational limits |
| `about_your_environment` | `Optional[str]` | Physical environment description |
| `about_your_capabilities` | `Optional[str]` | What the robot can do |
| `nuance_and_assumptions` | `Optional[str]` | Contextual assumptions |
| `mission_and_objectives` | `Optional[str]` | Primary goals |
| `environment_variables` | `Optional[dict]` | Robot-specific variables |

### Example

```python
from rosa.prompts import RobotSystemPrompts

warehouse_bot = RobotSystemPrompts(
    embodiment_and_persona="You are a warehouse navigation robot",
    critical_instructions="Always check for obstacles before moving",
    constraints_and_guardrails="Never move faster than 1 m/s",
    about_your_environment="Indoor warehouse with shelves and aisles",
    about_your_capabilities="Navigate, pick up boxes, avoid obstacles",
    mission_and_objectives="Transport boxes between warehouse zones"
)

rosa = ROSA(ros_version=1, llm=llm, prompts=warehouse_bot)
```

## ROSATools

Manage and extend ROSA's tool set.

### Built-in Tools

ROSA automatically includes tools based on the ROS version:

**ROS1 Tools**: calculation, log, system, ros1 (rostopic, rosnode, rosservice, rosparam, etc.)
**ROS2 Tools**: calculation, log, system, ros2 (ros2 topic, ros2 node, ros2 service, ros2 param, etc.)

### Custom Tool Creation

```python
from langchain.agents import tool

@tool
def my_custom_tool(parameter: str) -> str:
    """Description of what the tool does.
    
    Args:
        parameter: Description of parameter
    
    Returns:
        Description of return value
    """
    # Tool implementation
    return f"Result: {parameter}"

# Add to ROSA
rosa = ROSA(ros_version=1, llm=llm, tools=[my_custom_tool])
```

### Custom Tool Packages

```python
# my_tools.py
from langchain.agents import tool

@tool
def tool1():
    return "Tool 1 result"

@tool  
def tool2():
    return "Tool 2 result"
```

```python
import my_tools

rosa = ROSA(ros_version=1, llm=llm, tool_packages=[my_tools])
```

## Tool Creation Best Practices

### Parameter Types

Use type hints for all parameters:

```python
from typing import List, Optional

@tool
def move_robot(
    velocity: float,
    direction: str,
    waypoints: Optional[List[tuple]] = None
) -> str:
    """Move robot with specified parameters."""
    return f"Moving at {velocity} m/s in {direction} direction"
```

### Error Handling

Always handle errors gracefully:

```python
@tool
def safe_operation(parameter: str) -> str:
    """Perform a safe operation."""
    try:
        result = perform_operation(parameter)
        return f"Success: {result}"
    except Exception as e:
        return f"Error: {str(e)}. Please check your parameters."
```

### Documentation

Write clear docstrings:

```python
@tool
def complex_tool(
    required_param: str,
    optional_param: int = 10
) -> dict:
    """Perform a complex operation on the robot.
    
    This tool does multiple things including A, B, and C.
    Use this when you need to perform all three operations together.
    
    Args:
        required_param: Description of required parameter
        optional_param: Description with default value (default: 10)
    
    Returns:
        Dictionary with keys: 'status', 'result', 'message'
    
    Example:
        complex_tool("example", optional_param=20)
    """
    return {"status": "success", "result": "done", "message": "Operation completed"}
```

## Next Steps

- [ROS Tools Reference](ros-tools-reference.md) - Built-in ROS tools documentation
- [Custom Tool Development Tutorial](../tutorials/custom-tool-development.md) - Build custom tools
- [Configuration Guide](configuration.md) - Advanced configuration options
