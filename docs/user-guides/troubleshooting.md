# Troubleshooting Guide

Common issues and solutions when working with ROSA.

## Quick Diagnostics

Before diving into specific issues, try these quick diagnostic commands:

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

# Test basic connectivity
llm = ChatOpenAI(model="gpt-4")
rosa = ROSA(ros_version=1, llm=llm, verbose=True)

# Diagnostic query
response = rosa.invoke("Run a system health check")
print(response)
```

## Installation Issues

### pip install fails

**Symptom**: `pip install jpl-rosa` fails with dependency errors

**Solutions**:

1. **Use virtual environment**:
```bash
python3 -m venv rosa-env
source rosa-env/bin/activate
pip install jpl-rosa
```

2. **Upgrade pip**:
```bash
pip install --upgrade pip
pip install jpl-rosa
```

3. **Install with dependencies**:
```bash
pip install jpl-rosa[all]
```

### tiktoken build fails

**Symptom**: Installation fails with Rust compilation errors

**Solution**:
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Reinstall tiktoken
pip install --force-reinstall tiktoken
```

### Module not found after installation

**Symptom**: `ModuleNotFoundError: No module named 'rosa'`

**Solutions**:

1. **Check Python path**:
```bash
python3 -c "import sys; print(sys.path)"
```

2. **Verify installation**:
```bash
pip show jpl-rosa
```

3. **Reinstall with correct Python**:
```bash
python3.9 -m pip install jpl-rosa
```

## ROS Connection Problems

### ROS master not found

**Symptom**: `roscore cannot run as there is already one running` or connection errors

**Solutions**:

1. **Source ROS environment**:
```bash
source /opt/ros/noetic/setup.bash
```

2. **Check ROS master**:
```bash
roscore &
rostopic list
```

3. **Set ROS_MASTER_URI**:
```bash
export ROS_MASTER_URI=http://localhost:11311
```

### Cannot list topics or nodes

**Symptom**: ROSA returns empty lists or connection errors

**Diagnostics**:
```python
# Check if ROS is running
import rospy
print(rospy.get_master().getSystemState())
```

**Solutions**:

1. **Verify ROS environment**:
```bash
echo $ROS_DISTRO
echo $ROS_MASTER_URI
```

2. **Check node initialization**:
```python
import rospy
rospy.init_node('rosa_test', anonymous=True)
print("ROS node initialized successfully")
```

3. **Network issues** (for remote ROS):
```bash
# Test connectivity
ping $ROS_MASTER_URI
# Check firewall settings
sudo ufw status
```

### Permission denied errors

**Symptom**: Cannot access ROS topics or services

**Solutions**:

1. **Fix ROS workspace permissions**:
```bash
sudo chown -R $USER:$USER ~/.ros
chmod -R 755 ~/.ros
```

2. **Run with proper user**:
```bash
# Don't use sudo for ROS commands
rostopic list  # Correct
sudo rostopic list  # Wrong
```

## LLM Provider Issues

### API key not found

**Symptom**: `AuthenticationError` or `API key not found`

**Solutions**:

1. **Set environment variables**:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

2. **Use .env file**:
```bash
# .env file
OPENAI_API_KEY=sk-...
```
```python
from dotenv import load_dotenv
load_dotenv()
```

3. **Pass key directly** (not recommended for production):
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(api_key="sk-...")
```

### Rate limit errors

**Symptom**: `RateLimitError` or `Too many requests`

**Solutions**:

1. **Implement retry logic**:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    max_retries=5,
    request_timeout=30
)
```

2. **Use retry decorator**:
```python
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

3. **Check usage dashboard**:
- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/settings/usage

### Model not available

**Symptom**: `Model not found` or `Invalid model`

**Solutions**:

1. **Verify model name**:
```python
# Correct
ChatOpenAI(model="gpt-4")

# Incorrect
ChatOpenAI(model="gpt4")
```

2. **Check available models**:
```bash
# OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

3. **Use fallback model**:
```python
from langchain_openai import ChatOpenAI

try:
    llm = ChatOpenAI(model="gpt-4")
except Exception:
    llm = ChatOpenAI(model="gpt-3.5-turbo")
```

