# Sensor Fusion Example

Combine data from multiple sensors using ROSA.

## Scenario

Read data from camera and Lidar sensors and fuse them for environment understanding.

## Code

```python
from rosa import ROSA
from langchain.agents import tool
from langchain_openai import ChatOpenAI
import random

# Simulated sensor tools
@tool
def read_camera() -> dict:
    """Read camera data."""
    objects = ["person", "chair", "table", "box"]
    return {
        "sensor": "camera",
        "objects_detected": random.sample(objects, 2),
        "timestamp": "2024-01-15T10:30:00Z"
    }

@tool
def read_lidar() -> dict:
    """Read Lidar point cloud data."""
    return {
        "sensor": "lidar",
        "points": 15000,
        "range": 30.0,
        "obstacles": ["wall", "obstacle_1"],
        "timestamp": "2024-01-15T10:30:00Z"
    }

# Initialize ROSA
llm = ChatOpenAI(model="gpt-4")
rosa = ROSA(ros_version=1, llm=llm, tools=[read_camera, read_lidar])

# Sensor fusion query
response = rosa.invoke("""
Read all sensors and provide a fused understanding:
1. What does the camera see?
2. What does the lidar detect?
3. Combine both readings
4. Identify any discrepancies
5. Provide a complete scene description
""")

print(response)
```

## Usage

```bash
python3 sensor-fusion.py
```
