# Quick Start Tutorial

Get ROSA up and running in 15 minutes.

## Learning Objectives

- Install and configure ROSA
- Connect to a ROS system
- Execute your first natural language query
- Understand the response format

**Time**: 15 minutes  
**Prerequisites**: Python 3.9+, ROS Noetic or Humble installed

## Step 1: Installation (5 minutes)

### Install ROSA

```bash
# Create virtual environment (recommended)
python3 -m venv rosa-env
source rosa-env/bin/activate

# Install ROSA
pip install jpl-rosa
```

### Verify Installation

```bash
python3 -c "from rosa import ROSA; print('ROSA installed successfully!')"
```

**Expected Output**:
```
ROSA installed successfully!
```

## Step 2: Configure LLM Access (3 minutes)

### Option A: OpenAI

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Option B: Local with Ollama (Free)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.1

# Verify
ollama list
```

## Step 3: First ROSA Interaction (5 minutes)

### Create Your First Script

Create a file called `first_rosa.py`:

```python
#!/usr/bin/env python3
from rosa import ROSA
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4")

# Create ROSA instance
print("Initializing ROSA...")
rosa = ROSA(
    ros_version=1,  # Use 2 for ROS2
    llm=llm,
    streaming=False,  # Get complete response
    verbose=True      # See what's happening
)

print("ROSA ready! Let's explore your ROS system.")
print()

# Your first query
response = rosa.invoke("List all ROS nodes currently running")
print("Response:")
print(response)
```

### Run the Script

```bash
# Make sure ROS is running
roscore &

# Source ROS environment
source /opt/ros/noetic/setup.bash

# Run your script
python3 first_rosa.py
```

**Expected Output**:
```
Initializing ROSA...
ROSA ready! Let's explore your ROS system.

Response:
The following ROS nodes are currently running:
- /rosout
```

### Try More Queries

Add these to your script:

```python
# Query 2: Topics
print("\n=== Topics ===")
response = rosa.invoke("List all topics")
print(response)

# Query 3: System overview
print("\n=== System Overview ===")
response = rosa.invoke("Give me a summary of the ROS system")
print(response)
```

## Step 4: Verify Understanding (2 minutes)

### Self-Check Questions

1. **What did ROSA do when you asked it to list nodes?**
   - [ ] It created a new node
   - [ ] It called the `rosnode_list` tool behind the scenes
   - [ ] It connected to a remote server

   **Answer**: It called the `rosnode_list` tool behind the scenes. ROSA translated your natural language query into the appropriate ROS command.

2. **What happens if ROS is not running?**
   - [ ] ROSA starts ROS automatically
   - [ ] ROSA will report that no ROS system is available
   - [ ] ROSA will crash

   **Answer**: ROSA will report that no ROS system is available. It checks first before trying to use ROS tools.

3. **Can you use ROSA with ROS2?**
   - [ ] Yes, by setting `ros_version=2`
   - [ ] No, ROSA only supports ROS1
   - [ ] Only with additional plugins

   **Answer**: Yes, by setting `ros_version=2`. ROSA supports both ROS1 and ROS2.

## Common Issues

### Issue: "No module named 'rosa'"

**Solution**: Make sure you're in the virtual environment:
```bash
source rosa-env/bin/activate
```

### Issue: "No ROS environment found"

**Solution**: Source your ROS setup:
```bash
source /opt/ros/noetic/setup.bash  # For ROS1
# OR
source /opt/ros/humble/setup.bash  # For ROS2
```

### Issue: "API key not found"

**Solution**: Set your API key:
```bash
export OPENAI_API_KEY="your-key-here"
```

## What's Next?

You've successfully run your first ROSA queries! Here's what to explore next:

### Immediate Next Steps

1. **Try the [Basic ROS Operations Tutorial](basic-ros-operations.md)** - Learn to inspect and control ROS systems
2. **Explore [Code Examples](../examples/)** - See practical use cases
3. **Read the [New ROS Developer Guide](../user-guides/new-ros-developer.md)** - Comprehensive introduction

### Practice Exercises

```python
# Exercise 1: Get system status
rosa.invoke("Is the ROS system healthy? Check nodes, topics, and services")

# Exercise 2: Topic exploration
rosa.invoke("What topics have publishers but no subscribers?")

# Exercise 3: Parameter inspection
rosa.invoke("Show me all parameters and their values")
```

## Summary

In this tutorial, you:
- ✅ Installed ROSA
- ✅ Configured LLM access
- ✅ Created your first ROSA script
- ✅ Executed natural language queries
- ✅ Received and understood responses

**Key Takeaways**:
- ROSA translates natural language to ROS commands
- You need a running ROS system for ROSA to interact with
- ROSA supports both ROS1 and ROS2
- The `verbose=True` flag shows you what's happening behind the scenes

**Time to Next Tutorial**: Continue to [Basic ROS Operations Tutorial](basic-ros-operations.md) when you're ready!
