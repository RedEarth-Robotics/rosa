# TurtleSim Control Example

Control TurtleSim using natural language through ROSA.

## Scenario

Draw shapes and navigate TurtleSim using conversational commands.

## Code

```python
from rosa import ROSA
from langchain_openai import ChatOpenAI

# Initialize ROSA
llm = ChatOpenAI(model="gpt-4")
rosa = ROSA(ros_version=1, llm=llm)

# Draw a square
print("=== Drawing a Square ===")
response = rosa.invoke("""
Draw a square with the turtle:
1. Start at current position
2. Move forward 2 units
3. Turn 90 degrees right
4. Move forward 2 units
5. Turn 90 degrees right
6. Move forward 2 units
7. Turn 90 degrees right
8. Move forward 2 units
9. Report the final position
""")
print(response)

# Navigate to specific point
print("\n=== Navigate to Point ===")
response = rosa.invoke("Move the turtle to coordinates (5, 5)")
print(response)

# Get system status
print("\n=== System Status ===")
response = rosa.invoke("Show me the turtle's current state and position")
print(response)
```

## Usage

```bash
# Start TurtleSim
rosrun turtlesim turtlesim_node &

# Run the example
python3 turtlesim-control.py
```

## Expected Output

```
=== Drawing a Square ===
Drawing square...
1. Moving forward 2 units ✓
2. Turning 90° right ✓
3. Moving forward 2 units ✓
4. Turning 90° right ✓
5. Moving forward 2 units ✓
6. Turning 90° right ✓
7. Moving forward 2 units ✓
Square drawn! Final position: (2, 2)

=== Navigate to Point ===
Moving to (5, 5)...
Reached target position.

=== System Status ===
Position: (5, 5)
Orientation: 0.0 radians
Linear velocity: 0.0
Angular velocity: 0.0
```
