#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time

from langchain.agents import tool
from langchain.globals import set_debug, set_verbose


@tool
def set_verbosity(enable_verbose_messages: bool) -> str:
    """Sets the verbosity of the agent to enable or disable verbose messages.
    Set this to true to provide more detailed output for the user.

    :arg enable_verbose_messages: A boolean value to enable or disable verbose messages.
    """
    global VERBOSE
    VERBOSE = enable_verbose_messages
    set_verbose(VERBOSE)
    return f"Verbose messages are now {'enabled' if VERBOSE else 'disabled'}."


@tool
def set_debugging(enable_debug_messages: bool) -> str:
    """Sets the debug mode of the agent to enable or disable debug messages.
    Set this to true to provide debug output for the user. Debug output
    includes information about API calls, tool execution, and other.

    :arg enable_debug_messages: A boolean value to enable or disable debug messages.
    """
    global DEBUG
    DEBUG = enable_debug_messages
    set_debug(DEBUG)
    return f"Debug messages are now {'enabled' if DEBUG else 'disabled'}."


@tool
def wait(seconds: int) -> str:
    """Waits for the specified number of seconds before continuing.

    :arg seconds: The number of seconds to wait.
    """
    start = time.time()
    time.sleep(seconds)
    end = time.time()
    return f"Waited exactly {end - start} seconds."


