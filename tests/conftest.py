"""Pytest configuration for Rixens tests."""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry


pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield
