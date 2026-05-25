# Architecture Overview

Understanding ROSA's system design and components.

## System Architecture

ROSA follows a layered architecture that separates concerns between the user interface, AI reasoning, tool execution, and ROS system interaction.

```
┌─────────────────────────────────────────┐
│          User Interface                 │
│  (CLI, API, Custom Applications)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          ROSA Core                      │
│  (Agent Orchestration, Memory)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        LLM Integration                  │
│  (OpenAI, Anthropic, Azure, Ollama)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Tool Management                    │
│  (Built-in Tools, Custom Tools)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        ROS Integration                  │
│  (ROS1: rospy, ROS2: rclpy)            │
└─────────────────────────────────────────┘
```

## Component Breakdown

### User Interface Layer

The entry point for user interactions. Can be:
- Direct Python API calls
- Command-line interfaces
- Custom applications (like the TurtleSim demo)
- Research experiment frameworks

### ROSA Core Layer

#### Agent Orchestration
- **ROSA Class**: Main controller managing the agent lifecycle
- **Agent Executor**: LangChain-based execution engine
- **Tool Calling Agent**: Routes user queries to appropriate tools

#### Memory Management
- **Chat History**: Maintains conversation context
- **System Prompts**: Robot-specific behavior instructions
- **Configuration State**: Runtime settings and parameters

### LLM Integration Layer

Supports multiple language model providers through LangChain abstractions:

| Provider | Class | Streaming | Token Tracking |
|----------|-------|-----------|----------------|
| OpenAI | `ChatOpenAI` | Yes | Yes |
| Azure | `AzureChatOpenAI` | Yes | Yes |
| Anthropic | `ChatAnthropic` | Yes | No |
| Ollama | `ChatOllama` | Yes | No |

**Key Design Decisions**:
- Unified interface through LangChain's `BaseChatModel`
- Streaming configuration at initialization
- Token tracking only for OpenAI/Azure (available APIs)

### Tool Management Layer

#### Built-in Tools
- **ROS1 Tools**: Direct wrappers around `rostopic`, `rosnode`, etc.
- **ROS2 Tools**: Wrappers around `ros2` command-line tools
- **Utility Tools**: Calculation, logging, system control

#### Custom Tool System
- **Registration**: Automatic discovery via `@tool` decorator
- **Injection**: Blacklist parameter injection for safety
- **Packages**: Support for grouping tools into modules

### ROS Integration Layer

#### ROS1 Integration
- Uses `rospy`, `rostopic`, `rosnode`, `rosservice`, `rosparam`
- Direct Python API calls for efficiency
- Graceful handling of ROS master connection issues

#### ROS2 Integration
- Uses `rclpy` and subprocess calls to `ros2` CLI
- Service-oriented architecture alignment
- Parameter server through node APIs

## Data Flow

### Normal Query Flow

1. **User Input**: Natural language query received
2. **Prompt Assembly**: System prompts + chat history + user query
3. **LLM Processing**: Agent reasons about which tools to use
4. **Tool Selection**: Appropriate tools identified and prepared
5. **Tool Execution**: Tools run against ROS system
6. **Response Generation**: Results formatted for user
7. **History Update**: Interaction added to chat history

```
User Query → ROSA → Prompt Template → LLM → Tool Selection
                                              ↓
User ← Response ← Result Formatting ← Tool Execution
```

### Streaming Flow

1. **Event Streaming**: LLM generates tokens incrementally
2. **Real-time Updates**: User sees response as it's generated
3. **Tool Events**: Tool start/end events interleaved with tokens
4. **Final Assembly**: Complete response assembled at end

## Extension Points

### Custom Tools

The primary extension mechanism. Tools are Python functions decorated with `@tool`:

```python
@tool
def my_tool(param: str) -> str:
    """Tool description."""
    return f"Result: {param}"

rosa = ROSA(ros_version=1, llm=llm, tools=[my_tool])
```

### Custom Prompts

RobotSystemPrompts allow tailoring agent behavior:

```python
prompts = RobotSystemPrompts(
    embodiment_and_persona="You are a...",
    critical_instructions="Always...",
)
rosa = ROSA(ros_version=1, llm=llm, prompts=prompts)
```

### Custom Agents

Extend ROSA class for specialized behavior:

```python
class MyRobotAgent(ROSA):
    def __init__(self):
        super().__init__(ros_version=1, llm=llm)
        # Add custom initialization
```

## Design Principles

### Safety First
- Tool blacklisting prevents dangerous operations
- Blacklist injection ensures consistent safety
- Critical instructions in prompts reinforce safety

### Simplicity
- Natural language as primary interface
- Automatic tool discovery and registration
- Minimal configuration for basic use

### Extensibility
- Plugin architecture for tools
- Configuration-driven behavior customization
- Clear separation of concerns

### Performance
- Streaming for real-time interaction
- Configurable iteration limits
- Efficient ROS API usage

## Key Design Decisions

### Why LangChain?
- Mature ecosystem for LLM applications
- Built-in tool calling framework
- Multiple provider support
- Active development and community

### Why Not Direct ROS API?
- ROS1 and ROS2 have different APIs
- Natural language abstraction reduces complexity
- Tool-based approach enables reasoning about actions

### Chat History Management
- Persistent by default for context
- Clearable for stateless operation
- Used by agent for multi-turn reasoning

## Next Steps

- [API Reference](api-reference.md) - Explore the implementation
- [Custom Tool Development Tutorial](../tutorials/custom-tool-development.md) - Build extensions
- [Advanced Agent Customization Tutorial](../tutorials/advanced-agent-customization.md) - Create custom agents
