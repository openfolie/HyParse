import requests
from typing import Any, Dict, Optional, Literal, Tuple
from logging import getLogger
from json import dumps
from numerize.numerize import numerize

from .exceptions import HypixelSuccessError, ExpiredAPIKey, UserNotFound
from .levels import getSkillLevel
from .skills import Dungeons, Fishing
from .player import Inventory

logger = getLogger(__name__)

SelectedProfile = Literal[
    "Apple",
    "Banana",
    "Blueberry",
    "Coconut",
    "Cucumber",
    "Grapes",
    "Kiwi",
    "Lemon",
    "Lime",
    "Mango",
    "Orange",
    "Papaya",
    "Peach",
    "Pear",
    "Pineapple",
    "Pomegranate",
    "Raspberry",
    "Strawberry",
    "Tomato",
    "Watermelon",
    "Zucchini",
]


class Player:
    _base_url = "https://api.hypixel.net/v2/skyblock"

    def __init__(
        self,
        API_KEY: str,
        player_name: Optional[str] = None,
        uuid: Optional[str] = None,
        selected_profile: Optional[SelectedProfile] = None,
    ) -> None:
        self._auth_header = {"API-Key": API_KEY}
        self.uuid = self._resolve_uuid(player_name, uuid)
        self.selected_profile = selected_profile

        self.profiles = self._fetch_profiles()
        self.profile_id, self.profile_index = self._get_profile_id_and_index(
            self.profiles
        )

        self._data: Dict[str, Any] = self.profiles[self.profile_index]["members"][
            self.uuid
        ]

    def __str__(self) -> str:
        return dumps(self.profiles, indent=3)

    def __getitem__(self, key) -> Dict[str, Any]:
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data.keys())

    def _resolve_uuid(self, player_name: Optional[str], uuid: Optional[str]) -> str:
        """Ensure exactly one of player_name or uuid is provided, and return a resolved uuid."""
        if (player_name is None) == (uuid is None):  # XOR check
            raise ValueError(
                "Provide either 'uuid' or 'player_name', not both or none."
            )

        if player_name:
            return self._minecraft_uuid(player_name)

        if uuid is None:
            raise ValueError("Incorrect Player name provided")

        return uuid

    def _fetch_profiles(self) -> list[Dict[str, Any]]:
        url = f"{self._base_url}/profiles"
        response = requests.get(
            url, headers=self._auth_header, params={"uuid": self.uuid}
        )

        data = response.json()
        if not data.get("success", False):
            if response.status_code == 403:
                raise ExpiredAPIKey("API Key is either expired or invalid")
            raise HypixelSuccessError(
                f"Response was not successful due to {data.get('cause')}"
            )

        return data.get("profiles", [])

    def _get_profile_id_and_index(
        self, profiles: list[Dict[str, Any]]
    ) -> Tuple[str, int]:
        """Gets profile id and the index at which the id is located at"""

        if self.selected_profile:
            for index, profile in enumerate(profiles):
                if (
                    profile.get("cute_name", "").lower()
                    == self.selected_profile.lower()
                ):
                    return profile["profile_id"], index
        else:
            for index, profile in enumerate(profiles):
                if profile.get("selected"):
                    return profile["profile_id"], index

        raise ValueError("No matching profile found.")

    def _minecraft_uuid(self, playername: str):
        response = requests.get(
            "https://api.mojang.com/users/profiles/minecraft/" + playername
        )

        if response.status_code == 200:
            return response.json().get("id")

        else:
            raise UserNotFound("Minecraft user was not found")

    @property
    def skill_levels(self) -> Dict[str, Dict[str, int | float]]:
        """Converts raw exp into skyblock level"""

        player_experience: Dict[str, int] = self._data["player_data"]
        experiences = player_experience.get("experience")

        # User doesn't have any skill unlocked
        if experiences is None:
            return {}

        skill_levels = {}

        for skill_name, skill_exp in player_experience.items():
            skill_level = getSkillLevel(skill_xp=skill_exp)
            skill_levels[skill_name] = skill_level

        return skill_levels

    @property
    def skyblock_data(self) -> Dict[str, Any]:
        return self._data

    @property
    def dungeons(self) -> Dungeons:
        return Dungeons(self._data)

    @property
    def fishing(self) -> Fishing:
        return Fishing(self._data)

    def inventory(self, *, lazy_load: bool = True) -> Inventory:
        return Inventory(self._data, lazy_load)

    def purse(self, human_readable: bool = True) -> float | str:
        banking: Dict[str, Any] = self.profiles[self.profile_index]["banking"]
        balance: float = banking.get("balance", 0)

        if not human_readable:
            return balance

        return numerize(balance)
