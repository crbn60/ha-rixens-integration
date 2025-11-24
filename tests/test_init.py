"""Tests for the Rixens integration initialization."""

import pytest
from aioresponses import aioresponses
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.rixens.const import CONF_HOST, DOMAIN

MOCK_STATUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<status>
    <currenttemp>720</currenttemp>
    <currenthumidity>45</currenthumidity>
    <setpoint>680</setpoint>
    <fanspeed>50</fanspeed>
    <engineenable>1</engineenable>
    <electricenable>0</electricenable>
</status>
"""


@pytest.mark.asyncio
async def test_coordinator_refresh_with_mocked_response(hass):
    """Test coordinator refresh with mocked API responses."""
    from datetime import timedelta

    from custom_components.rixens.coordinator import RixensDataCoordinator

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Rixens MCS7 (10.0.22.6)",
        data={CONF_HOST: "10.0.22.6"},
        options={"poll_interval": 30},
        unique_id="10.0.22.6",
        entry_id="test_entry_id",
    )

    # Create coordinator
    coordinator = RixensDataCoordinator(
        hass=hass,
        host="10.0.22.6",
        update_interval=timedelta(seconds=30),
        config_entry=entry,
    )

    # Mock the HTTP response
    with aioresponses() as mock:
        mock.get("http://10.0.22.6/status.xml", status=200, body=MOCK_STATUS_XML)

        # Perform refresh (not first_refresh as that requires specific entry state)
        await coordinator.async_refresh()

        # Verify data was loaded
        assert coordinator.data is not None
        assert coordinator.data["currenttemp"] == 720
        assert coordinator.data["setpoint"] == 680


@pytest.mark.asyncio
async def test_async_setup(hass):
    """Test async_setup returns True (YAML config not supported)."""
    from custom_components.rixens import async_setup

    result = await async_setup(hass, {})
    assert result is True
