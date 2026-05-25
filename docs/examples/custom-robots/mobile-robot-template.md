# Mobile Robot Template

Template for creating a custom ROSA agent for a mobile robot.

## Robot Specifications

- **Type**: Differential drive mobile robot
- **Sensors**: Lidar, camera, IMU
- **Actuators**: 2 DC motors with encoders
- **Compute**: Raspberry Pi 4 with Ubuntu 20.04
- **ROS**: Noetic

## Template Code

```python
#!/usr/bin/env python3
"""Mobile Robot ROSA Agent Template.

This template provides a complete starting point for creating
a ROSA agent for a custom mobile robot.
"""

from rosa import ROSA
from rosa.prompts import RobotSystemPrompts
from langchain.agents import tool
from langchain_openai import ChatOpenAI
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


class MobileRobotAgent(ROSA):
    """Custom agent for a differential drive mobile robot.
    
    Features:
    - Differential drive control
    - Lidar-based obstacle detection
    - Odometry-based position tracking
    - Emergency stop functionality
    """
    
    def __init__(self, streaming: bool = False):
        # Robot-specific prompts
        prompts = RobotSystemPrompts(
            embodiment_and_persona=(
                "You are a differential drive mobile robot with "
                "Lidar, camera, and IMU sensors. You operate in "
                "indoor and outdoor environments."
            ),
            about_your_capabilities=(
                "- Differential drive movement\n"
                "- Obstacle avoidance using Lidar\n"
                "- Position tracking via odometry\n"
                "- Autonomous navigation\n"
                "- Emergency stop"
            ),
            critical_instructions=(
                "1. Check for obstacles before moving\n"
                "2. Never exceed maximum speed\n"
                "3. Maintain safe distance from obstacles\n"
                "4. Report position after each movement"
            ),
            constraints_and_guardrails=(
                "- Max linear speed: 0.5 m/s\n"
                "- Max angular speed: 1.0 rad/s\n"
                "- Minimum obstacle distance: 0.5m\n"
                "- Operating time: Battery dependent"
            ),
            about_your_environment=(
                "Indoor/outdoor environments with flat terrain. "
                "May contain static and dynamic obstacles."
            ),
            mission_and_objectives=(
                "Navigate safely to target locations while "
                "avoiding obstacles and maintaining position accuracy."
            )
        )
        
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Initialize ROSA
        super().__init__(
            ros_version=1,
            llm=llm,
            tools=self._create_robot_tools(),
            prompts=prompts,
            blacklist=["emergency_stop"],
            streaming=streaming,
            verbose=True
        )
        
        # Robot state
        self.current_speed = 0.0
        self.current_angular = 0.0
    
    def _create_robot_tools(self):
        """Create robot-specific tools."""
        
        @tool
        def move_forward(speed: float, duration: float) -> str:
            """Move robot forward.
            
            Args:
                speed: Linear speed in m/s (0.0 to 0.5)
                duration: Movement duration in seconds
            """
            if speed > 0.5:
                return "Error: Speed exceeds maximum 0.5 m/s"
            
            # Publish velocity command
            pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
            twist = Twist()
            twist.linear.x = speed
            pub.publish(twist)
            rospy.sleep(duration)
            
            # Stop
            twist.linear.x = 0
            pub.publish(twist)
            
            return f"Moved forward at {speed} m/s for {duration} seconds"
        
        @tool
        def rotate(angular_speed: float, duration: float) -> str:
            """Rotate robot in place.
            
            Args:
                angular_speed: Angular speed in rad/s (-1.0 to 1.0)
                duration: Rotation duration in seconds
            """
            if abs(angular_speed) > 1.0:
                return "Error: Angular speed exceeds maximum 1.0 rad/s"
            
            pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
            twist = Twist()
            twist.angular.z = angular_speed
            pub.publish(twist)
            rospy.sleep(duration)
            
            # Stop
            twist.angular.z = 0
            pub.publish(twist)
            
            return f"Rotated at {angular_speed} rad/s for {duration} seconds"
        
        @tool
        def get_position() -> dict:
            """Get current robot position from odometry."""
            try:
                odom = rospy.wait_for_message('/odom', Odometry, timeout=5.0)
                return {
                    "x": odom.pose.pose.position.x,
                    "y": odom.pose.pose.position.y,
                    "theta": odom.pose.pose.orientation.z,
                    "status": "success"
                }
            except Exception as e:
                return {"error": str(e), "status": "failed"}
        
        @tool
        def scan_environment() -> dict:
            """Scan environment using Lidar."""
            try:
                scan = rospy.wait_for_message('/scan', LaserScan, timeout=5.0)
                return {
                    "ranges": len(scan.ranges),
                    "min_range": min(scan.ranges),
                    "max_range": max(scan.ranges),
                    "status": "success"
                }
            except Exception as e:
                return {"error": str(e), "status": "failed"}
        
        @tool
        def check_obstacles() -> str:
            """Check for obstacles in front of robot."""
            try:
                scan = rospy.wait_for_message('/scan', LaserScan, timeout=5.0)
                # Check front sector (assumes 0 degrees is front)
                front_distances = scan.ranges[:30] + scan.ranges[-30:]
                min_distance = min(front_distances)
                
                if min_distance < 0.5:
                    return f"WARNING: Obstacle detected at {min_distance:.2f}m"
                return f"Path clear. Closest obstacle: {min_distance:.2f}m"
            except Exception as e:
                return f"Error checking obstacles: {e}"
        
        return [move_forward, rotate, get_position, scan_environment, check_obstacles]
    
    def get_robot_status(self) -> dict:
        """Get comprehensive robot status."""
        return {
            "agent": "MobileRobot",
            "speed": self.current_speed,
            "angular": self.current_angular,
            "status": "operational"
        }


# Usage example
if __name__ == "__main__":
    # Initialize ROS
    rospy.init_node('mobile_robot_agent')
    
    # Create agent
    agent = MobileRobotAgent()
    
    print("Mobile Robot Agent initialized!")
    print("Try these commands:")
    print("- 'Move forward 1 meter at 0.3 speed'")
    print("- 'Rotate 90 degrees'")
    print("- 'What is my current position?'")
    print("- 'Scan environment for obstacles'")
    
    # Interactive session
    while True:
        try:
            query = input("\n> ")
            if query.lower() in ['exit', 'quit']:
                break
            response = agent.invoke(query)
            print(response)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Shutting down...")
```

## Usage

```bash
# Make executable
chmod +x mobile-robot-template.py

# Run
python3 mobile-robot-template.py
```

## Customization Guide

### Modifying for Your Robot

1. **Update Robot Specifications**
   - Change `RobotSystemPrompts` for your robot
   - Update speed limits and constraints
   - Add your robot's specific capabilities

2. **Add Custom Tools**
   - Create new `@tool` functions
   - Integrate with your robot's ROS topics
   - Add safety checks

3. **Customize Behavior**
   - Override `invoke()` for custom processing
   - Add logging and monitoring
   - Implement error recovery

4. **Test Thoroughly**
   - Test each tool independently
   - Verify safety constraints
   - Test edge cases

## Next Steps

- [Custom Tool Development Tutorial](../../tutorials/custom-tool-development.md)
- [Advanced Agent Customization Tutorial](../../tutorials/advanced-agent-customization.md)
- [API Reference](../../core/api-reference.md)
