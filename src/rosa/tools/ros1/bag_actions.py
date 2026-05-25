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

import os
import time
import subprocess
import datetime
from typing import Optional, List

import rosgraph
import rospkg
from langchain.agents import tool


@tool
def rosbag_record(
    topics: List[str],
    output: Optional[str] = None,
    duration: Optional[float] = None,
    max_size: Optional[float] = None,
) -> str:
    """Record ROS bag file from specified topics.

    :param topics: List of topic names to record.
    :param output: Output bag file path (default: auto-generated with timestamp).
    :param duration: Maximum recording duration in seconds (optional).
    :param max_size: Maximum bag file size in MB (optional).
    """
    import subprocess
    import datetime

    if not topics or len(topics) == 0:
        return "Error: Please provide at least one topic to record."

    try:
        # Generate output filename if not provided
        if not output:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            output = f"rosbag_{timestamp}.bag"

        # Build rosbag record command
        cmd = ["rosbag", "record", "-O", output]
        
        if duration:
            cmd.extend(["--duration", str(duration)])
        if max_size:
            cmd.extend(["--size", str(max_size)])
        
        cmd.extend(topics)

        return (
            f"To record a bag file, run this command in a new terminal:\n"
            f"{' '.join(cmd)}\n\n"
            f"This will record topics: {', '.join(topics)}\n"
            f"Output file: {output}\n"
            f"Press Ctrl+C to stop recording."
        )
    except Exception as e:
        return f"Error preparing rosbag record: {e}"


@tool
def rosbag_info(bag_file: str) -> dict:
    """Get information about a ROS bag file.

    :param bag_file: Path to the bag file.
    """
    import subprocess
    import json

    if not bag_file or not os.path.exists(bag_file):
        return {"error": f"Bag file not found: {bag_file}"}

    try:
        result = subprocess.run(
            ["rosbag", "info", "--yaml", bag_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"error": f"rosbag info failed: {result.stderr}"}

        # Parse basic info from yaml output
        output_lines = result.stdout.split('\n')
        info = {
            "file": bag_file,
            "raw_info": result.stdout[:1000]  # Limit output size
        }
        
        for line in output_lines:
            if 'path:' in line:
                info["path"] = line.split(':', 1)[1].strip()
            elif 'duration:' in line:
                info["duration"] = line.split(':', 1)[1].strip()
            elif 'size:' in line:
                info["size"] = line.split(':', 1)[1].strip()
            elif 'messages:' in line:
                info["messages"] = line.split(':', 1)[1].strip()

        return info
    except subprocess.TimeoutExpired:
        return {"error": "rosbag info timed out (30s limit)"}
    except Exception as e:
        return {"error": f"Failed to get bag info: {e}"}


@tool
def rosbag_play(
    bag_file: str,
    start: Optional[float] = None,
    duration: Optional[float] = None,
    rate: Optional[float] = None,
    loop: bool = False,
) -> str:
    """Play a ROS bag file.

    :param bag_file: Path to the bag file to play.
    :param start: Start time in seconds from beginning (optional).
    :param duration: Duration to play in seconds (optional).
    :param rate: Playback rate multiplier (optional, default: 1.0).
    :param loop: Whether to loop playback (default: False).
    """
    import subprocess

    if not bag_file or not os.path.exists(bag_file):
        return f"Error: Bag file not found: {bag_file}"

    try:
        # Build rosbag play command
        cmd = ["rosbag", "play"]
        
        if start is not None:
            cmd.extend(["-s", str(start)])
        if duration is not None:
            cmd.extend(["-u", str(duration)])
        if rate is not None:
            cmd.extend(["-r", str(rate)])
        if loop:
            cmd.append("-l")
        
        cmd.append(bag_file)

        return (
            f"To play the bag file, run this command in a new terminal:\n"
            f"{' '.join(cmd)}\n\n"
            f"Playing: {bag_file}\n"
            f"Press Ctrl+C to stop playback."
        )
    except Exception as e:
        return f"Error preparing rosbag play: {e}"


@tool
def actionclient_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
) -> dict:
    """Returns a list of available ROS action servers.

    :param pattern: A Python regex pattern to filter action server names.
    :param namespace: ROS namespace to scope return values by.
    :param blacklist: List of action servers to exclude.
    """
    try:
        import actionlib
        
        # Get all action servers from the ROS master
        state = rosgraph.masterapi.Master('/rostopic')
        pubs, subs, srvs = state.getSystemState()
        
        # Action servers typically publish to /action_name/status, /action_name/result, /action_name/feedback
        # and subscribe to /action_name/goal, /action_name/cancel
        action_servers = set()
        for topic, _ in pubs:
            if '/status' in topic and not topic.endswith('/status'):
                action_name = topic.rsplit('/status', 1)[0]
                action_servers.add(action_name)
        
        # Filter by pattern if provided
        if pattern:
            import re
            action_servers = {a for a in action_servers if re.search(pattern, a)}
        
        # Filter by namespace
        if namespace:
            ns = namespace if namespace.startswith('/') else f'/{namespace}'
            action_servers = {a for a in action_servers if a.startswith(ns)}
        
        # Apply blacklist
        if blacklist:
            action_servers = {a for a in action_servers if not any(b in a for b in blacklist)}
        
        return {
            "total": len(action_servers),
            "action_servers": sorted(list(action_servers))
        }
    except Exception as e:
        return {"error": f"Failed to list action servers: {e}"}


@tool
def roslaunch_find(package: str, launch_file: Optional[str] = None) -> dict:
    """Find launch files in a ROS package.

    :param package: Name of the ROS package to search.
    :param launch_file: Specific launch file to find (optional).
    """
    try:
        import rospkg
        pkg_path = rospkg.RosPack().get_path(package)
        launch_dir = os.path.join(pkg_path, 'launch')
        
        if not os.path.exists(launch_dir):
            return {"error": f"No launch directory found in package '{package}'"}
        
        launch_files = []
        for root, dirs, files in os.walk(launch_dir):
            for file in files:
                if file.endswith('.launch'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, launch_dir)
                    if launch_file is None or launch_file in file:
                        launch_files.append({
                            "file": file,
                            "path": full_path,
                            "relative": rel_path
                        })
        
        return {
            "package": package,
            "total": len(launch_files),
            "launch_files": launch_files
        }
    except rospkg.ResourceNotFound:
        return {"error": f"Package '{package}' not found"}
    except Exception as e:
        return {"error": f"Failed to find launch files: {e}"}
