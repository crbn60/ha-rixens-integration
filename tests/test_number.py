"""Tests for Rixens number entities."""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.rixens.const import CMD_MAP
from custom_components.rixens.number import NUMBER_ENTITIES, RixensNumber


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = {
        "setpoint": 180,
        "fanspeed": 75,
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
async def test_number_native_value(mock_coordinator, mock_entry):
    """Test number native_value property."""
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    assert number.native_value == 180.0


@pytest.mark.asyncio
async def test_number_native_value_float(mock_coordinator, mock_entry):
    """Test number native_value with float input."""
    mock_coordinator.data["fanspeed"] = 75.5
    meta = NUMBER_ENTITIES["fanspeed"]
    number = RixensNumber(mock_coordinator, mock_entry, "fanspeed", meta)

    assert number.native_value == 75.5


@pytest.mark.asyncio
async def test_number_native_value_none(mock_coordinator, mock_entry):
    """Test number native_value when data is None."""
    mock_coordinator.data["setpoint"] = None
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    assert number.native_value is None


@pytest.mark.asyncio
async def test_number_set_native_value(mock_coordinator, mock_entry):
    """Test setting number value."""
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    await number.async_set_native_value(200.0)

    mock_coordinator.api.async_set_value.assert_called_once_with(
        CMD_MAP["setpoint"], 200
    )
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_number_set_native_value_decimal(mock_coordinator, mock_entry):
    """Test setting number value with decimal (should be truncated to int)."""
    meta = NUMBER_ENTITIES["fanspeed"]
    number = RixensNumber(mock_coordinator, mock_entry, "fanspeed", meta)

    await number.async_set_native_value(85.7)

    # Value should be converted to int
    mock_coordinator.api.async_set_value.assert_called_once_with(
        CMD_MAP["fanspeed"], 85
    )
    mock_coordinator.async_request_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_number_set_value_failure(mock_coordinator, mock_entry):
    """Test setting number value when API call fails."""
    mock_coordinator.api.async_set_value.return_value = False
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    await number.async_set_native_value(150.0)

    mock_coordinator.api.async_set_value.assert_called_once()
    # Refresh should not be called on failure
    mock_coordinator.async_request_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_number_unique_id(mock_coordinator, mock_entry):
    """Test number unique ID generation."""
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    assert number.unique_id == "test_entry_123_setpoint"


@pytest.mark.asyncio
async def test_number_name(mock_coordinator, mock_entry):
    """Test number entity name."""
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    assert number.name == "Setpoint"


@pytest.mark.asyncio
async def test_number_min_max_step(mock_coordinator, mock_entry):
    """Test number min, max, and step values."""
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    assert number.native_min_value == 90
    assert number.native_max_value == 220
    assert number.native_step == 1


@pytest.mark.asyncio
async def test_fanspeed_min_max_step(mock_coordinator, mock_entry):
    """Test fanspeed min, max, and step values."""
    meta = NUMBER_ENTITIES["fanspeed"]
    number = RixensNumber(mock_coordinator, mock_entry, "fanspeed", meta)

    assert number.native_min_value == 0
    assert number.native_max_value == 100
    assert number.native_step == 1


@pytest.mark.asyncio
async def test_all_number_keys_in_cmd_map():
    """Test that all number entity keys have CMD_MAP entries."""
    for key in NUMBER_ENTITIES.keys():
        assert key in CMD_MAP, f"Number entity key '{key}' not found in CMD_MAP"


@pytest.mark.asyncio
async def test_number_set_no_cmd_map_entry(mock_coordinator, mock_entry):
    """Test number behavior when parameter not in CMD_MAP."""
    # Create a number entity with a meta that references a non-existent CMD_MAP entry
    meta = {"name": "Test", "min": 0, "max": 100, "step": 1}
    number = RixensNumber(mock_coordinator, mock_entry, "unknown_param", meta)

    await number.async_set_native_value(50.0)

    # Should not call API or refresh if parameter not in CMD_MAP
    mock_coordinator.api.async_set_value.assert_not_called()
    mock_coordinator.async_request_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_number_boundary_values(mock_coordinator, mock_entry):
    """Test setting boundary values for number entities."""
    meta = NUMBER_ENTITIES["setpoint"]
    number = RixensNumber(mock_coordinator, mock_entry, "setpoint", meta)

    # Test minimum value
    await number.async_set_native_value(90.0)
    mock_coordinator.api.async_set_value.assert_called_with(CMD_MAP["setpoint"], 90)

    mock_coordinator.api.async_set_value.reset_mock()

    # Test maximum value
    await number.async_set_native_value(220.0)
    mock_coordinator.api.async_set_value.assert_called_with(CMD_MAP["setpoint"], 220)
