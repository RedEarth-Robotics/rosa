# New ROS Developer Guide

Welcome! This guide is designed for developers who are new to ROS or new to ROSA. We'll help you get started with using natural language to interact with robotic systems.

## Learning Objectives

By the end of this guide, you will:
- Understand what ROSA does and how it fits into robotics
- Be able to install and configure ROSA
- Know how to ask effective questions about robot systems
- Understand basic ROS concepts through ROSA

**Estimated Time**: 60 minutes  
**Prerequisites**: Basic Python knowledge, ROS installed ([Installation Guide](../core/installation.md))

## What is ROSA?

ROSA (Robot Operating System Agent) is like having a conversational interface to your robot. Instead of writing complex ROS commands, you can ask questions in plain English:

**Instead of**:
```bash
rostopic list | grep cmd_vel
rosnode info /turtle1
```

**You say**:
```
"What topics control the turtle's movement?"
"Tell me about the turtle1 node"
```

### Key Benefits for New ROS Developers

- **Learn by asking**: Discover ROS concepts through natural conversation
- **See the commands**: ROSA shows you what ROS commands it uses
- **Safety built-in**: Won't execute dangerous operations accidentally
- **Progressive complexity**: Start simple and gradually learn more

## Understanding ROS Through ROSA

### ROS Concepts Simplified

#### Nodes
Think of nodes as individual programs running on your robot. Each node does one thing:
- A camera node reads from a camera
- A motor control node moves wheels
- A navigation node plans paths

**Try it**:
```python
rosa.invoke("List all the nodes currently running")
```

**ROSA might respond**:
```
The following nodes are running:
- /turtle1 (turtlesim node)
- /teleop (keyboard control)
- /rosout (logging)
```

#### Topics
Topics are communication channels between nodes. They carry messages like sensor data or commands:

**Try it**:
```python
rosa.invoke("List all topics and explain what each one does")
```

**ROSA might explain**:
```
Topics are like radio channels:
- /turtle1/cmd_vel: Commands for turtle movement
- /turtle1/pose: Current position of turtle
- /rosout: System log messages
```

#### Services
Services are like function calls between nodes. You request something and get a response:

**Try it**:
```python
rosa.invoke("What services are available? What can they do?")
```

### Common First Queries

Here are great starting queries to learn ROS:

```python
# System Overview
rosa.invoke("Give me an overview of the current ROS system")

# Topic Exploration
rosa.invoke("List all topics and group them by type")

# Node Details
rosa.invoke("Show me what each node is doing")

# Understanding Messages
rosa.invoke("What type of messages does /turtle1/cmd_vel use?")

# Parameters
rosa.invoke("Show me all parameters and explain their purpose")
```

## Effective Question Patterns

### Be Specific

**Good**:
```python
rosa.invoke("List all topics that have publishers but no subscribers")
```

**Less Effective**:
```python
rosa.invoke("Show me topics")
```

### Ask for Explanations

ROSA can explain what it finds:

```python
rosa.invoke("What nodes control the robot's movement and how do they work together?")
```

### Request Step-by-Step

```python
rosa.invoke("Walk me through how a movement command gets from the keyboard to the robot")
```

## Safety and Best Practices

### What ROSA Won't Do

ROSA is designed to be safe by default:
- Won't execute commands without your query
- Respects blacklist of dangerous operations
- Explains what it's going to do before doing it

### Understanding Responses

Always read ROSA's response carefully:

```python
response = rosa.invoke("Move the turtle forward")
print(response)

# Response: "I'll publish a Twist message to /turtle1/cmd_vel 
#           with linear.x = 2.0 for 1 second"
```

## Hands-On Exercise: First Robot Interaction

### Exercise 1: System Exploration (15 min)

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

# Setup
llm = ChatOpenAI(model="gpt-4")
rosa = ROSA(ros_version=1, llm=llm, verbose=True)

# Task 1: System Overview
print("=== Task 1: System Overview ===")
response = rosa.invoke("Describe the current ROS system")
print(response)

# Task 2: Topic Discovery
print("\n=== Task 2: Topic Discovery ===")
response = rosa.invoke("List all topics and categorize them")
print(response)

# Task 3: Node Understanding
print("\n=== Task 3: Node Understanding ===")
response = rosa.invoke("Explain what each node does and how they connect")
print(response)
```

### Exercise 2: Basic Control (15 min)

```python
# Task 4: Simple Movement
print("=== Task 4: Simple Movement ===")
response = rosa.invoke("Make the turtle move forward slowly for 2 seconds")
print(response)

# Task 5: Position Check
print("\n=== Task 5: Position Check ===")
response = rosa.invoke("Where is the turtle now? Show me its coordinates")
print(response)
```

## Common New Developer Questions

### "How do I know what questions to ask?"

Start with these patterns:
- "Show me..." (lists, overviews)
- "Explain..." (concepts, how things work)
- "What is..." (definitions, types)
- "How do I..." (actions, procedures)

### "What if ROSA can't do something?"

ROSA will tell you! If it can't access something or doesn't have a tool, it will explain:
```python
rosa.invoke("Launch a new ROS node")  
# Response: "I don't have a tool to launch nodes, but I can tell you..."
```

### "How do I learn more about ROS?"

Use ROSA as your tutor:
```python
rosa.invoke("Teach me about ROS services with examples")
rosa.invoke("What's the difference between topics and services?")
rosa.invoke("Show me a typical ROS workflow")
```

## Progression Path

### Beginner (You Are Here)
- Understanding basic ROS concepts through queries
- Simple system inspection
- Basic robot control

### Intermediate
- Custom tool development
- Advanced queries with conditions
- Multi-step operations

### Advanced
- Custom agent creation
- Research integration
- Production deployment

## Next Steps

Continue your learning journey:

1. [Quick Start Tutorial](../tutorials/quick-start.md) - 15-minute hands-on introduction
2. [Basic ROS Operations Tutorial](../tutorials/basic-ros-operations.md) - Learn ROS inspection and control
3. [Experienced ROS Developer Guide](experienced-ros-developer.md) - When you're ready for advanced features

## Tips for Success

1. **Start Simple**: Begin with basic queries and gradually increase complexity
2. **Read Responses**: ROSA often explains what it's doing - this is educational
3. **Experiment**: Try different queries to see what ROSA can do
4. **Use Verbose Mode**: Enable `verbose=True` to see the tools ROSA uses
5. **Ask for Help**: If stuck, ask ROSA to explain something differently

Remember: ROSA is a tool to help you learn ROS faster. The more you use it, the more comfortable you'll become with both ROSA and ROS concepts.
