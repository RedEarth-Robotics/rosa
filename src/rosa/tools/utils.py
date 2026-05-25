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

import regex
from typing import Any, Callable, Dict, List, Optional


def filter_by_pattern(
    items: List[str],
    pattern: Optional[str] = None,
    blacklist: Optional[List[str]] = None,
) -> List[str]:
    """Filter a list of items by pattern and blacklist."""
    result = items
    if blacklist:
        result = list(
            filter(
                lambda x: not any(regex.match(f".*{bl}.*", x) for bl in blacklist),
                result,
            )
        )
    if pattern:
        result = list(filter(lambda x: regex.match(f".*{pattern}.*", x), result))
    return result


def format_tool_response(
    data: Any = None,
    error: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> Dict[str, Any]:
    """Format a consistent response dictionary for tool functions."""
    response: Dict[str, Any] = {}
    if data is not None:
        response["data"] = data
    if error:
        response["error"] = error
    if suggestion:
        response["suggestion"] = suggestion
    return response


def safe_tool_execute(
    operation_name: str,
    func: Callable,
    *args,
    **kwargs,
) -> Dict[str, Any]:
    """Execute a tool function with standardized error handling."""
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        return format_tool_response(
            error=f"Failed to {operation_name}: {e}",
            suggestion="Check that the ROS system is running and the target exists.",
        )
