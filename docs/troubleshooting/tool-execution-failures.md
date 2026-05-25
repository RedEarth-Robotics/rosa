# Tool Execution Failures

Diagnosing and fixing tool execution errors.

## Quick Diagnostics

Enable verbose mode to see tool execution:

```python
from rosa import ROSA

rosa = ROSA(ros_version=1, llm=llm, verbose=True)
```

## Common Problems

### Problem: Tool timeout

**Symptoms**:
Tool execution hangs and eventually fails.

**Solutions**:

1. **Check ROS system responsiveness**:
```bash
rostopic list  # Should be instant
```

2. **Reduce tool parameters**:
```python
# Instead of 1000 messages
rosa.invoke("Echo 10 messages from /topic")
```

3. **Set ROSA iteration limit**:
```python
rosa = ROSA(ros_version=1, llm=llm, max_iterations=10)
```

### Problem: Tool not found

**Symptoms**:
ROSA says it doesn't have a tool for a task.

**Solutions**:

1. **Check tool registration**:
```python
# Verify tools are registered
print(rosa._ROSA__tools.get_tools())
```

2. **Use correct tool names**:
```python
# ROSA uses specific tool names
rosa.invoke("List all topics")  # Uses rostopic_list
rosa.invoke("List all nodes")   # Uses rosnode_list
```

3. **Add custom tools**:
```python
from langchain.agents import tool

@tool
def my_tool():
    return "Result"

rosa = ROSA(ros_version=1, llm=llm, tools=[my_tool])
```

### Problem: ROS command fails

**Symptoms**:
Tool returns ROS error message.

**Solutions**:

1. **Check ROS environment**:
```bash
source /opt/ros/noetic/setup.bash
rostopic list
```

2. **Verify topic/node exists**:
```bash
rostopic list | grep <topic_name>
rosnode list | grep <node_name>
```

3. **Check message type**:
```bash
rostopic type <topic_name>
```

### Problem: Invalid parameters

**Symptoms**:
Tool fails with parameter validation error.

**Solutions**:

1. **Check parameter types**:
```python
# Ensure correct types
rosa.invoke("Move forward at speed 2.0")  # Float
rosa.invoke("Echo 10 messages")           # Int
```

2. **Use verbose mode**:
```python
rosa = ROSA(ros_version=1, llm=llm, verbose=True)
# See exactly what parameters are passed
```

### Problem: Permission denied

**Symptoms**:
Tool fails with permission error.

**Solutions**:

1. **Check file permissions**:
```bash
ls -la <file_path>
chmod 755 <file_path>
```

2. **Run without sudo**:
```bash
# Correct
rostopic list

# Wrong
sudo rostopic list
```

3. **Fix ROS permissions**:
```bash
sudo chown -R $USER:$USER ~/.ros
```

## Debugging Tools

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

rosa = ROSA(ros_version=1, llm=llm, verbose=True)
```

### Check Tool Availability

```python
# List all available tools
tools = rosa._ROSA__tools.get_tools()
for tool in tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
```

### Test Individual Tools

```python
# Test specific tool directly
from rosa.tools.ros1 import rostopic_list

result = rostopic_list({"pattern": None, "namespace": None})
print(result)
```

## Next Steps

- [Performance Problems](performance-problems.md)
- [Debugging Tools](debugging-tools.md)
- [Custom Tool Development Tutorial](../tutorials/custom-tool-development.md)
