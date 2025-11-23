# custom_components/rixens/__init__.py

import logging
import async_timeout
import aiohttp
import xml.etree.ElementTree as ET
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, UPDATE_INTERVAL, RIXENS_URL
import yarl  # Added yarl for robust URL joining

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "number", "switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Rixens integration from YAML (only for legacy/discovery)."""
    # Support legacy YAML config for local development/tests.
    conf = config.get(DOMAIN)
    if not conf:
        return True

    # Accept either `rixens_url` (base) or `data_url`/`control_url` from README/tests
    base = None
    if conf.get(RIXENS_URL):
        base = conf.get(RIXENS_URL).rstrip("/")
    else:
        data_url = conf.get("data_url") or conf.get("control_url")
        if data_url:
            base = data_url.rsplit("/", 1)[0].rstrip("/")

    if not base:
        return True

    session = aiohttp.ClientSession()
    api = RixensApiClient(session, base)
    # Allow YAML config to override polling interval using `update_interval` (seconds)
    yaml_interval = None
    try:
        yaml_interval = (
            int(conf.get("update_interval"))
            if conf.get("update_interval") is not None
            else None
        )
    except Exception:
        yaml_interval = None

    coordinator = RixensCoordinator(hass, api, update_interval_seconds=yaml_interval)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Initial refresh failed (YAML): %s", err)
        await session.close()
        return False

    # For legacy YAML keep a single coordinator available at hass.data[DOMAIN]
    hass.data[DOMAIN] = coordinator

    # Load platforms which will pick up hass.data[DOMAIN]
    for p in PLATFORMS:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(p, DOMAIN, {}, config)
        )
        return True

    async def async_setup(hass: HomeAssistant, config: dict):
        """Legacy YAML setup is no longer supported. Use config entry only."""
        return True

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Rixens from a config entry."""
    # Retrieve the single base URL
    base_url = entry.data[RIXENS_URL].rstrip("/")

    # Initialize API client with an aiohttp session
    session = aiohttp.ClientSession()
    api = RixensApiClient(session, base_url)

    # Initialize the coordinator for scheduled data fetching
    # Read configured update interval (seconds) from entry.options if present
    entry_interval = entry.options.get("update_interval", None)
    try:
        entry_interval = int(entry_interval) if entry_interval is not None else None
    except Exception:
        entry_interval = None

    coordinator = RixensCoordinator(hass, api, update_interval_seconds=entry_interval)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Initial refresh failed: %s", err)
        await session.close()
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.session.close()
    return unload_ok


class RixensApiClient:
    """Handles communication with the Rixens web interface."""

    def __init__(self, session, base_url):
        self.session = session
        # Use yarl to safely handle URL construction regardless of trailing slashes
        self._base_url = yarl.URL(base_url)

    @property
    def data_url(self):
        """Constructs the full status URL."""
        return str(self._base_url / "status.xml")

    @property
    def control_url(self):
        """Constructs the full control URL."""
        return str(self._base_url / "interface.cgi")

    async def fetch_data(self):
        """Fetches status.xml and parses it."""
        async with async_timeout.timeout(10):
            # Use the constructed data_url
            resp = await self.session.get(self.data_url)
            resp.raise_for_status()
            text = await resp.text()
            return self._parse_xml(text)

    async def set_parameter(self, action_id, value):
        """Sends control command via interface.cgi?act=ID&val=VALUE."""
        params = {"act": action_id, "val": int(value)}
        # Use the constructed control_url
        async with self.session.get(self.control_url, params=params) as resp:
            resp.raise_for_status()

    def _parse_xml(self, xml_string):
        """Parses the XML string into a flattened dictionary."""
        root = ET.fromstring(xml_string)
        data = {}

        # 1. Top-level items
        for key in [
            "version",
            "systemheat",
            "currenttemp",
            "currenthumidity",
            "uptime",
        ]:
            node = root.find(key)
            if node is not None:
                data[key] = node.text

        # 2. Nested items (heater1)
        heater = root.find("heater1")
        if heater:
            for k in ["battv", "flametemp"]:
                node = heater.find(k)
                if node is not None:
                    data[k] = node.text

        # 3. Nested items (settings)
        settings = root.find("settings")
        if settings:
            for k in ["setpoint", "fanspeed", "floorenable"]:
                node = settings.find(k)
                if node is not None:
                    data[k] = node.text
        return data


class RixensCoordinator(DataUpdateCoordinator):
    """Manages scheduling and fetching data from the API."""

    def __init__(self, hass, api, update_interval_seconds: int | None = None):
        """Create a coordinator.

        If `update_interval_seconds` is provided and is an integer, it will be
        used as the polling interval in seconds. Otherwise falls back to
        `const.UPDATE_INTERVAL`.
        """
        if update_interval_seconds is None:
            interval_seconds = UPDATE_INTERVAL
        else:
            try:
                interval_seconds = int(update_interval_seconds)
            except Exception:
                interval_seconds = UPDATE_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name="Rixens",
            update_interval=timedelta(seconds=interval_seconds),
        )
        self.api = api

    async def _async_update_data(self):
        """Functon called by the update coordinator to fetch data."""
        try:
            return await self.api.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error: {err}")
