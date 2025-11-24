"""Tests for Rixens switch entities."""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.rixens.const import CMD_MAP
from custom_components.rixens.switch import SWITCH_KEYS, RixensSwitch


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = {
        "engineenable": 1,
        "electricenable": 0,
        "floorenable": 1,
        "glycol": 0,
        "fanenabled": 1,
        "thermenabled": 1,
    }
    coordinator.api = Mock()
    coordinator.api.async_set_value = AsyncMock(return_value=True)
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = Mock()
    entry.entry_id = "test_entry_123"
    return entry


@pytest.mark.asyncio
async def test_switch_is_on(mock_coordinator, mock_entry):
    """Test switch is_on property."""
    switch = RixensSwitch(mock_coordinator, mock_entry, "engineenable")

    assert switch.is_on is True

    switch2 = RixensSwitch(mock_coordinator, mock_entry, "electricenable")
    assert switch2.is_on is False


@pytest.mark.asyncio
async def test_switch_turn_on(mock_coordinator, mock_entry):
    """Test turning switch on."""
    switch = RixensSwitch(mock_coordinator, mock_entry, "engineenable")

    await switch.async_turn_on()

    mock_coordinator.api.async_set_value.assert_called_once_with(
        CMD_MAP["engineenable"], 1
    )
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_switch_turn_off(mock_coordinator, mock_entry):
    """Test turning switch off."""
    switch = RixensSwitch(mock_coordinator, mock_entry, "engineenable")

    await switch.async_turn_off()

    mock_coordinator.api.async_set_value.assert_called_once_with(
        CMD_MAP["engineenable"], 0
    )
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_switch_turn_on_failure(mock_coordinator, mock_entry):
    """Test turning switch on when API call fails."""
    mock_coordinator.api.async_set_value.return_value = False
    switch = RixensSwitch(mock_coordinator, mock_entry, "engineenable")

    await switch.async_turn_on()

    mock_coordinator.api.async_set_value.assert_called_once()
    # Refresh should not be called on failure
    mock_coordinator.async_request_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_switch_turn_off_failure(mock_coordinator, mock_entry):
    """Test turning switch off when API call fails."""
    mock_coordinator.api.async_set_value.return_value = False
    switch = RixensSwitch(mock_coordinator, mock_entry, "electricenable")

    await switch.async_turn_off()

    mock_coordinator.api.async_set_value.assert_called_once()
    mock_coordinator.async_request_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_switch_unique_id(mock_coordinator, mock_entry):
    """Test switch unique ID generation."""
    switch = RixensSwitch(mock_coordinator, mock_entry, "engineenable")

    assert switch.unique_id == "test_entry_123_engineenable"


@pytest.mark.asyncio
async def test_switch_name(mock_coordinator, mock_entry):
    """Test switch name."""
    switch = RixensSwitch(mock_coordinator, mock_entry, "engineenable")

    assert switch.name == "engineenable"


@pytest.mark.asyncio
async def test_all_switch_keys_in_cmd_map():
    """Test that all switch keys have CMD_MAP entries."""
    for key in SWITCH_KEYS:
        assert key in CMD_MAP, f"Switch key '{key}' not found in CMD_MAP"


@pytest.mark.asyncio
async def test_glycol_switch_control(mock_coordinator, mock_entry):
    """Test glycol switch control operations."""
    switch = RixensSwitch(mock_coordinator, mock_entry, "glycol")

    # Test turn on
    await switch.async_turn_on()
    mock_coordinator.api.async_set_value.assert_called_with(CMD_MAP["glycol"], 1)

    # Reset mock
    mock_coordinator.api.async_set_value.reset_mock()
    mock_coordinator.async_request_refresh.reset_mock()

    # Test turn off
    await switch.async_turn_off()
    mock_coordinator.api.async_set_value.assert_called_with(CMD_MAP["glycol"], 0)


@pytest.mark.asyncio
async def test_switch_no_cmd_map_entry(mock_coordinator, mock_entry):
    """Test switch behavior when parameter not in CMD_MAP."""
    # This shouldn't happen in practice but test defensive behavior
    switch = RixensSwitch(mock_coordinator, mock_entry, "unknown_param")

    await switch.async_turn_on()

    # Should not call API if parameter not in CMD_MAP
    mock_coordinator.api.async_set_value.assert_not_called()
    mock_coordinator.async_request_refresh.assert_not_called()