## Tool Execution Failures

### Tool timeout

**Symptom**: Tool execution hangs or times out

**Solutions**:

1. **Check ROS system responsiveness**:
```bash
rostopic list  # Should be fast
```

2. **Reduce tool parameters**:
```python
# Instead of:
rosa.invoke("Echo 1000 messages from /topic")

# Use:
rosa.invoke("Echo 10 messages from /topic")
```

3. **Set ROSA timeout**:
```python
rosa = ROSA(
    ros_version=1,
    llm=llm,
    max_iterations=20  # Limit execution time
)
```

### Tool returns error

**Symptom**: Tool execution fails with ROS error

**Diagnostics**:
```python
# Enable verbose mode to see tool execution
rosa = ROSA(ros_version=1, llm=llm, verbose=True)
```

**Solutions**:

1. **Check topic existence**:
```bash
rostopic list | grep <topic_name>
```

2. **Verify message type**:
```bash
rostopic type <topic_name>
```

3. **Check node status**:
```bash
rosnode info <node_name>
```

### Tool not found

**Symptom**: ROSA says it doesn't have a tool for a task

**Solutions**:

1. **Check available tools**:
```python
print(rosa.chat_history)  # See what tools were used
```

2. **Use correct tool name**:
```python
# ROSA tools use specific names
rosa.invoke("List all topics")  # Uses rostopic_list
rosa.invoke("List all nodes")   # Uses rosnode_list
```

3. **Add custom tools**:
```python
from langchain.agents import tool

@tool
def my_custom_tool():
    return "Result"

rosa = ROSA(ros_version=1, llm=llm, tools=[my_custom_tool])
```

## Performance Problems

### Slow responses

**Symptom**: ROSA takes a long time to respond

**Diagnostics**:
```python
import time

start = time.time()
response = rosa.invoke("List all topics")
print(f"Time: {time.time() - start:.2f}s")
```

**Solutions**:

1. **Use non-streaming mode**:
```python
rosa = ROSA(ros_version=1, llm=llm, streaming=False)
```

2. **Limit iterations**:
```python
rosa = ROSA(ros_version=1, llm=llm, max_iterations=10)
```

3. **Use faster model**:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")  # Faster than gpt-4
```

### High token usage

**Symptom**: High API costs or token limit errors

**Solutions**:

1. **Track token usage**:
```python
rosa = ROSA(
    ros_version=1,
    llm=llm,
    show_token_usage=True,
    streaming=False
)
```

2. **Use concise queries**:
```python
# Instead of:
rosa.invoke("Can you please show me all the topics that are currently available in the system?")

# Use:
rosa.invoke("List all topics")
```

3. **Limit response context**:
```python
rosa = ROSA(
    ros_version=1,
    llm=llm,
    accumulate_chat_history=False  # Don't accumulate history
)
```

### Memory issues

**Symptom**: Out of memory errors or high RAM usage

**Solutions**:

1. **Clear chat history regularly**:
```python
rosa.clear_chat()
```

2. **Disable intermediate steps**:
```python
rosa = ROSA(
    ros_version=1,
    llm=llm,
    return_intermediate_steps=False
)
```

3. **Limit tool output**:
```python
rosa.invoke("List first 10 topics only")
```

## Still Having Issues?

### Enable Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

rosa = ROSA(ros_version=1, llm=llm, verbose=True)
```

### Check System Requirements

```bash
# Python version
python3 --version  # Should be 3.9+

# ROS version
rosversion -d  # Should be noetic or humble

# Disk space
df -h

# Memory
free -h
```

### Report Issues

When reporting issues, include:
1. ROSA version: `pip show jpl-rosa`
2. Python version: `python3 --version`
3. ROS version: `echo $ROS_DISTRO`
4. Error message (full traceback)
5. Steps to reproduce

**Where to report**:
- GitHub Issues: https://github.com/nasa-jpl/rosa/issues
- Include `[TROUBLESHOOTING]` in the title

## Next Steps

- [Troubleshooting Center](../troubleshooting/) - Detailed guides for each category
- [Installation Guide](../core/installation.md) - Setup instructions
- [Configuration Guide](../core/configuration.md) - Advanced configuration
