from typing import Any, Dict

from hyparse.levels import getSkillLevel
from .Catacombs import Catacombs


class Dungeons:
    def __init__(self, skyblock_data: Dict[str, Any]) -> None:
        self._data = skyblock_data
        self.dungeon_data = self._get_dungeon_data()
        self.dungeon_types: Dict[str, Any] = self.dungeon_data.get("dungeon_types", {})

    def _get_dungeon_data(self) -> Dict[str, Any]:
        return self._data.get("dungeons", {})

    @property
    def catacombs(self) -> Catacombs:
        return Catacombs(self.dungeon_types.get("catacombs", {}))

    @property
    def master_catacombs(self) -> Catacombs:
        return Catacombs(self.dungeon_types.get("master_catacombs", {}))

    @property
    def cata_level(self):
        catacombs_data: Dict[str, Any] = self.dungeon_types.get("catacombs", {})
        experience: float = catacombs_data.get("experience", 0)
        level = getSkillLevel(experience, is_catacombs=True)
        return level