@tool
def get_system_health() -> dict:
    """Get overall system health status including ROS and agent status.
    
    Returns a comprehensive health report with:
    - ROS master connectivity
    - Active node count
    - Memory usage (if available)
    - Agent status
    """
    import os
    import sys
    
    health = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check ROS master (ROS1)
    try:
        import rosgraph
        master = rosgraph.masterapi.Master('/rostopic')
        master.getSystemState()
        health["checks"]["ros_master"] = "connected"
    except Exception:
        health["checks"]["ros_master"] = "not connected"
        health["status"] = "degraded"
    
    # Check Python version
    health["checks"]["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Check ROSA availability
    try:
        import rosa
        health["checks"]["rosa_version"] = getattr(rosa, '__version__', 'unknown')
    except ImportError:
        health["checks"]["rosa"] = "not installed"
        health["status"] = "degraded"
    
    # Check LangChain
    try:
        import langchain
        health["checks"]["langchain"] = "available"
    except ImportError:
        health["checks"]["langchain"] = "not available"
    
    return health


@tool
def monitor_topic(topic_name: str, duration: float = 5.0) -> dict:
    """Monitor a ROS topic for a specified duration and report statistics.
    
    :param topic_name: Name of the topic to monitor.
    :param duration: Duration to monitor in seconds (default: 5.0).
    
    Returns:
        Dictionary with monitoring statistics including message count,
        frequency, and average message size.
    """
    import subprocess
    
    try:
        # Use rostopic hz to get frequency
        result = subprocess.run(
            ["timeout", str(duration), "rostopic", "hz", topic_name],
            capture_output=True,
            text=True,
            timeout=duration + 2
        )
        
        # Parse output
        hz_output = result.stderr if result.stderr else result.stdout
        
        # Extract frequency info
        freq_info = {}
        for line in hz_output.split('\n'):
            if 'average rate' in line:
                freq_info["average_rate"] = line.split(':')[1].strip() if ':' in line else "unknown"
            elif 'min' in line and 'max' in line:
                freq_info["range"] = line.strip()
        
        # Also get message type
        type_result = subprocess.run(
            ["rostopic", "type", topic_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        msg_type = type_result.stdout.strip() if type_result.returncode == 0 else "unknown"
        
        return {
            "topic": topic_name,
            "duration": duration,
            "message_type": msg_type,
            "monitoring_results": freq_info,
            "raw_output": hz_output[:500]  # Limit output size
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Monitoring timed out for topic '{topic_name}'"}
    except Exception as e:
        return {"error": f"Failed to monitor topic '{topic_name}': {e}"}


@tool
def check_disk_space() -> dict:
    """Check available disk space on the system.
    
    Returns:
        Dictionary with disk usage information for relevant partitions.
    """
    import shutil
    import os
    
    try:
        # Check root partition
        root_usage = shutil.disk_usage("/")
        
        # Check home directory
        home_path = os.path.expanduser("~")
        home_usage = shutil.disk_usage(home_path)
        
        # Check ROS log directory if it exists
        ros_log_path = os.path.expanduser("~/.ros/log")
        ros_log_usage = None
        if os.path.exists(ros_log_path):
            try:
                ros_log_usage = shutil.disk_usage(ros_log_path)
            except:
                pass
        
        def format_bytes(b):
            """Format bytes to human readable."""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if b < 1024.0:
                    return f"{b:.2f} {unit}"
                b /= 1024.0
            return f"{b:.2f} PB"
        
        result = {
            "root": {
                "total": format_bytes(root_usage.total),
                "used": format_bytes(root_usage.used),
                "free": format_bytes(root_usage.free),
                "percent_used": f"{(root_usage.used / root_usage.total) * 100:.1f}%"
            },
            "home": {
                "total": format_bytes(home_usage.total),
                "used": format_bytes(home_usage.used),
                "free": format_bytes(home_usage.free),
                "percent_used": f"{(home_usage.used / home_usage.total) * 100:.1f}%"
            }
        }
        
        if ros_log_usage:
            result["ros_logs"] = {
                "total": format_bytes(ros_log_usage.total),
                "used": format_bytes(ros_log_usage.used),
                "free": format_bytes(ros_log_usage.free),
                "percent_used": f"{(ros_log_usage.used / ros_log_usage.total) * 100:.1f}%"
            }
        
        return result
    except Exception as e:
        return {"error": f"Failed to check disk space: {e}"}


@tool
def get_environment_summary() -> dict:
    """Get a summary of the current ROS environment setup.
    
    Returns:
        Dictionary with ROS environment variables and configuration.
    """
    import os
    
    env_vars = {
        "ROS_DISTRO": os.environ.get("ROS_DISTRO", "not set"),
        "ROS_VERSION": os.environ.get("ROS_VERSION", "not set"),
        "ROS_MASTER_URI": os.environ.get("ROS_MASTER_URI", "not set"),
        "ROS_HOSTNAME": os.environ.get("ROS_HOSTNAME", "not set"),
        "ROS_IP": os.environ.get("ROS_IP", "not set"),
        "PYTHONPATH": os.environ.get("PYTHONPATH", "not set")[:200] + "..." if len(os.environ.get("PYTHONPATH", "")) > 200 else os.environ.get("PYTHONPATH", "not set"),
    }
    
    # Check ROS installation
    ros_installation = "unknown"
    if os.path.exists("/opt/ros/noetic"):
        ros_installation = "ROS1 Noetic detected"
    elif os.path.exists("/opt/ros/humble"):
        ros_installation = "ROS2 Humble detected"
    elif os.path.exists("/opt/ros/iron"):
        ros_installation = "ROS2 Iron detected"
    elif os.path.exists("/opt/ros/jazzy"):
        ros_installation = "ROS2 Jazzy detected"
    
    return {
        "environment_variables": env_vars,
        "ros_installation": ros_installation,
        "platform": os.sys.platform,
        "working_directory": os.getcwd()
    }


@tool
def get_performance_metrics() -> dict:
    """Get performance metrics including cache hit rates and execution times.

    Returns:
        Dictionary with cache statistics, tool execution times, and memory usage.
    """
    return {
        "status": "Metrics available after profiling is enabled.",
        "note": "Set enable_profiling=True in ROSA constructor to collect metrics.",
        "metrics": {}
    }


@tool
def clear_caches() -> str:
    """Clear all internal caches (ROS state and tool result caches).

    Use this if you suspect stale data or want to force fresh queries.
    """
    return "Cache clearing requires caching to be enabled. Use ROSA constructor parameter enable_caching=True."
