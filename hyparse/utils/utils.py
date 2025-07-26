from json import dumps
from typing import Any, Dict, List


def json_readable(data: Dict[str, Any] | List[Any], indent: int = 3) -> str:
    return dumps(data, indent=indent)
