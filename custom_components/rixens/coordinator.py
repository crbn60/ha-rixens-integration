"""DataUpdateCoordinator for Rixens controller."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from aiohttp import ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RixensApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RixensDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Rixens data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        update_interval: timedelta,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self.host = host
        self.session: ClientSession = aiohttp_client.async_get_clientsession(hass)
        self.api = RixensApiClient(host=self.host, session=self.session)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}:{host}",
            update_method=self._async_update_data,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Rixens controller."""
        try:
            return await self.api.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error updating Rixens data: {err}") from err
