# Pick and Place Example

Simple pick and place operation using ROSA.

## Scenario

Pick up an object from one location and place it at another.

## Code

```python
from rosa import ROSA
from langchain.agents import tool
from langchain_openai import ChatOpenAI

# Custom manipulation tools
@tool
def move_to_location(x: float, y: float, z: float) -> str:
    """Move arm to location.
    
    Args:
        x, y, z: Target coordinates
    """
    return f"Arm moved to ({x}, {y}, {z})"

@tool
def grasp_object(object_id: str) -> str:
    """Grasp an object.
    
    Args:
        object_id: Object identifier
    """
    return f"Grasped object {object_id}"

@tool
def release_object() -> str:
    """Release currently held object."""
    return "Object released"

# Initialize ROSA
llm = ChatOpenAI(model="gpt-4")

rosa = ROSA(
    ros_version=1,
    llm=llm,
    tools=[move_to_location, grasp_object, release_object]
)

# Execute pick and place
response = rosa.invoke("""
Pick and place operation:
1. Move to object "box_1" at (1, 2, 0)
2. Grasp object "box_1"
3. Move to destination (3, 4, 0)
4. Release the object
5. Report the operation status
""")

print(response)
```

## Usage

```bash
python3 pick-and-place.py
```

## Expected Output

```
Pick and Place Operation:
1. Moving to (1, 2, 0) - Reached position ✓
2. Grasping box_1 - Object secured ✓
3. Moving to (3, 4, 0) - Destination reached ✓
4. Releasing object - Released ✓
5. Operation completed successfully ✓
```
