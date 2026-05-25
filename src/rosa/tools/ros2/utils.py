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

import re
import subprocess
from typing import List, Optional, Tuple

from ...cache import ROSStateCache

# Global cache instance (set by ROSATools.__init__)
_ros_state_cache: ROSStateCache = None


def set_ros_state_cache(cache: ROSStateCache):
    """Set the ROS state cache instance. Called by ROSATools."""
    global _ros_state_cache
    _ros_state_cache = cache


def execute_ros_command(command: str) -> Tuple[bool, str]:
    """
    Execute a ROS2 command.

    :param command: The ROS2 command to execute.
    :return: A tuple containing a boolean indicating success and the output of the command.
    """

    # Validate the command is a proper ROS2 command
    cmd = command.split(" ")
    valid_ros2_commands = ["node", "topic", "service", "param", "doctor"]

    if len(cmd) < 2:
        raise ValueError(f"'{command}' is not a valid ROS2 command.")
    if cmd[0] != "ros2":
        raise ValueError(f"'{command}' is not a valid ROS2 command.")
    if cmd[1] not in valid_ros2_commands:
        raise ValueError(f"'ros2 {cmd[1]}' is not a valid ros2 subcommand.")

    try:
        output = subprocess.check_output(command, shell=True).decode()
        return True, output
    except Exception as e:
        return False, str(e)


def get_entities(
    cmd: str,
    delimiter: str = "\n",
    pattern: str = None,
    blacklist: Optional[List[str]] = None,
) -> List[str]:
    """
    Get a list of ROS2 entities (nodes, topics, services, etc.).

    :param cmd: the ROS2 command to execute.
    :param delimiter: The delimiter to split the output by.
    :param pattern: A regular expression pattern to filter the list of entities.
    :return:
    """
    entities = None

    if _ros_state_cache:
        if cmd == "ros2 topic list":
            entities = _ros_state_cache.get_topics()
        elif cmd == "ros2 node list":
            entities = _ros_state_cache.get_nodes()
        elif cmd == "ros2 service list":
            entities = _ros_state_cache.get_services()

    if entities is None:
        success, output = execute_ros_command(cmd)

        if not success:
            return [output]

        entities = output.split(delimiter)
        entities = [e for e in entities if e.strip() != ""]

        if _ros_state_cache:
            if cmd == "ros2 topic list":
                _ros_state_cache.set_topics(entities)
            elif cmd == "ros2 node list":
                _ros_state_cache.set_nodes(entities)
            elif cmd == "ros2 service list":
                _ros_state_cache.set_services(entities)

    # Filter out blacklisted entities
    if blacklist:
        entities = list(
            filter(
                lambda x: not any(
                    re.match(f".*{pattern}.*", x) for pattern in blacklist
                ),
                entities,
            )
        )

    if pattern:
        entities = list(filter(lambda x: re.match(f".*{pattern}.*", x), entities))

    entities = [e for e in entities if e.strip() != ""]

    return entities
