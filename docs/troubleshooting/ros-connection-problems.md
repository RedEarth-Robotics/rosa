# ROS Connection Problems

Fixing issues with ROS connectivity and communication.

## Quick Diagnostics

Check ROS status:

```bash
# Check if ROS master is running
rostopic list

# Check ROS environment
echo $ROS_MASTER_URI
echo $ROS_HOSTNAME

# Check nodes
rosnode list
```

## Common Problems

### Problem: Can't connect to ROS master

**Symptoms**:
```
ERROR: Unable to communicate with master!
```

**Solutions**:

1. **Start ROS master**:
```bash
roscore &
```

2. **Check ROS_MASTER_URI**:
```bash
echo $ROS_MASTER_URI  # Should be http://localhost:11311
```

3. **Set correct URI**:
```bash
export ROS_MASTER_URI=http://localhost:11311
```

### Problem: Empty topic/node lists

**Symptoms**:
ROSA returns empty lists when querying topics/nodes.

**Solutions**:

1. **Verify ROS is running**:
```bash
rostopic list
```

2. **Check if nodes are running**:
```bash
rosnode list
```

3. **Start demo nodes**:
```bash
rosrun turtlesim turtlesim_node &
rosrun turtlesim turtle_teleop_key &
```

### Problem: Permission denied on ROS topics

**Symptoms**:
```
PermissionError when trying to publish/subscribe
```

**Solutions**:

1. **Fix ROS log permissions**:
```bash
sudo chown -R $USER:$USER ~/.ros
```

2. **Check file permissions**:
```bash
ls -la ~/.ros/
```

### Problem: Network issues with remote ROS

**Symptoms**:
Can't connect to remote ROS master.

**Solutions**:

1. **Check connectivity**:
```bash
ping <master-ip>
```

2. **Configure ROS master**:
```bash
export ROS_MASTER_URI=http://<master-ip>:11311
export ROS_IP=<your-ip>
```

3. **Check firewall**:
```bash
sudo ufw status
sudo ufw allow 11311
```

### Problem: Multiple ROS masters

**Symptoms**:
Confusion about which ROS master is being used.

**Solutions**:

1. **Check current master**:
```bash
echo $ROS_MASTER_URI
```

2. **Kill existing master**:
```bash
killall rosmaster
roscore &
```

3. **Use unique ports**:
```bash
export ROS_MASTER_URI=http://localhost:11312
roscore -p 11312 &
```

## ROS2 Specific Issues

### Problem: ros2 command not found

**Solution**:
```bash
source /opt/ros/humble/setup.bash
```

### Problem: DDS configuration issues

**Solution**:
```bash
# Check DDS settings
echo $RMW_IMPLEMENTATION

# Set DDS implementation
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

## Environment Variables

Required ROS environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `ROS_MASTER_URI` | ROS master location | `http://localhost:11311` |
| `ROS_IP` | Your IP address | `192.168.1.100` |
| `ROS_HOSTNAME` | Your hostname | `myrobot` |
| `ROS_PACKAGE_PATH` | Package search path | `/opt/ros/noetic/share` |
| `PYTHONPATH` | Python module path | `...python3/dist-packages` |

## Verification Commands

```bash
# Test ROS connectivity
rostopic list
rosnode list
rosservice list
rosparam list

# Test with a simple publisher/subscriber
rostopic pub /test std_msgs/String "data: 'hello'"
rostopic echo /test
```

## Next Steps

- [Installation Issues](installation-issues.md)
- [Tool Execution Failures](tool-execution-failures.md)
- [Troubleshooting Guide](../user-guides/troubleshooting.md)
