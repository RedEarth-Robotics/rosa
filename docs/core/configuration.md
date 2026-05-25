# Configuration Guide

This guide covers how to configure ROSA for different setups, LLM providers, and use cases.

## Basic Configuration

### ROS Version Selection

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

# ROS1
llm = ChatOpenAI(model="gpt-4")
rosa = ROSA(ros_version=1, llm=llm)

# ROS2
rosa = ROSA(ros_version=2, llm=llm)
```

### LLM Provider Configuration

#### OpenAI

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    api_key="your-api-key"  # or set OPENAI_API_KEY env var
)
```

#### Anthropic

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-opus-20240229",
    temperature=0,
    api_key="your-api-key"
)
```

#### Azure OpenAI

```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-4",
    api_version="2024-02-01",
    temperature=0
)
```

#### Ollama (Local)

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url="http://localhost:11434",
    model="llama3.1",
    temperature=0,
    num_ctx=8192
)
```

## Advanced Configuration

### Streaming vs Non-Streaming

```python
# Streaming (real-time response)
rosa = ROSA(ros_version=1, llm=llm, streaming=True)

# Non-streaming (complete response at once)
rosa = ROSA(ros_version=1, llm=llm, streaming=False)
```

### Token Usage Tracking

```python
# Track token usage (OpenAI/Azure only)
rosa = ROSA(
    ros_version=1,
    llm=llm,
    show_token_usage=True,
    streaming=False  # Must be False for token tracking
)
```

### Chat History Management

```python
# Enable chat history accumulation (default)
rosa = ROSA(ros_version=1, llm=llm, accumulate_chat_history=True)

# Disable for stateless operation
rosa = ROSA(ros_version=1, llm=llm, accumulate_chat_history=False)

# Clear history
rosa.clear_chat()
```

### Maximum Iterations

```python
# Limit agent iterations to prevent runaway execution
rosa = ROSA(ros_version=1, llm=llm, max_iterations=50)
```

### Intermediate Steps

```python
# Return detailed execution trace
rosa = ROSA(
    ros_version=1,
    llm=llm,
    return_intermediate_steps=True
)
```

## Safety Configuration

### Tool Blacklisting

```python
# Prevent dangerous operations
rosa = ROSA(
    ros_version=1,
    llm=llm,
    blacklist=["emergency_stop", "motor_kill", "override_safety"]
)
```

### Custom Prompts

```python
from rosa.prompts import RobotSystemPrompts

robot_prompts = RobotSystemPrompts(
    embodiment_and_persona="You are a warehouse navigation robot",
    critical_instructions="Always check for obstacles before moving",
    constraints_and_guardrails="Never move faster than 1 m/s",
    about_your_environment="Indoor warehouse with shelves and aisles",
    about_your_capabilities="Navigate, pick up boxes, avoid obstacles",
    mission_and_objectives="Transport boxes between warehouse zones"
)

rosa = ROSA(ros_version=1, llm=llm, prompts=robot_prompts)
```

## Performance Tuning

### Verbosity

```python
# Enable verbose output for debugging
rosa = ROSA(ros_version=1, llm=llm, verbose=True)
```

### System Verbosity

```python
from rosa.tools.system import set_verbosity

# Set global verbosity
set_verbosity(True)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | Required |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | Required |
| `AZURE_OPENAI_API_VERSION` | Azure API version | `2024-02-01` |
| `ROS_VERSION` | ROS version (1 or 2) | Auto-detected |
| `ROSA_VERBOSE` | Enable verbose mode | `False` |

## Configuration Examples

### Production Configuration

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)

rosa = ROSA(
    ros_version=1,
    llm=llm,
    streaming=True,
    verbose=False,
    max_iterations=50,
    blacklist=["emergency_stop"],
    accumulate_chat_history=True
)
```

### Research Configuration

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)

rosa = ROSA(
    ros_version=1,
    llm=llm,
    streaming=False,
    show_token_usage=True,
    return_intermediate_steps=True,
    accumulate_chat_history=False
)
```

## Performance Configuration

ROSA provides several performance tuning options:

### Caching

Enable caching (default: `True`) to reduce redundant ROS queries:

```python
agent = ROSA(
    ros_version=1,
    llm=llm,
    enable_caching=True,  # Master switch for all caching
    max_cache_entries=500,  # Tool cache size limit
)
```

### Chat History Management

Control memory usage with history strategies:

| Strategy | Behavior | Best For |
|----------|----------|----------|
| `accumulate` | Keep all messages (default) | Short conversations |
| `window` | Keep last N pairs | Medium conversations |
| `token_budget` | Enforce max token count | Long conversations |
| `summarize` | Summarize old, keep recent | Very long conversations |

```python
agent = ROSA(
    ros_version=1,
    llm=llm,
    history_strategy="window",
    history_window_size=20,
)
```

### Profiling

Enable profiling to collect performance metrics:

```python
agent = ROSA(
    ros_version=1,
    llm=llm,
    enable_profiling=True,
)
```

Access metrics via the `get_performance_metrics` tool.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROSA_ENABLE_CACHING` | Enable/disable caching | `true` |
| `ROSA_HISTORY_STRATEGY` | Chat history strategy | `accumulate` |
| `ROSA_TOKEN_BUDGET` | Token budget for history | `8000` |

## Next Steps

- [API Reference](api-reference.md) - Explore all ROSA capabilities
- [Troubleshooting Guide](../troubleshooting/) - Resolve configuration issues
- [Custom Tool Development Tutorial](../tutorials/custom-tool-development.md) - Build your own tools
