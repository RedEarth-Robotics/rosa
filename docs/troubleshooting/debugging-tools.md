# Debugging Tools

Tools and techniques for debugging ROSA issues.

## Built-in Debugging

### Verbose Mode

Enable verbose output to see what's happening:

```python
from rosa import ROSA

rosa = ROSA(ros_version=1, llm=llm, verbose=True)
response = rosa.invoke("List all topics")
```

**Output shows**:
- Which tools are being called
- Parameters being passed
- Intermediate reasoning steps

### Logging

```python
import logging

# Set logging level
logging.basicConfig(level=logging.DEBUG)

# ROSA-specific logging
logging.getLogger("rosa").setLevel(logging.DEBUG)
logging.getLogger("langchain").setLevel(logging.DEBUG)
```

## Diagnostic Queries

### System Health Check

```python
# Comprehensive diagnostic
response = rosa.invoke("""
Run a complete system diagnostic:
1. Check if ROS is running
2. List all nodes, topics, services
3. Check for any errors or warnings
4. Report overall system status
""")
print(response)
```

### Tool Testing

```python
# Test individual tools
from rosa.tools.ros1 import rostopic_list
from rosa.tools.ros2 import ros2_topic_list

# ROS1
result = rostopic_list({"pattern": None, "namespace": None})
print("ROS1 topics:", result)

# ROS2
result = ros2_topic_list({"pattern": None, "namespace": None})
print("ROS2 topics:", result)
```

### LLM Testing

```python
# Test LLM connection
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
try:
    response = llm.invoke("Hello, are you working?")
    print("LLM OK:", response)
except Exception as e:
    print("LLM Error:", e)
```

## Common Debugging Scenarios

### Scenario 1: ROSA not responding

**Steps**:
1. Check if ROS is running
2. Test LLM connection
3. Enable verbose mode
4. Try a simple query

```python
# Diagnostic script
def diagnose_rosa(rosa):
    print("=== ROSA Diagnostics ===")
    
    # 1. Check ROS
    try:
        import rospy
        print("✓ ROS Python modules available")
    except:
        print("✗ ROS Python modules not found")
    
    # 2. Check LLM
    try:
        response = rosa.invoke("Hello")
        print("✓ LLM responding")
    except:
        print("✗ LLM not responding")
    
    # 3. Check tools
    tools = rosa._ROSA__tools.get_tools()
    print(f"✓ {len(tools)} tools registered")
    
    return True
```

### Scenario 2: Unexpected responses

**Steps**:
1. Check system prompts
2. Verify tool availability
3. Test with simple query
4. Check chat history

```python
# Debug unexpected behavior
def debug_response(rosa, query):
    print(f"Query: {query}")
    print(f"Chat history: {len(rosa.chat_history)} messages")
    
    # Clear history and retry
    rosa.clear_chat()
    response = rosa.invoke(query)
    print(f"Response: {response}")
    
    return response
```

### Scenario 3: Tool execution errors

**Steps**:
1. Enable verbose mode
2. Test tool directly
3. Check ROS connectivity
4. Verify parameters

```python
# Debug tool execution
def debug_tool(rosa, query):
    rosa = ROSA(ros_version=1, llm=llm, verbose=True, return_intermediate_steps=True)
    
    response = rosa.invoke(query)
    print(f"Response: {response}")
    
    # Check intermediate steps
    if hasattr(rosa, 'intermediate_steps'):
        for step in rosa.intermediate_steps:
            print(f"Step: {step}")
    
    return response
```

## External Debugging Tools

### ROS Tools

```bash
# ROS system inspection
rostopic list
rosnode list
rosservice list
rosparam list

# Topic monitoring
rostopic echo /topic_name
rostopic hz /topic_name

# Node inspection
rosnode info /node_name

# System logs
roscd log
cat rosout.log
```

### Python Debugging

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Print debug info
print(f"Debug: variable = {variable}")

# Inspect objects
import inspect
print(inspect.getsource(my_function))
```

## Creating Debug Scripts

### System Info Script

```python
#!/usr/bin/env python3
"""Print system information for debugging."""

import sys
import os
import rosa

def print_system_info():
    print("=== System Information ===")
    print(f"Python: {sys.version}")
    print(f"ROSA: {rosa.__version__}")
    print(f"ROS: {os.environ.get('ROS_DISTRO', 'Not set')}")
    print(f"ROS_MASTER_URI: {os.environ.get('ROS_MASTER_URI', 'Not set')}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")
    
    # Check ROS
    try:
        import rospy
        print("✓ ROS1 available")
    except:
        print("✗ ROS1 not available")
    
    try:
        import rclpy
        print("✓ ROS2 available")
    except:
        print("✗ ROS2 not available")

if __name__ == "__main__":
    print_system_info()
```

## Next Steps

- [Installation Issues](installation-issues.md)
- [ROS Connection Problems](ros-connection-problems.md)
- [Troubleshooting Guide](../user-guides/troubleshooting.md)
