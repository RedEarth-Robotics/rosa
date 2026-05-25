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

from typing import List, Optional

import regex
import rosnode
import rostopic

from ...cache import ROSStateCache

# Global cache instance (set by ROSATools.__init__)
_ros_state_cache: ROSStateCache = None


def set_ros_state_cache(cache: ROSStateCache):
    """Set the ROS state cache instance. Called by ROSATools."""
    global _ros_state_cache
    _ros_state_cache = cache


def get_entities(
    type: str,
    pattern: Optional[str],
    namespace: Optional[str],
    blacklist: List[str] = None,
):
    """Convenience function because topic and node retrieval basically do the same thing."""
    entities = []

    if type == "topic":
        if _ros_state_cache:
            cached = _ros_state_cache.get_topics()
            if cached is not None:
                entities = cached
            else:
                pub, sub = rostopic.get_topic_list()
                pub = list(map(lambda x: x[0], pub))
                sub = list(map(lambda x: x[0], sub))
                entities = sorted(list(set(pub + sub)))
                _ros_state_cache.set_topics(entities)
        else:
            pub, sub = rostopic.get_topic_list()
            pub = list(map(lambda x: x[0], pub))
            sub = list(map(lambda x: x[0], sub))
            entities = sorted(list(set(pub + sub)))
    elif type == "node":
        if _ros_state_cache:
            cached = _ros_state_cache.get_nodes()
            if cached is not None:
                entities = cached
            else:
                entities = rosnode.get_node_names()
                _ros_state_cache.set_nodes(entities)
        else:
            entities = rosnode.get_node_names()
    total = len(entities)

    if namespace:
        # Handle root namespace specially - topics like /turtle1/cmd_vel are in root namespace
        if namespace == "/":
            # All topics starting with / are in root namespace
            # Don't filter, they're all in root namespace already
            pass
        else:
            # For non-root namespaces, filter for topics that start with namespace/
            entities = list(filter(lambda x: x.startswith(namespace + "/"), entities))
    in_namespace = len(entities)

    if pattern:
        entities = list(filter(lambda x: regex.match(f".*{pattern}.*", x), entities))
    match_pattern = len(entities)

    if blacklist:
        entities = list(
            filter(
                lambda x: not any(regex.match(f".*{bl}.*", x) for bl in blacklist),
                entities,
            )
        )

    if total == 0:
        entities = [f"There are currently no {type}s available in the system."]
    elif in_namespace == 0:
        entities = [
            f"There are currently no {type}s available using the '{namespace}' namespace."
        ]
    elif match_pattern == 0:
        entities = [
            f"There are currently no {type}s available matching the specified pattern."
        ]

    return total, in_namespace, match_pattern, sorted(entities)
