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
import rosgraph
import rosparam
from langchain.agents import tool


@tool
def rosgraph_get(
    node_pattern: Optional[str] = ".*",
    topic_pattern: Optional[str] = ".*",
    blacklist: List[str] = None,
    exclude_self_connections: bool = True,
) -> dict:
    """
    Get a list of tuples representing nodes and topics in the ROS graph.

    :param node_pattern: A regex pattern for the nodes to include in the graph (publishers and subscribers).
    :param topic_pattern: A regex pattern for the topics to include in the graph.
    :param exclude_self_connections: Exclude connections where the publisher and subscriber are the same node.

    :note: you should avoid using the topic pattern when searching for nodes, as it may not return any results.
    :important: you must NOT use this function to get lists of nodes, topics, etc.

    Example regex patterns:
    - .*node.* any node containing "node"
    - .*node any node that ends with "node"
    - node.* any node that starts with "node"
    - (.*node1.*|.*node2.*|.*node3.*) any node containing either "node1", "node2", or "node3"
    """
    try:
        publishers, subscribers, services = rosgraph.masterapi.Master(
            "/rosout"
        ).getSystemState()
    except Exception as e:
        return {"error": f"Failed to get ROS graph: {e}"}

    graph = []
    topic_pub_map = {}
    topic_sub_map = {}

    for pub in publishers:
        for node in pub[1]:
            if pub[0] in topic_pub_map:
                topic_pub_map[pub[0]].append(node)
            else:
                topic_pub_map[pub[0]] = [node]

    for sub in subscribers:
        for node in sub[1]:
            if sub[0] in topic_sub_map:
                topic_sub_map[sub[0]].append(node)
            else:
                topic_sub_map[sub[0]] = [node]

    # Convert the maps to a graph
    for topic, pubs in topic_pub_map.items():
        if topic in topic_sub_map:
            for pub in pubs:
                for sub in topic_sub_map[topic]:
                    if topic_pattern and not regex.match(f"{topic_pattern}", topic):
                        continue
                    graph.append((pub, topic, sub))

    # Filter out any blacklisted entries
    blacklist = blacklist if blacklist else []
    graph = list(
        filter(
            lambda x: not any(
                regex.match(f".*{word}.*", entry) for word in blacklist for entry in x
            ),
            graph,
        )
    )

    # Remove any triple that does not have a publisher or subscriber that contains the node pattern
    if node_pattern:
        graph = list(
            filter(
                lambda x: regex.match(f"{node_pattern}", x[0])
                or regex.match(f"{node_pattern}", x[2]),
                graph,
            )
        )

    if exclude_self_connections:
        graph = list(filter(lambda x: x[0] != x[2], graph))

    if not graph or len(graph) == 0:
        reasons = []
        if node_pattern:
            reasons.append(f"node pattern '{node_pattern}' filtered out all connections")
        if topic_pattern and topic_pattern != ".*":
            reasons.append(f"topic pattern '{topic_pattern}' filtered out all topics")
        if exclude_self_connections:
            reasons.append("self-connections were excluded")
        if blacklist:
            reasons.append(f"blacklist excluded: {blacklist}")
        
        reason_str = "; ".join(reasons) if reasons else "no matching connections found"
        
        return {
            "error": f"No results found for the specified parameters. Reason: {reason_str}.",
            "suggestion": "Try broadening your search by using '.*' for patterns, or check if the expected nodes/topics are running.",
            "filters_applied": {
                "node_pattern": node_pattern,
                "topic_pattern": topic_pattern,
                "exclude_self_connections": exclude_self_connections,
                "blacklist": blacklist
            }
        }

    # Get count of unique nodes in the graph (publishers and subscribers)
    unique_nodes = set()
    for pub, _, sub in graph:
        unique_nodes.add(pub)
        unique_nodes.add(sub)

    node_count = len(unique_nodes)

    # Get count of unique topics in the graph
    unique_topics = set()
    for _, topic, _ in graph:
        unique_topics.add(topic)

    topic_count = len(unique_topics)

    response = dict(
        graph_convention="Each tuple in the graph is of the form (publisher, topic, subscriber).",
        nuance="Disconnected nodes are not included in this graph.",
        node_count=node_count,
        topic_count=topic_count,
        total_connections=len(graph),
        graph=graph,
    )

    max_render_size = 50
    if len(graph) > 50:
        response["warning"] = (
            f"The graph is too large to display or render (size > {max_render_size}. Please make "
            f"some recommendations to the user on how to filter the graph to a more manageable "
            f"size. Do not attempt to render the graph."
        )

    return response


@tool
def rosparam_list(namespace: str = "/", blacklist: List[str] = None) -> dict:
    """Returns a list of all ROS parameters available on the system.

    :param namespace: (optional) ROS namespace to scope return values by.
    """
    try:
        params = rosparam.list_params(namespace)
        if blacklist:
            params = list(
                filter(
                    lambda x: not any(
                        regex.match(f".*{pattern}", x) for pattern in blacklist
                    ),
                    params,
                )
            )
        return {"namespace": namespace, "total": len(params), "ros_params": params}
    except Exception as e:
        return {"error": f"Failed to get ROS parameters: {e}"}


@tool
def rosparam_get(params: List[str]) -> dict:
    """Returns the value of one or more ROS parameters.

    :param params: A list of ROS parameter names. Parameter names must be fully resolved. Do not use wildcards.
    """
    values = {}
    for param in params:
        p = rosparam.get_param(param)
        values[param] = p
    return values


@tool
def rosparam_set(param: str, value: str, is_rosa_param: bool) -> str:
    """Sets the value of a specific ROS parameter.

    :param param: The name of the ROS parameter to set.
    :param value: The value to set the parameter to.
    :param is_rosa_param: If True, set the parameter in the ROSA namespace.
    """

    if is_rosa_param and not param.startswith("/rosa"):
        param = f"/rosa/{param}".replace("//", "/")

    try:
        rosparam.set_param(param, value)
        return f"Set parameter '{param}' to '{value}'."
    except Exception as e:
        return f"Failed to set parameter '{param}' to '{value}': {e}. Try again!"
