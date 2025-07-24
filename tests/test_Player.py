import pytest
from hyparse import Player
from hyparse.exceptions import ExpiredAPIKey, UserNotFound

from unittest.mock import patch, MagicMock
from json import load


API_KEY = "ABCDEFG"
UUID = "0959dfbde98d4b348271ad0c5728f4fe"
PLAYER_NAME = "TheFieryWarrior"

# Mock responses
MOCK_UUID_RESPONSE = {"id": UUID}

with open("test.json") as file:
    MOCK_PROFILE_DATA = load(file)


@pytest.fixture
def mock_requests():
    with patch("hyparse.Player.requests.get") as mock_get:

        def side_effect(url, *args, **kwargs):
            if "mojang.com" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = MOCK_UUID_RESPONSE
                return mock_resp
            if "hypixel.net" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = MOCK_PROFILE_DATA
                return mock_resp
            raise ValueError("Unknown URL")

        mock_get.side_effect = side_effect
        yield mock_get


def test_player_initialization_with_name(mock_requests):
    player = Player(API_KEY, player_name=PLAYER_NAME)
    assert player.uuid == UUID
    assert player.profile_id == "aa79769f-40c3-48ec-b9cb-4dfa095335fe"


def test_player_initialization_with_uuid(mock_requests):
    player = Player(API_KEY, uuid=UUID)
    assert player.uuid == UUID


def test_purse(mock_requests):
    player = Player(API_KEY, uuid=UUID)
    assert isinstance(player.purse(), str)
    assert isinstance(player.purse(human_readable=False), float)


def test_errors_on_failed_profile_fetch():
    with patch("hyparse.Player.requests.get") as mock_get:
        # Simulate 403 error
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.json.return_value = {"success": False, "cause": "Invalid API Key"}
        mock_get.return_value = mock_resp

        with pytest.raises(ExpiredAPIKey):
            Player(API_KEY, uuid=UUID)


def test_errors_on_minecraft_user_not_found():
    with patch("hyparse.Player.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        with pytest.raises(UserNotFound):
            Player(API_KEY, player_name="unknown_user")
