# Simple Navigation Example

Basic path planning and execution using ROSA.

## Scenario

Navigate a robot from point A to point B while avoiding obstacles.

## Code

```python
from rosa import ROSA
from rosa.prompts import RobotSystemPrompts
from langchain.agents import tool
from langchain_openai import ChatOpenAI

# Custom navigation tool
@tool
def move_to(x: float, y: float) -> str:
    """Move robot to coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
    """
    return f"Moving to ({x}, {y})"

# Initialize ROSA
llm = ChatOpenAI(model="gpt-4")

prompts = RobotSystemPrompts(
    about_your_capabilities="Navigate between points in a 2D plane"
)

rosa = ROSA(
    ros_version=1,
    llm=llm,
    tools=[move_to],
    prompts=prompts
)

# Navigate to multiple points
response = rosa.invoke("""
Navigate to these points in order:
1. (0, 0) - Starting position
2. (5, 0) - Move east
3. (5, 5) - Move north
4. (0, 5) - Move west
5. (0, 0) - Return home
""")

print(response)
```

## Usage

```bash
python3 simple-navigation.py
```

## Expected Output

```
Navigation plan executed:
1. Moving to (0, 0) - Starting position ✓
2. Moving to (5, 0) - Move east ✓
3. Moving to (5, 5) - Move north ✓
4. Moving to (0, 5) - Move west ✓
5. Moving to (0, 0) - Return home ✓

Navigation complete!
```
