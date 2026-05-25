# ROS Tools Reference

Comprehensive reference for all built-in ROS tools available in ROSA.

## ROS1 Tools

### Topic Management

#### `rostopic_list`

List available ROS topics with optional filtering.

```python
rostopic_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

**Parameters**:
- `pattern`: Python regex to filter topics (e.g., `.*cmd.*`)
- `namespace`: ROS namespace to scope results
- `blacklist`: Topics to exclude

**Returns**: Dictionary with topic list and metadata

**Example**:
```
rosa.invoke("List all topics containing 'cmd'")
```

#### `rostopic_info`

Get detailed information about specific topics.

```python
rostopic_info(topics: List[str])
```

**Parameters**:
- `topics`: List of topic names

**Returns**: Topic details including type, publishers, subscribers

#### `rostopic_echo`

Echo messages from a topic.

```python
rostopic_echo(
    topic: str,
    count: int,
    return_echoes: bool = False,
    delay: float = 1.0,
    timeout: float = 1.0,
)
```

**Parameters**:
- `topic`: Topic name
- `count`: Number of messages to echo (1-100)
- `return_echoes`: Return messages in response
- `delay`: Time between messages (seconds)
- `timeout`: Max wait time for messages

### Node Management

#### `rosnode_list`

List running ROS nodes.

```python
rosnode_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

#### `rosnode_info`

Get information about specific nodes.

```python
rosnode_info(nodes: List[str])
```

### Service Management

#### `rosservice_list`

List available ROS services.

```python
rosservice_list(
    node: Optional[str] = None,
    namespace: Optional[str] = None,
    include_nodes: bool = False,
    regex_pattern: Optional[str] = None,
    exclude_logging: bool = True,
    exclude_rosapi: bool = True,
    exclude_parameters: bool = True,
    exclude_pattern: Optional[str] = None,
    blacklist: List[str] = None,
)
```

#### `rosservice_call`

Call a ROS service.

```python
rosservice_call(
    service: str,
    args: Optional[List[any]] = None,
)
```

### Parameter Management

#### `rosparam_list`

List ROS parameters.

```python
rosparam_list(
    namespace: str = "/",
    blacklist: List[str] = None,
)
```

#### `rosparam_get`

Get parameter values.

```python
rosparam_get(params: List[str])
```

#### `rosparam_set`

Set parameter values.

```python
rosparam_set(
    param: str,
    value: str,
    is_rosa_param: bool,
)
```

### Graph Tools

#### `rosgraph_get`

Get ROS graph structure.

```python
rosgraph_get(
    node_pattern: Optional[str] = ".*",
    topic_pattern: Optional[str] = ".*",
    blacklist: List[str] = None,
    exclude_self_connections: bool = True,
)
```

### Package Tools

#### `rospkg_list`

List ROS packages.

```python
rospkg_list(
    package_pattern: str = ".*",
    ignore_msgs: bool = True,
    blacklist: Optional[List[str]] = None,
)
```

#### `rospkg_info`

Get package information.

```python
rospkg_info(packages: List[str])
```

### Message Tools

#### `rosmsg_info`

Get message type information.

```python
rosmsg_info(msg_type: List[str])
```

#### `rossrv_info`

Get service type information.

```python
rossrv_info(
    srv_type: List[str],
    raw: bool = False,
)
```

### Logging Tools

#### `roslog_list`

List ROS log files.

```python
roslog_list(
    min_size: int = 2048,
    blacklist: Optional[List[str]] = None,
)
```

### Bag File Tools

#### `rosbag_record`

Record ROS bag file from specified topics.

```python
rosbag_record(
    topics: List[str],
    output: Optional[str] = None,
    duration: Optional[float] = None,
    max_size: Optional[float] = None,
)
```

#### `rosbag_info`

Get information about a ROS bag file.

```python
rosbag_info(bag_file: str)
```

#### `rosbag_play`

Play a ROS bag file.

```python
rosbag_play(
    bag_file: str,
    start: Optional[float] = None,
    duration: Optional[float] = None,
    rate: Optional[float] = None,
    loop: bool = False,
)
```

### Action Tools

#### `actionclient_list`

List available ROS action servers.

```python
actionclient_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

### Launch Tools

#### `roslaunch_find`

Find launch files in a ROS package.

```python
roslaunch_find(
    package: str,
    launch_file: Optional[str] = None,
)
```

## ROS2 Tools

### Topic Management

#### `ros2_topic_list`

List ROS2 topics.

```python
ros2_topic_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

#### `ros2_topic_echo`

Echo ROS2 topic messages.

```python
ros2_topic_echo(
    topic: str,
    count: int,
    return_echoes: bool = False,
    delay: float = 1.0,
    timeout: float = 1.0,
)
```

