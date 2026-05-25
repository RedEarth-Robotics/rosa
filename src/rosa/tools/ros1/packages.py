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

from typing import Optional, List

import regex
import rospkg
import rosmsg
from langchain.agents import tool


@tool
def rosmsg_info(msg_type: List[str]) -> dict:
    """Returns details about a specific ROS message type.

    :param msg_type: A list of ROS message types. Smaller lists are better for performance.
    """
    details = {}

    for msg in msg_type:
        msg_path = rosmsg.get_msg_text(msg)
        details[msg] = msg_path
    return details


@tool
def rossrv_info(srv_type: List[str], raw: bool = False) -> dict:
    """Returns details about a specific ROS service type.

    :param srv_type: A list of ROS service types. Smaller lists are better for performance.
    :param raw: (optional) if True, include comments and whitespace (default: False)
    """
    details = {}

    for srv in srv_type:
        # Get the Python class corresponding to the srv file
        srv_path = rosmsg.get_srv_text(srv, raw=raw)
        details[srv] = srv_path
    return details


@tool
def rospkg_list(
    package_pattern: str = ".*",
    ignore_msgs: bool = True,
    blacklist: Optional[List[str]] = None,
) -> dict:
    """Returns a list of ROS packages available on the system.

    :param package_pattern: A Python regex pattern to filter the list of packages. Defaults to '.*'.
    :param ignore_msgs: If True, ignore packages that end in 'msgs'.
    """
    packages = rospkg.RosPack().list()
    count = len(packages)

    if ignore_msgs:
        packages = list(filter(lambda x: not x.endswith("msgs"), packages))

    msg_pkg_count = count - len(packages)

    if package_pattern and package_pattern != ".*":
        packages = list(
            filter(lambda x: regex.match(f".*{package_pattern}", x), packages)
        )

    if blacklist:
        packages = list(
            filter(
                lambda x: not any(
                    regex.match(f".*{pattern}", x) for pattern in blacklist
                ),
                packages,
            )
        )

    matches = len(packages)
    packages = sorted(packages)
    packages = dict(
        total=count,
        msg_pkg_count=msg_pkg_count,
        match_pattern=matches,
        packages=packages,
    )

    return packages
