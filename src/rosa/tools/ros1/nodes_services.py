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
import rosnode
import rosservice
from langchain.agents import tool

from . import utils
from .utils import get_entities


@tool
def rosnode_list(
    pattern: Optional[str] = None,
    namespace: Optional[str] = None,
    blacklist: List[str] = None,
) -> dict:
    """Returns a dictionary containing a list of running ROS nodes and other metadata.
    
    By default, returns ALL nodes in the system. Most users should NOT specify namespace.

    :param pattern: (optional) A Python regex pattern to filter the list of nodes. Use ".*" or leave empty to see all nodes.
    :param namespace: (optional) ROS namespace to scope return values by. Leave empty for root namespace (most common). Only use this if you need nodes from a specific sub-namespace.
    """
    try:
        total, in_namespace, match_pattern, nodes = get_entities(
            "node", pattern, namespace, blacklist
        )
    except Exception as e:
        return {"error": f"Failed to get ROS nodes: {e}"}

    if blacklist:
        nodes = list(
            filter(
                lambda x: not any(regex.match(f".*{bl}.*", x) for bl in blacklist),
                nodes,
            )
        )

    return dict(
        namespace=namespace if namespace else "/",
        pattern=pattern if pattern else ".*",
        total=total,
        in_namespace=in_namespace,
        match_pattern=match_pattern,
        nodes=nodes,
    )


@tool
def rosnode_info(nodes: List[str]) -> dict:
    """Returns details about specific ROS node(s).

    :param nodes: A list of ROS node names. Smaller lists are better for performance.
    """
    details = {}

    for node in nodes:
        if utils._ros_state_cache:
            cached = utils._ros_state_cache.get_node_info(node)
            if cached is not None:
                details[node] = cached
                continue

        info_text = rosnode.get_node_info_description(node)
        processed = info_text.replace("\n", " ")
        details[node] = processed

        if utils._ros_state_cache:
            utils._ros_state_cache.set_node_info(node, processed)

    return details


@tool
def rosservice_list(
    node: Optional[str] = None,
    namespace: Optional[str] = None,
    include_nodes: bool = False,
    regex_pattern: Optional[str] = None,
    exclude_logging: bool = True,
    exclude_rosapi: bool = True,
    exclude_parameters: bool = True,
    exclude_pattern: Optional[str] = None,
    blacklist: List[str] = None,
):
    """Returns a list of available ROS services.

    :param node: (optional) The name of the node to retrieve services from.
    :param namespace: (optional) ROS namespace to scope return values by.
    :param include_nodes: (optional) If True, return list will be [service_name, [node]]
    :param regex_pattern: (optional) A Python regex pattern to filter the list of services.
    :param exclude_logging: (optional) If True, exclude services related to logging.
    :param exclude_rosapi: (optional) If True, exclude services related to the ROS API.
    :param exclude_parameters: (optional) If True, exclude services related to parameters.
    :param exclude_pattern: (optional) A Python regex pattern to exclude services.
    """
    services = rosservice.get_service_list(node, namespace, include_nodes)

    if exclude_logging:
        services = list(filter(lambda x: not x.startswith("/rosout"), services))

        # Exclude if the word "logger" is in the service name
        services = list(filter(lambda x: "logger" not in x, services))

    if exclude_rosapi:
        services = list(filter(lambda x: not x.startswith("/rosapi"), services))

    if exclude_parameters:
        services = list(filter(lambda x: "param" not in x, services))

    if exclude_pattern:
        services = list(
            filter(lambda x: not regex.match(f".*{exclude_pattern}", x), services)
        )

    if regex_pattern:
        services = list(
            filter(lambda x: regex.match(f".*{regex_pattern}", x), services)
        )

    if blacklist:
        services = list(
            filter(
                lambda x: not any(
                    regex.match(f".*{pattern}", x) for pattern in blacklist
                ),
                services,
            )
        )

    return services


@tool
def rosservice_info(services: List[str]) -> dict:
    """Returns details about specific ROS service(s).

    :param services: A list of ROS service names. Smaller lists are better for performance.
    """
    details = {}

    for service in services:
        service_uri = rosservice.get_service_uri(service)
        info_text = rosservice.get_service_headers(service, service_uri)
        details[service] = info_text

    return details


@tool
def rosservice_call(service: str, args: Optional[List[any]] = None) -> dict:
    """Calls a specific ROS service with the provided arguments.

    :param service: The name of the ROS service to call.
    :param args: A list of arguments to pass to the service.
    """
    if not args:
        args = []
    try:
        response = rosservice.call_service(service, args)
        return response
    except Exception as e:
        return {"error": f"Failed to call service '{service}': {e}"}
