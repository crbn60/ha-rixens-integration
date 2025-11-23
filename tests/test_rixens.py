# tests/test_rixen.py
from unittest.mock import patch
import pytest
from aioresponses import aioresponses

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_ON, STATE_OFF
from custom_components.rixen_heater.const import DOMAIN

# Constants for our mock
MOCK_CONFIG = {
    "data_url": "http://192.168.1.50/status.xml",
    "control_url": "http://192.168.1.50/interface.cgi"
}

@pytest.mark.asyncio
async def test_sensor_creation_and_values(hass: HomeAssistant, mock_status_xml):
    """Test that entities are created and populated from XML."""
    
    # 1. Mock the HTTP response for the status.xml
    with aioresponses() as m:
        m.get("http://192.168.1.50/status.xml", body=mock_status_xml)

        # 2. Setup the integration
        from custom_components.rixen_heater import async_setup
        
        # We manually trigger the setup
        assert await async_setup(hass, {DOMAIN: MOCK_CONFIG})
        await hass.async_block_till_done()

        # 3. Verify Sensor States
        # Check Temperature (145 -> 14.5 based on logic)
        state_temp = hass.states.get("sensor.device_current_temp")
        assert state_temp is not None
        assert state_temp.state == "14.5"
        
        # Check Voltage (128 -> 12.8)
        state_batt = hass.states.get("sensor.device_battery_voltage")
        assert state_batt.state == "12.8"

        # Check Switch (systemheat=1 -> 'on')
        state_switch = hass.states.get("switch.system_heat")
        assert state_switch.state == STATE_ON

@pytest.mark.asyncio
async def test_number_control(hass: HomeAssistant, mock_status_xml):
    """Test that changing a number entity sends the correct API command."""
    
    with aioresponses() as m:
        # Mock the initial status fetch
        m.get("http://192.168.1.50/status.xml", body=mock_status_xml)
        
        # Setup integration
        from custom_components.rixen_heater import async_setup
        await async_setup(hass, {DOMAIN: MOCK_CONFIG})
        await hass.async_block_till_done()

        # Mock the Control URL response
        # We expect a call to /interface.cgi?act=1&val=150 (Setpoint ID=1)
        m.get("http://192.168.1.50/interface.cgi?act=1&val=150", body="OK")
        
        # Mock the refresh status call that happens immediately after
        m.get("http://192.168.1.50/status.xml", body=mock_status_xml)

        # 4. Perform the Action: Set temperature to 150
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": "number.device_target_temperature", "value": 150},
            blocking=True,
        )

        # 5. Assert the URL was called
        # 'm.requests' contains all calls made. We search for the one with our params.
        key = ("GET", "http://192.168.1.50/interface.cgi?act=1&val=150")
        assert key in m.requests