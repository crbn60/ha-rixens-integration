"""The Rixens integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .coordinator import RixensCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

SERVICE_FORCE_REFRESH = "force_refresh"

SERVICE_FORCE_REFRESH_SCHEMA = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rixens from a config entry."""
    coordinator = RixensCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Register force refresh service
    async def handle_force_refresh(call: ServiceCall) -> None:
        """Handle force refresh service call."""
        entry_id = call.data.get("entry_id")

        if entry_id:
            # Refresh specific entry
            if entry_id in hass.data[DOMAIN]:
                coordinator = hass.data[DOMAIN][entry_id]
                await coordinator.async_request_refresh()
                _LOGGER.info("Forced refresh for entry %s", entry_id)
            else:
                _LOGGER.error("Entry ID %s not found", entry_id)
        else:
            # Refresh all entries
            for coordinator in hass.data[DOMAIN].values():
                await coordinator.async_request_refresh()
            _LOGGER.info("Forced refresh for all Rixens devices")

    # Register service only once
    if not hass.services.has_service(DOMAIN, SERVICE_FORCE_REFRESH):
        hass.services.async_register(
            DOMAIN,
            SERVICE_FORCE_REFRESH,
            handle_force_refresh,
            schema=SERVICE_FORCE_REFRESH_SCHEMA,
        )

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # Update the coordinator's interval without reloading
    coordinator: RixensCoordinator = hass.data[DOMAIN][entry.entry_id]
    new_interval = coordinator._get_update_interval()
    if new_interval != coordinator.update_interval:
        coordinator.update_interval = new_interval
        _LOGGER.info("Update interval changed to %s", new_interval)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
