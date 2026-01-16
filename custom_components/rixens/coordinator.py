"""DataUpdateCoordinator for Rixens integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RixensApi, RixensApiError, RixensData
from .const import CONF_PORT, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)


class RixensCoordinator(DataUpdateCoordinator[RixensData]):
    """Coordinator for Rixens data updates."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.config_entry = entry
        self.api = RixensApi(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            session=async_get_clientsession(hass),
        )

    async def _async_update_data(self) -> RixensData:
        """Fetch data from API."""
        try:
            return await self.api.get_status()
        except RixensApiError as err:
            raise UpdateFailed(f"Error communicating with Rixens device: {err}") from err
