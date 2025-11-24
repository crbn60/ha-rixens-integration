"""Tests for the Rixens API client."""

from unittest.mock import Mock

import pytest

from custom_components.rixens.api import RixensApiClient
from custom_components.rixens.const import CMD_MAP


@pytest.mark.asyncio
async def test_async_set_parameter_invalid_name():
    """Test setting parameter with invalid name."""
    mock_session = Mock()
    api_client = RixensApiClient(host="10.0.22.6", session=mock_session)

    with pytest.raises(
        ValueError, match="Parameter 'invalid_param' not found in CMD_MAP"
    ):
        await api_client.async_set_parameter("invalid_param", 100, CMD_MAP)


@pytest.mark.asyncio
async def test_all_cmd_map_entries():
    """Test that all CMD_MAP entries are valid integers."""
    for param_name, act_id in CMD_MAP.items():
        assert isinstance(
            param_name, str
        ), f"CMD_MAP key '{param_name}' should be string"
        assert isinstance(
            act_id, int
        ), f"CMD_MAP value for '{param_name}' should be int"
        assert act_id > 0, f"CMD_MAP value for '{param_name}' should be positive"


@pytest.mark.asyncio
async def test_cmd_map_completeness():
    """Test that CMD_MAP contains all expected parameters."""
    expected_params = {
        "setpoint",
        "fanspeed",
        "engineenable",
        "electricenable",
        "floorenable",
        "glycol",
        "fanenabled",
        "thermenabled",
    }

    for param in expected_params:
        assert param in CMD_MAP, f"Expected parameter '{param}' not found in CMD_MAP"


@pytest.mark.asyncio
async def test_cmd_map_unique_act_ids():
    """Test that all act IDs in CMD_MAP are unique."""
    act_ids = list(CMD_MAP.values())
    assert len(act_ids) == len(set(act_ids)), "CMD_MAP contains duplicate act IDs"
