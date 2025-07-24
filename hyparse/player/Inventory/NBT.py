import operator
from base64 import b64decode
from typing import Union, List, Dict, Any, Tuple, Deque
from gzip import decompress
from collections import deque

from nbtlib import File
from io import BytesIO
from functools import reduce

JsonType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def _convert_nbt_tag(tag: Any) -> Any:
    stack: Deque[Tuple[Union[dict, list, None], Any, Union[str, int, None]]] = deque()
    stack.append((None, tag, None))
    root = None

    while stack:
        parent, current, key = stack.pop()

        # Resolve .value if it exists
        while hasattr(current, "value"):
            current = current.value

        # Handle dict
        if isinstance(current, dict):
            converted = {}
            if parent is not None:
                if isinstance(parent, dict) and isinstance(key, str):
                    parent[key] = converted
                elif isinstance(parent, list) and isinstance(key, int):
                    parent[key] = converted

            else:
                root = converted
            for k, v in current.items():
                stack.append((converted, v, k))

        # Handle list
        elif isinstance(current, list):
            converted = [None] * len(current)
            if parent is not None:
                if isinstance(parent, dict) and isinstance(key, str):
                    parent[key] = converted
                elif isinstance(parent, list) and isinstance(key, int):
                    parent[key] = converted

            else:
                root = converted
            for i in range(len(current) - 1, -1, -1):  # Reverse to preserve order
                stack.append((converted, current[i], i))

        # Base case (primitive)
        else:
            if parent is not None:
                if isinstance(parent, dict) and isinstance(key, str):
                    parent[key] = current
                elif isinstance(parent, list) and isinstance(key, int):
                    parent[key] = current
            else:
                root = current

    return root


def _nbt_to_json(nbt_data: str) -> JsonType:
    if not nbt_data:
        return {}

    decoded = b64decode(nbt_data)
    decompressed = decompress(decoded)
    nbt_file = File.parse(BytesIO(decompressed))
    return _convert_nbt_tag(nbt_file)


def _get_nested(d: Dict, path: List[str], default=None):
    """Safely do d[path[0]][path[1]]…"""
    try:
        return reduce(operator.getitem, path, d)
    except (KeyError, TypeError):
        return default