### Node Management

#### `ros2_node_list`

List ROS2 nodes.

```python
ros2_node_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

#### `ros2_node_info`

Get ROS2 node information.

```python
ros2_node_info(nodes: List[str])
```

### Service Management

#### `ros2_service_list`

List ROS2 services.

```python
ros2_service_list(
    node: Optional[str] = None,
    namespace: Optional[str] = None,
    regex_pattern: Optional[str] = None,
    blacklist: List[str] = None,
)
```

#### `ros2_service_call`

Call ROS2 services.

```python
ros2_service_call(
    service: str,
    args: Optional[List[any]] = None,
)
```

### Parameter Management

#### `ros2_param_list`

List ROS2 parameters.

```python
ros2_param_list(
    node_name: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

#### `ros2_param_get`

Get ROS2 parameter values.

```python
ros2_param_get(
    node_name: str,
    params: List[str],
)
```

#### `ros2_param_set`

Set ROS2 parameter values.

```python
ros2_param_set(
    node_name: str,
    param: str,
    value: str,
)
```

### Diagnostic Tools

#### `ros2_doctor`

Run ROS2 system diagnostics.

```python
ros2_doctor()
```

#### `ros2_log_directories`

Get ROS2 log directory paths.

```python
ros2_log_directories()
```

### Bag File Tools

#### `ros2_bag_record`

Record ROS2 bag file from specified topics.

```python
ros2_bag_record(
    topics: List[str],
    output: Optional[str] = None,
    duration: Optional[float] = None,
    max_size: Optional[float] = None,
)
```

#### `ros2_bag_info`

Get information about a ROS2 bag file.

```python
ros2_bag_info(bag_file: str)
```

#### `ros2_bag_play`

Play a ROS2 bag file.

```python
ros2_bag_play(
    bag_file: str,
    start: Optional[float] = None,
    duration: Optional[float] = None,
    rate: Optional[float] = None,
    loop: bool = False,
)
```

### Launch Tools

#### `ros2_launch_list`

List launch files in a ROS2 package.

```python
ros2_launch_list(package: str)
```

### Action Tools

#### `ros2_action_list`

List available ROS2 action servers.

```python
ros2_action_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
)
```

### Node Tools

#### `ros2_node_topics`

Get all topics and services for a specific ROS2 node.

```python
ros2_node_topics(node_name: str)
```

## Utility Tools

### Calculation Tools

#### `add_all`
Sum a list of numbers.

```python
add_all(numbers: List[float]) -> float
```

#### `multiply_all`
Multiply a list of numbers.

```python
multiply_all(numbers: List[float]) -> float
```

#### `mean`
Calculate mean and standard deviation.

```python
mean(numbers: List[float]) -> dict
```

Returns: `{"mean": float, "stdev": float}`

#### `median`
Calculate median.

```python
median(numbers: List[float]) -> float
```

#### `mode`
Calculate mode.

```python
mode(numbers: List[float]) -> float
```

#### `variance`
Calculate variance.

```python
variance(numbers: List[float]) -> float
```

### Math Tools

- `add`, `subtract`, `multiply`, `divide`
- `exponentiate`, `modulo`
- `sine`, `cosine`, `tangent`

### Log Tools

#### `read_log`
Read ROS log files.

```python
read_log(
    file_path: Optional[str] = None,
    lines: int = 100,
)
```

### System Tools

#### `set_verbosity`
Set global verbosity level.

```python
set_verbosity(verbose: bool)
```

#### `set_debugging`
Enable/disable debugging mode.

```python
set_debugging(debug: bool)
```

#### `wait`
Pause execution.

```python
wait(seconds: float)
```

#### `get_system_health`
Get overall system health status including ROS and agent status.

```python
get_system_health() -> dict
```

Returns comprehensive health report with ROS master connectivity, active components, and environment status.

#### `monitor_topic`
Monitor a ROS topic for a specified duration and report statistics.

```python
monitor_topic(
    topic_name: str,
    duration: float = 5.0,
) -> dict
```

Returns monitoring statistics including message frequency and type.

#### `check_disk_space`
Check available disk space on the system.

```python
check_disk_space() -> dict
```

Returns disk usage information for root, home, and ROS log partitions.

#### `get_environment_summary`
Get a summary of the current ROS environment setup.

```python
get_environment_summary() -> dict
```

Returns ROS environment variables, installation status, and platform information.

## Next Steps

- [Basic ROS Operations Tutorial](../tutorials/basic-ros-operations.md) - Learn to use these tools hands-on
- [API Reference](api-reference.md) - Python API documentation
- [Custom Tool Development Tutorial](../tutorials/custom-tool-development.md) - Build custom tools
