# Basic ROS Operations Tutorial

Learn how to inspect, monitor, and control ROS systems using ROSA.

## Learning Objectives

- Inspect ROS system state (nodes, topics, services, parameters)
- Monitor robot data in real-time
- Execute basic robot control commands
- Understand ROSA's reasoning process

**Time**: 45 minutes  
**Prerequisites**: Quick Start Tutorial completed, ROS system running

## Part 1: System Inspection (15 minutes)

### Exercise 1.1: Comprehensive System Overview

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
rosa = ROSA(ros_version=1, llm=llm, verbose=True)

# Get comprehensive overview
print("=== System Overview ===")
response = rosa.invoke("""
Give me a complete overview of the ROS system:
1. List all nodes and what they do
2. List all topics with their types
3. List all services
4. List all parameters
""")
print(response)
```

**What to Look For**:
- Node names and purposes
- Topic types (e.g., `geometry_msgs/Twist`)
- Service availability
- Parameter values

### Exercise 1.2: Node Analysis

```python
# Deep dive into specific nodes
print("\n=== Node Analysis ===")
response = rosa.invoke("""
Analyze the /turtle1 node:
- What topics does it publish?
- What topics does it subscribe to?
- What services does it provide?
- What's its purpose?
""")
print(response)
```

**Expected Understanding**:
- Publishers: Output data (e.g., pose)
- Subscribers: Input commands (e.g., velocity)
- Services: Request-response operations

### Exercise 1.3: Topic Filtering

```python
# Find specific types of topics
print("\n=== Topic Filtering ===")
response = rosa.invoke("""
Show me all topics related to:
- Movement or velocity
- Sensor data
- Configuration or parameters
Separate them into categories.
""")
print(response)
```

**Practice Task**: Try different filter queries:
- "Show topics containing 'cmd'"
- "What topics have no subscribers?"
- "List all image or camera topics"

## Part 2: Data Monitoring (15 minutes)

### Exercise 2.1: Topic Echo

```python
# Monitor topic data
print("=== Topic Monitoring ===")
response = rosa.invoke("""
Echo 5 messages from /turtle1/pose and explain:
- What does each field mean?
- What's the turtle's current position?
- Is it moving or stationary?
""")
print(response)
```

**Key Concepts**:
- Message fields (x, y, theta, linear_velocity, angular_velocity)
- Real-time vs. requested data
- Message frequency

### Exercise 2.2: Velocity Commands

```python
# Understand movement commands
print("\n=== Velocity Commands ===")
response = rosa.invoke("""
Show me what's being published to /turtle1/cmd_vel:
- What are the linear and angular values?
- What do these values mean?
- How do they control the turtle?
""")
print(response)
```

**Understanding**:
- `linear.x`: Forward/backward speed
- `angular.z`: Rotation speed
- Combined for curved motion

### Exercise 2.3: System Health Check

```python
# Comprehensive health check
print("\n=== Health Check ===")
response = rosa.invoke("""
Perform a system health check:
1. Are all expected nodes running?
2. Are critical topics being published?
3. Are there any errors or warnings?
4. What's the overall system status?
""")
print(response)
```

## Part 3: Basic Control (15 minutes)

### Exercise 3.1: Simple Movement

```python
# Basic movement control
print("=== Simple Movement ===")
response = rosa.invoke("""
Make the turtle move:
1. Move forward at 2.0 units/second for 1 second
2. Stop
3. Report the turtle's final position
""")
print(response)
```

**Understanding the Response**:
- ROSA will use `publish_twist_to_cmd_vel` tool
- It calculates the expected position
- It verifies the actual position

### Exercise 3.2: Rotation

```python
# Rotation control
print("\n=== Rotation ===")
response = rosa.invoke("""
Make the turtle:
1. Rotate 90 degrees counterclockwise
2. Stop
3. Report the new heading
""")
print(response)
```

**Key Concept**: Angular velocity (radians/second) × time = rotation angle

### Exercise 3.3: Combined Motion

```python
# Complex movement
print("\n=== Combined Motion ===")
response = rosa.invoke("""
Make the turtle:
1. Move in a circle (forward + rotate)
2. After 3 seconds, stop
3. Report position and orientation
""")
print(response)
```

**Understanding**: Combining linear and angular velocity creates circular motion

## Verification Exercises

### Self-Check: Understanding Check

After completing the tutorial, verify your understanding:

**Exercise A**: Node Relationships
```python
response = rosa.invoke("""
Draw a diagram (in text) showing:
- All nodes
- Topics between them
- Direction of data flow
- Who controls whom
""")
```

**Exercise B**: Topic Analysis
```python
response = rosa.invoke("""
For each topic in the system:
- What data type?
- Who publishes?
- Who subscribes?
- What's the purpose?
Present as a table.
""")
```

**Exercise C**: Command Verification
```python
# Before: Get current position
before = rosa.invoke("What is the turtle's exact position?")
print("Before:", before)

# Move
rosa.invoke("Move the turtle forward 2 units")

# After: Verify position
after = rosa.invoke("What is the turtle's exact position now?")
print("After:", after)

# Compare
rosa.invoke(f"""
Compare these positions:
Before: {before}
After: {after}
Did the turtle move as expected?
""")
```

## Common Patterns Summary

### Inspection Patterns
```python
# Quick check
rosa.invoke("System status")

# Detailed check
rosa.invoke("List all nodes and their purposes")

# Filtered check
rosa.invoke("Show only topics with 'cmd' in name")
```

### Control Patterns
```python
# Direct command
rosa.invoke("Move forward")

# Specific parameters
rosa.invoke("Move forward at 2.0 speed for 2 seconds")

# Conditional command
rosa.invoke("If the path is clear, move forward")
```

## Troubleshooting This Tutorial

### "No nodes found"
**Solution**: Make sure your ROS system is running:
```bash
roscore &
rosrun turtlesim turtlesim_node &
```

### "Topic not found"
**Solution**: The node publishing to that topic might not be running. Check:
```bash
rostopic list
```

### "Command didn't work"
**Solution**: Enable verbose mode to see what ROSA tried:
```python
rosa = ROSA(ros_version=1, llm=llm, verbose=True)
```

## What's Next?

Continue your learning:

1. **Custom Tool Development Tutorial** - Build your own tools
2. **Code Examples** - See practical use cases
3. **Experienced ROS Developer Guide** - Advanced features

## Summary

In this tutorial, you:
- ✅ Inspected ROS system state comprehensively
- ✅ Monitored real-time topic data
- ✅ Executed basic robot control commands
- ✅ Understood ROSA's reasoning process

**Key Takeaways**:
- ROSA can inspect all aspects of a ROS system
- Natural language queries translate to precise ROS operations
- You can monitor data and control robots through conversation
- Verbose mode helps understand the internal process
