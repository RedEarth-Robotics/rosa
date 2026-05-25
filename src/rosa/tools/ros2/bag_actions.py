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
import re
import subprocess
from datetime import datetime
from typing import List, Optional

from langchain.agents import tool


@tool
def ros2_bag_record(
    topics: List[str],
    output: Optional[str] = None,
    duration: Optional[float] = None,
    max_size: Optional[float] = None,
) -> str:
    """Record ROS2 bag file from specified topics.

    :param topics: List of topic names to record.
    :param output: Output bag file path (default: auto-generated with timestamp).
    :param duration: Maximum recording duration in seconds (optional).
    :param max_size: Maximum bag file size in MB (optional).
    """
    import datetime

    if not topics or len(topics) == 0:
        return "Error: Please provide at least one topic to record."

    try:
        # Generate output filename if not provided
        if not output:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            output = f"ros2bag_{timestamp}"

        # Build ros2 bag record command
        cmd = ["ros2", "bag", "record", "-o", output]
        
        if duration:
            cmd.extend(["-d", str(int(duration))])
        if max_size:
            cmd.extend(["-b", str(int(max_size * 1024 * 1024))])  # Convert MB to bytes
        
        cmd.extend(topics)

        return (
            f"To record a ROS2 bag file, run this command in a new terminal:\n"
            f"{' '.join(cmd)}\n\n"
            f"This will record topics: {', '.join(topics)}\n"
            f"Output directory: {output}\n"
            f"Press Ctrl+C to stop recording."
        )
    except Exception as e:
        return f"Error preparing ros2 bag record: {e}"


@tool
def ros2_bag_info(bag_file: str) -> dict:
    """Get information about a ROS2 bag file.

    :param bag_file: Path to the bag file directory.
    """
    if not bag_file or not os.path.exists(bag_file):
        return {"error": f"Bag file not found: {bag_file}"}

    try:
        result = subprocess.run(
            ["ros2", "bag", "info", bag_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"error": f"ros2 bag info failed: {result.stderr}"}

        # Parse basic info
        output_lines = result.stdout.split('\n')
        info = {
            "file": bag_file,
            "raw_info": result.stdout[:2000]  # Limit output size
        }
        
        for line in output_lines:
            if 'Duration:' in line:
                info["duration"] = line.split(':', 1)[1].strip()
            elif 'Size:' in line:
                info["size"] = line.split(':', 1)[1].strip()
            elif 'Messages:' in line:
                info["messages"] = line.split(':', 1)[1].strip()
            elif 'Topic:' in line:
                info.setdefault("topics", []).append(line.split(':', 1)[1].strip())

        return info
    except subprocess.TimeoutExpired:
        return {"error": "ros2 bag info timed out (30s limit)"}
    except Exception as e:
        return {"error": f"Failed to get bag info: {e}"}


@tool
def ros2_bag_play(
    bag_file: str,
    start: Optional[float] = None,
    duration: Optional[float] = None,
    rate: Optional[float] = None,
    loop: bool = False,
) -> str:
    """Play a ROS2 bag file.

    :param bag_file: Path to the bag file directory to play.
    :param start: Start offset in seconds from beginning (optional).
    :param duration: Duration to play in seconds (optional).
    :param rate: Playback rate multiplier (optional, default: 1.0).
    :param loop: Whether to loop playback (default: False).
    """
    if not bag_file or not os.path.exists(bag_file):
        return f"Error: Bag file not found: {bag_file}"

    try:
        # Build ros2 bag play command
        cmd = ["ros2", "bag", "play"]
        
        if start is not None:
            cmd.extend(["--start-offset", str(start)])
        if duration is not None:
            cmd.extend(["--playback-duration", str(duration)])
        if rate is not None:
            cmd.extend(["-r", str(rate)])
        if loop:
            cmd.append("-l")
        
        cmd.append(bag_file)

        return (
            f"To play the ROS2 bag file, run this command in a new terminal:\n"
            f"{' '.join(cmd)}\n\n"
            f"Playing: {bag_file}\n"
            f"Press Ctrl+C to stop playback."
        )
    except Exception as e:
        return f"Error preparing ros2 bag play: {e}"


@tool
def ros2_launch_list(package: str) -> dict:
    """List launch files in a ROS2 package.

    :param package: Name of the ROS2 package to search.
    """
    try:
        result = subprocess.run(
            ["ros2", "pkg", "prefix", package],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"error": f"Package '{package}' not found"}
        
        pkg_path = result.stdout.strip()
        share_dir = os.path.join(pkg_path, 'share', package)
        launch_dir = os.path.join(share_dir, 'launch')
        
        if not os.path.exists(launch_dir):
            # Try finding launch files in share directory
            launch_files = []
            for root, dirs, files in os.walk(share_dir):
                for file in files:
                    if file.endswith('.launch.py') or file.endswith('.launch.xml'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, share_dir)
                        launch_files.append({
                            "file": file,
                            "path": full_path,
                            "relative": rel_path
                        })
            
            if not launch_files:
                return {"error": f"No launch files found in package '{package}'"}
            
            return {
                "package": package,
                "total": len(launch_files),
                "launch_files": launch_files
            }
        
        # Search in launch directory
        launch_files = []
        for root, dirs, files in os.walk(launch_dir):
            for file in files:
                if file.endswith('.launch.py') or file.endswith('.launch.xml'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, launch_dir)
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
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out"}
    except Exception as e:
        return {"error": f"Failed to list launch files: {e}"}


@tool
def ros2_action_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
) -> dict:
    """Returns a list of available ROS2 action servers.

    :param pattern: A Python regex pattern to filter action server names.
    :param namespace: ROS namespace to scope return values by.
    :param blacklist: List of action servers to exclude.
    """
    try:
        result = subprocess.run(
            ["ros2", "action", "list", "-t"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"error": f"Failed to list actions: {result.stderr}"}
        
        action_servers = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            # Format: /action_name [action_type]
            parts = line.split('[')
            if len(parts) == 2:
                name = parts[0].strip()
                action_type = parts[1].rstrip(']')
                action_servers.append({"name": name, "type": action_type})
        
        # Filter by pattern
        if pattern:
            import re
            action_servers = [a for a in action_servers if re.search(pattern, a["name"])]
        
        # Filter by namespace
        if namespace:
            ns = namespace if namespace.startswith('/') else f'/{namespace}'
            action_servers = [a for a in action_servers if a["name"].startswith(ns)]
        
        # Apply blacklist
        if blacklist:
            action_servers = [a for a in action_servers if not any(b in a["name"] for b in blacklist)]
        
        return {
            "total": len(action_servers),
            "action_servers": action_servers
        }
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out (10s limit)"}
    except Exception as e:
        return {"error": f"Failed to list action servers: {e}"}
