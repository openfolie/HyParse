import pytest

from unittest.mock import patch, MagicMock
from json import load
from os import path
from typing import Generator, Tuple, Dict, Any

from hyparse import Player
from hyparse.exceptions import ExpiredAPIKey, UserNotFound, HypixelSuccessError


API_KEY = "ABCDEFG"
UUID = "0959dfbde98d4b348271ad0c5728f4fe"
PLAYER_NAME = "TheFieryWarrior"

# Mock responses
MOCK_UUID_RESPONSE = {"id": UUID, "name": PLAYER_NAME}

TEST_JSON = path.join(path.dirname(__file__), "json", "test_Player.json")


@pytest.fixture
def mock_requests() -> Generator[Tuple[MagicMock, Dict[str, Any]], None, None]:
    with open(TEST_JSON) as file:
        MOCK_PROFILE_DATA = load(file)

    with patch("hyparse.Player.requests.get") as mock_get:

        def side_effect(url, *args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            if "mojang.com" in url:
                mock_resp.json.return_value = MOCK_UUID_RESPONSE
                return mock_resp

            elif "hypixel.net" in url:
                mock_resp.json.return_value = MOCK_PROFILE_DATA
                return mock_resp

            raise RuntimeError(f"[MOCK FAILURE] Unhandled request to: {url}")

        mock_get.side_effect = side_effect
        yield mock_get, MOCK_PROFILE_DATA["profiles"]


def test_player_initialization_with_name(mock_requests):
    mock_get, profile_data = mock_requests

    profile_id = next(
        profile["profile_id"] for profile in profile_data if profile["selected"]
    )

    player = Player(API_KEY, player_name=PLAYER_NAME)
    assert player.uuid == UUID
    assert player.profile_id == profile_id


def test_player_initialization_with_name_and_selected_profile(mock_requests):
    mock_get, profile_data = mock_requests

    TEST_PROFILE = "Zucchini"

    profile_id = next(
        profile["profile_id"]
        for profile in profile_data
        if profile["cute_name"] == TEST_PROFILE
    )
    player = Player(API_KEY, player_name=PLAYER_NAME, selected_profile=TEST_PROFILE)
    assert player.uuid == UUID
    assert player.profile_id == profile_id


def test_player_initialization_with_uuid(mock_requests):
    player = Player(API_KEY, uuid=UUID)
    assert player.uuid == UUID


def test_purse(mock_requests):
    player = Player(API_KEY, uuid=UUID)
    assert isinstance(player.purse(), str)
    assert isinstance(player.purse(human_readable=False), float)


def test_errors_on_failed_invalid_api_key():
    with patch("hyparse.Player.requests.get") as mock_get:
        # Simulate 403 error
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.json.return_value = {"success": False, "cause": "Invalid API Key"}
        mock_get.return_value = mock_resp

        with pytest.raises(ExpiredAPIKey):
            Player(API_KEY, uuid=UUID)


def test_errors_on_failed_fetch_request():
    with patch("hyparse.Player.requests.get") as mock_get:
        # Simulate a 404 Error
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.json.return_value = {
            "success": False,
            "cause": "Insert random error message, too lazy to think of one",
        }

        mock_get.return_value = mock_resp

        with pytest.raises(
            HypixelSuccessError,
            match="Insert random error message, too lazy to think of one",
        ):
            Player(API_KEY, uuid=UUID)


def test_errors_on_minecraft_user_not_found():
    with patch("hyparse.Player.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        with pytest.raises(UserNotFound):
            Player(API_KEY, player_name="unknown_user")


def test_skill_levels(mock_requests):
    expected_skills = [
        "SKILL_FISHING",
        "SKILL_ALCHEMY",
        "SKILL_RUNECRAFTING",
        "SKILL_MINING",
        "SKILL_FARMING",
        "SKILL_ENCHANTING",
        "SKILL_TAMING",
        "SKILL_FORAGING",
        "SKILL_SOCIAL",
        "SKILL_CARPENTRY",
        "SKILL_COMBAT",
    ]
    player = Player(API_KEY=API_KEY, uuid=UUID, selected_profile="Zucchini")

    skill_levels = player.skill_levels

    for skills in expected_skills:
        assert skills in skill_levels

    for skill in skill_levels.values():
        assert "remaining_xp" in skill
        assert "skill_level" in skill
        assert "xp_required_to_level_up" in skill
