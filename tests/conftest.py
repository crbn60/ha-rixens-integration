"""Pytest configuration for Rixens tests."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.rixens.const import CONF_HOST, CONF_POLL_INTERVAL, DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.1.100"},
        options={CONF_POLL_INTERVAL: 15},
        entry_id="test_entry_id",
        unique_id="192.168.1.100",
    )
