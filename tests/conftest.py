"""Pytest configuration for Rixens tests."""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry


pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
async def mock_aiohttp_session(hass):
    """Get the aiohttp session from hass to avoid thread cleanup issues."""
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    return async_get_clientsession(hass)
