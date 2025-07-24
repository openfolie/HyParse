from typing import Any, Dict
from json import dumps
from concurrent.futures import ProcessPoolExecutor

from .NBT import JsonType, _nbt_to_json, _get_nested


class Inventory:
    def __init__(self, skyblock_data: Dict[str, Any], lazy_load: bool) -> None:
        # Raw skyblock_data["inventory"] holds all the NBT blobs
        self.inventory: Dict[str, Any] = skyblock_data.get("inventory", {})
        self.lazy_load = lazy_load

        # Prepare parsed cache, but don’t fill it until needed (unless eager)
        self._parsed_nbt: Dict[str, Any] = {}

        if not self.lazy_load:
            # eager: parse everything up front
            self._parsed_nbt = self._batch_parse_nbt()

    def __str__(self) -> str:
        return dumps(self.inventory, indent=3)

    def __getitem__(self, key) -> JsonType:
        return self._get_nbt_json(key)

    def __iter__(self):
        return iter(self.inventory.keys())

    def __contains__(self, key):
        return key in self.inventory

    def __len__(self) -> int:
        return len(self.inventory)

    def __getattr__(self, name: str) -> Any:
        if name in self.inventory:
            return self[name]
        raise AttributeError(f"{self.__class__.__name__!r} has no attribute {name!r}")

    def __repr__(self) -> str:
        mode = "lazy" if self.lazy_load else "eager"
        return f"<Inventory mode={mode} sections={len(self)}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Inventory):
            return NotImplemented

        # force-evaluate both sides
        self.load_all()
        other.load_all()
        return self._parsed_nbt == other._parsed_nbt

    def keys(self):
        return self.inventory.keys()

    def values(self):
        return (self[k] for k in self.inventory.keys())

    def items(self):
        return ((k, self[k]) for k in self.inventory.keys())

    def _batch_parse_nbt(self) -> Dict[str, Any]:
        # build a list of all the dotted keys we want
        static_paths = [
            ["inv_contents"],
            ["ender_chest_contents"],
            ["inv_armor"],
            ["equipment_contents"],
            ["personal_vault_contents"],
            ["wardrobe_contents"],
            ["bag_contents", "talisman_bag"],
            ["bag_contents", "potion_bag"],
            ["bag_contents", "fishing_bag"],
            ["bag_contents", "sacks_bag"],
            ["bag_contents", "quiver"],
        ]
        # add every backpack_contents.<idx>
        bc = self.inventory.get("backpack_contents", {})
        if isinstance(bc, dict):
            for idx in bc:
                static_paths.append(["backpack_contents", str(idx)])

        # gather (key → base64‑blob)
        tasks: Dict[str, str] = {}
        for path in static_paths:
            blob = _get_nested(self.inventory, path + ["data"], "")
            key = "/".join(path)
            if isinstance(blob, str) and blob:
                tasks[key] = blob
            else:
                self._parsed_nbt[key] = {}

        # parallel decode
        if tasks:
            with ProcessPoolExecutor() as exe:
                results = exe.map(_nbt_to_json, tasks.values())
                for key, res in zip(tasks, results):
                    self._parsed_nbt[key] = res

        return self._parsed_nbt

    def _get_nbt_json(self, *path: str) -> JsonType:
        """
        Return the JSON for inventory[path].data, caching it.
        """
        key = "/".join(path)
        if key not in self._parsed_nbt:
            blob = _get_nested(self.inventory, list(path) + ["data"], "")
            self._parsed_nbt[key] = _nbt_to_json(blob)
        return self._parsed_nbt[key]

    # ──────────────────────────────── @property functions ────────────────────────────────
    @property
    def player_inventory(self):
        return self._get_nbt_json("inv_contents")

    @property
    def ender_chest(self):
        return self._get_nbt_json("ender_chest_contents")

    @property
    def potion_bag(self):
        return self._get_nbt_json("bag_contents", "potion_bag")

    @property
    def talisman_bag(self):
        return self._get_nbt_json("bag_contents", "talisman_bag")

    @property
    def fishing_bag(self):
        return self._get_nbt_json("bag_contents", "fishing_bag")

    @property
    def sacks_bag(self):
        return self._get_nbt_json("bag_contents", "sacks_bag")

    @property
    def quiver(self):
        return self._get_nbt_json("bag_contents", "quiver")

    @property
    def backpacks(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        bc = self.inventory.get("backpack_contents", {})
        for idx, entry in bc.items():
            if not isinstance(entry, dict) or not entry.get("data"):
                continue
            out[idx] = self._get_nbt_json("backpack_contents", idx).get("i")
        return out

    @property
    def wardrobe(self):
        return self._get_nbt_json("wardrobe_contents")

    def load_all(self) -> Dict[str, Any]:
        """
        If you initialized with lazy_load=True, calling load_all()
        will parse *everything* up front and return the full cache.
        """
        return self._parsed_nbt if not self.lazy_load else self._batch_parse_nbt()
