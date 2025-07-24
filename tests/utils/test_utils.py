import json
from hyparse.utils.utils import json_readable


def test_json_readable_with_dict():
    data = {"a": 1, "b": {"c": 2}}
    expected = json.dumps(data, indent=3)
    assert json_readable(data) == expected


def test_json_readable_with_list():
    data = [1, 2, {"a": 3}]
    expected = json.dumps(data, indent=3)
    assert json_readable(data) == expected


def test_json_readable_with_custom_indent():
    data = {"key": "value"}
    expected = json.dumps(data, indent=2)
    assert json_readable(data, indent=2) == expected
