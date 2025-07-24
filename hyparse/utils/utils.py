from json import dumps
from sqlite3 import connect
from typing import Any, Dict, List


def connect_linkdb():
    database = connect("accounts.sqlite")
    database.isolation_level = None  # Enables autocommit mode
    cursor = database.cursor()

    # Create the table if it doesn't exist
    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS accountlinks (
                        discord_uuid VARCHAR(255) PRIMARY KEY,
                        minecraft_uuid VARCHAR(255),
                        discord_name VARCHAR(255),
                        minecraft_name VARCHAR(255),
                        is_linked BOOLEAN
                        )     
        """)
    return cursor


def whodis(dcname):
    cursor = connect_linkdb()
    result = cursor.execute(
        f"SELECT discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked FROM accountlinks WHERE discord_name = '{dcname}'"
    ).fetchone()

    if result:
        discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked = result

    class player:
        def __init__(
            self, discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked
        ):
            self.discordid = discord_uuid
            self.minecraftid = minecraft_uuid
            self.discordname = discord_name
            self.minecraftname = minecraft_name
            self.linked = is_linked

    return player(discord_uuid, minecraft_uuid, discord_name, minecraft_name, is_linked)


def get_skill_emote(skill_name):
    skill_emotes = {
        "Catacombs": "🪦",  # Example emoji for Catacombs
        "SKILL_FISHING": "🎣",  # Emoji for Fishing
        "SKILL_ALCHEMY": "⚗️",  # Emoji for Alchemy
        "SKILL_MINING": "⛏️",  # Emoji for Mining
        "SKILL_FARMING": "🌾",  # Emoji for Farming
        "SKILL_ENCHANTING": "✨",  # Emoji for Enchanting
        "SKILL_TAMING": "🐾",  # Emoji for Taming
        "SKILL_FORGING": "🔨",  # Emoji for Foraging
        "SKILL_CARPENTRY": "🪚",  # Emoji for Carpentry
        "SKILL_COMBAT": "⚔️",  # Emoji for Combat
    }
    return skill_emotes.get(skill_name, "❓")


def json_readable(data: Dict[str, Any] | List[Any], indent: int = 3) -> str:
    return dumps(data, indent=indent)
