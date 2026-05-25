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
from typing import Optional, List

import regex
import rospy
import rostopic
from langchain.agents import tool

from . import utils
from .utils import get_entities


@tool
def rostopic_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
) -> dict:
    """Returns a list of available ROS topics.
    
    By default, returns ALL topics in the system. Most users should NOT specify namespace.

    :param pattern: (optional) A Python regex pattern to filter the list of topics. Use ".*" or leave empty to see all topics.
    :param namespace: (optional) ROS namespace to scope return values by. Leave empty for root namespace (most common). Only use this if you need topics from a specific sub-namespace like "/my_robot".
    """
    try:
        total, in_namespace, match_pattern, topics = get_entities(
            "topic", pattern, namespace, blacklist
        )
    except Exception as e:
        return {"error": f"Failed to get ROS topics: {e}"}

    if blacklist:
        topics = list(
            filter(
                lambda x: not any(regex.match(f".*{bl}.*", x) for bl in blacklist),
                topics,
            )
        )

    return dict(
        namespace=namespace if namespace else "/",
        pattern=pattern if pattern else ".*",
        total=total,
        in_namespace=in_namespace,
        match_pattern=match_pattern,
        topics=topics,
    )


@tool
def rostopic_info(topics: List[str]) -> dict:
    """Returns details about specific ROS topic(s).

    :param topics: A list of ROS topic names. Smaller lists are better for performance.
    """
    details = {}

    for topic in topics:
        if utils._ros_state_cache:
            cached = utils._ros_state_cache.get_topic_info(topic)
            if cached is not None:
                details[topic] = cached
                continue

        info_text = rostopic.get_info_text(topic)
        # info_text is of the following format:
        #   Type: std_msgs/String
        #   Publishers:
        #   * /topic/name
        #   Subscribers:
        #   * /rosout"
        # Convert this into a dictionary for easier parsing

        topic_details = {
            "topic": topic,
            "type": None,
            "publishers": [],
            "subscribers": [],
        }

        # capture the type information using regex
        type_match = regex.match(r"Type: (.+)", info_text)
        if type_match:
            topic_details["type"] = type_match.group(1)

        # capture the publishers (need to get the list after the "Publishers:" line and before the "Subscribers:" line)
        # start by make an array of lines, then iterate through them
        lines = info_text.split("\n")
        capture_publishers = False
        capture_subscribers = False

        def strip_star(line: str) -> str:
            return line.strip().replace("* ", "")

        for line in lines:
            if "Publishers:" in line:
                capture_publishers = True
                continue
            if "Subscribers:" in line:
                capture_publishers = False
                capture_subscribers = True
                continue
            if capture_publishers:
                line = strip_star(line)
                topic_details["publishers"].append(line)
            if capture_subscribers:
                line = strip_star(line)
                topic_details["subscribers"].append(line)
        details[topic] = topic_details

        if utils._ros_state_cache:
            utils._ros_state_cache.set_topic_info(topic, topic_details)

    return details


@tool
def rostopic_echo(
    topic: str,
    count: int,
    return_echoes: bool = False,
    delay: float = 1.0,
    timeout: float = 1.0,
) -> dict:
    """
    Echoes the contents of a specific ROS topic.

    :param topic: The name of the ROS topic to echo.
    :param count: The number of messages to echo. Valid range is 1-100.
    :param return_echoes: If True, return the messages as a list with the response.
    :param delay: Time to wait between each message in seconds.
    :param timeout: Max time to wait for a message before timing out.

    :note: Do not set return_echoes to True if the number of messages is large.
           This will cause the response to be too large and may cause the tool to fail.
    """
    # Get the message class so we can retrieve messages from the topic
    msg_class = rostopic.get_topic_class(topic)[0]
    if not msg_class:
        return {"error": f"Failed to get message class for topic '{topic}'"}

    # Retrieve the messages from the topic
    msgs = []

    for i in range(count):
        try:
            msg = rospy.wait_for_message(topic, msg_class, timeout)

            if return_echoes:
                msgs.append(msg)

            if delay > 0:
                time.sleep(delay)

        except (rospy.ROSException, rospy.ROSInterruptException) as e:
            break

    response = dict(topic=topic, requested_count=count, actual_count=len(msgs))

    if return_echoes:
        response["echoes"] = msgs[:10]
        response["truncated"] = len(msgs) > 10

    return response
