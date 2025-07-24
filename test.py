from json import dump
from hyparse import Player as Skyblock


player_data = Skyblock(
    "00688fa3-020b-49b5-a11a-483210f84f22", uuid="5424b7a7f5e24d2ea77b999979e4d5bf"
)

with open("test.json", "w") as file:
    dump(player_data.inventory(lazy_load=False).inventory, file)
