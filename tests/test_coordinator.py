"""Tests for the Rixens coordinator."""
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.rixens.coordinator import RixensDataCoordinator
from custom_components.rixens.const import DOMAIN, CONF_HOST


@pytest.mark.asyncio
async def test_coordinator_initialization(hass):
    """Test coordinator initialization."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "10.0.22.6"},
        entry_id="test_entry",
    )
    
    coordinator = RixensDataCoordinator(
        hass=hass,
        host="10.0.22.6",
        update_interval=timedelta(seconds=30),
        config_entry=mock_entry,
    )
    
    assert coordinator.host == "10.0.22.6"
    assert coordinator.config_entry == mock_entry
    assert coordinator.api is not None


@pytest.mark.asyncio
async def test_coordinator_successful_update(hass):
    """Test successful data update."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "10.0.22.6"},
        entry_id="test_entry",
    )
    
    coordinator = RixensDataCoordinator(
        hass=hass,
        host="10.0.22.6",
        update_interval=timedelta(seconds=30),
        config_entry=mock_entry,
    )
    
    # Mock the API client's async_get_status method
    mock_data = {
        "currenttemp": 720,
        "currenthumidity": 45,
        "setpoint": 680,
        "fanspeed": 50,
    }
    coordinator.api.async_get_status = AsyncMock(return_value=mock_data)
    
    # Trigger an update
    await coordinator.async_refresh()
    
    # Verify data was updated
    assert coordinator.data == mock_data
    assert coordinator.data["currenttemp"] == 720
    assert coordinator.data["currenthumidity"] == 45


@pytest.mark.asyncio
async def test_coordinator_update_failure(hass):
    """Test handling of update failures."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "10.0.22.6"},
        entry_id="test_entry",
    )
    
    coordinator = RixensDataCoordinator(
        hass=hass,
        host="10.0.22.6",
        update_interval=timedelta(seconds=30),
        config_entry=mock_entry,
    )
    
    # Mock the API client to raise an error
    coordinator.api.async_get_status = AsyncMock(
        side_effect=RuntimeError("Connection failed")
    )
    
    # async_refresh catches UpdateFailed and logs it, but doesn't re-raise
    # Instead, we should test _async_update_data directly
    with pytest.raises(UpdateFailed, match="Error updating Rixens data"):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_api_set_value(hass):
    """Test that API set_value method is accessible through coordinator."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "10.0.22.6"},
        entry_id="test_entry",
    )
    
    coordinator = RixensDataCoordinator(
        hass=hass,
        host="10.0.22.6",
        update_interval=timedelta(seconds=30),
        config_entry=mock_entry,
    )
    
    # Mock the API client's async_set_value method
    coordinator.api.async_set_value = AsyncMock(return_value=True)
    
    # Call set_value through coordinator API
    result = await coordinator.api.async_set_value(act=101, val=680)
    
    assert result is True
    coordinator.api.async_set_value.assert_called_once_with(act=101, val=680)
