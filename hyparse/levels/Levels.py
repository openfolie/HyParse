import json
from os import path
from typing import TypedDict


JSON_PATH = path.abspath(path.join(path.dirname(__file__), "json", "levels.json"))


class SkillInfo(TypedDict):
    skill_level: int
    remaining_xp: float
    xp_required_to_level_up: float


def getSkillLevel(
    initial_exp: float,
    is_catacombs: bool = False,
) -> SkillInfo:
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    skill_type = "Catacombs" if is_catacombs else "Skills"
    skill_data = data[skill_type]

    # Convert string keys to int and sort
    cumulative_xp = {}
    xp_required = {}
    for level_str, (xp_req, total_xp) in skill_data.items():
        level = int(level_str)
        xp_required[level] = xp_req
        cumulative_xp[level] = total_xp

    # Determine skill level
    skill_level = 0
    for level in sorted(cumulative_xp):
        if initial_exp < cumulative_xp[level]:
            skill_level = level - 1
            break
    else:
        skill_level = max(cumulative_xp)

    remaining_xp = initial_exp - cumulative_xp.get(skill_level, 0)
    xp_to_next = xp_required.get(skill_level + 1, 0)

    return {
        "skill_level": skill_level,
        "remaining_xp": remaining_xp,
        "xp_required_to_level_up": xp_to_next,
    }
