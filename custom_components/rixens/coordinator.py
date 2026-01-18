"""DataUpdateCoordinator for Rixens integration."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RixensApi, RixensApiError, RixensData
from .const import (
    BURST_COUNT,
    BURST_INTERVAL,
    CONF_ADAPTIVE_ACTIVE,
    CONF_ADAPTIVE_IDLE,
    CONF_ADAPTIVE_OFF,
    CONF_BURST_MODE,
    CONF_PORT,
    CONF_POLLING_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_ADAPTIVE_ACTIVE,
    DEFAULT_ADAPTIVE_IDLE,
    DEFAULT_ADAPTIVE_OFF,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POLLING_MODE_ADAPTIVE,
    POLLING_MODE_FIXED,
)

_LOGGER = logging.getLogger(__name__)


class RixensCoordinator(DataUpdateCoordinator[RixensData]):
    """Coordinator for Rixens data updates."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self.api = RixensApi(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            session=async_get_clientsession(hass),
        )

        # Polling statistics
        self._total_polls = 0
        self._failed_polls = 0
        self._last_poll_time: datetime | None = None
        self._response_times: list[float] = []

        # Burst mode tracking
        self._burst_remaining = 0
        self._last_user_action: datetime | None = None

        # Initialize coordinator with current interval
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=self._get_update_interval(),
        )

    def _get_update_interval(self) -> timedelta:
        """Get the current update interval based on configuration and state."""
        options = self.config_entry.options
        polling_mode = options.get(CONF_POLLING_MODE, POLLING_MODE_FIXED)

        # Check for burst mode
        if self._burst_remaining > 0:
            return timedelta(seconds=BURST_INTERVAL)

        if polling_mode == POLLING_MODE_FIXED:
            interval = options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            return timedelta(seconds=interval)

        # Adaptive polling mode
        if not self.data:
            # Use active interval until first data fetch
            return timedelta(seconds=options.get(CONF_ADAPTIVE_ACTIVE, DEFAULT_ADAPTIVE_ACTIVE))

        # Determine state based on current data
        if self.data.system_heat:
            # System is actively heating
            interval = options.get(CONF_ADAPTIVE_ACTIVE, DEFAULT_ADAPTIVE_ACTIVE)
        elif (
            self.data.settings.furnace_src == 2
            or self.data.settings.electric_src == 2
        ):
            # System is enabled but idle (not calling for heat)
            interval = options.get(CONF_ADAPTIVE_IDLE, DEFAULT_ADAPTIVE_IDLE)
        else:
            # System is off
            interval = options.get(CONF_ADAPTIVE_OFF, DEFAULT_ADAPTIVE_OFF)

        return timedelta(seconds=interval)

    def trigger_burst_mode(self) -> None:
        """Trigger burst mode for responsive updates after user action."""
        options = self.config_entry.options
        if options.get(CONF_BURST_MODE, True):
            self._burst_remaining = BURST_COUNT
            self._last_user_action = datetime.now()
            self.update_interval = self._get_update_interval()
            _LOGGER.debug("Burst mode activated for %d polls", BURST_COUNT)

    async def _async_update_data(self) -> RixensData:
        """Fetch data from API."""
        start_time = datetime.now()
        self._total_polls += 1

        try:
            data = await self.api.get_status()

            # Record response time
            response_time = (datetime.now() - start_time).total_seconds()
            self._response_times.append(response_time)
            # Keep only last 100 response times
            if len(self._response_times) > 100:
                self._response_times.pop(0)

            self._last_poll_time = datetime.now()

            # Handle burst mode countdown
            if self._burst_remaining > 0:
                self._burst_remaining -= 1
                if self._burst_remaining == 0:
                    _LOGGER.debug("Burst mode completed, returning to normal interval")

            # Update interval if needed (for adaptive polling)
            new_interval = self._get_update_interval()
            if new_interval != self.update_interval:
                self.update_interval = new_interval
                _LOGGER.debug("Update interval changed to %s", new_interval)

            return data
        except RixensApiError as err:
            self._failed_polls += 1
            raise UpdateFailed(f"Error communicating with Rixens device: {err}") from err

    @property
    def polling_stats(self) -> dict[str, Any]:
        """Return polling statistics."""
        avg_response_time = (
            sum(self._response_times) / len(self._response_times)
            if self._response_times
            else 0
        )

        return {
            "total_polls": self._total_polls,
            "failed_polls": self._failed_polls,
            "last_poll": self._last_poll_time,
            "average_response_time": round(avg_response_time, 3),
            "current_interval": self.update_interval.total_seconds() if self.update_interval else None,
            "burst_mode_active": self._burst_remaining > 0,
        }
