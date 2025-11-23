import logging
import async_timeout
import aiohttp
import xml.etree.ElementTree as ET
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the Rixens integration."""
    conf = config[DOMAIN]
    # Initialize API client with an aiohttp session
    api = RixensApiClient(
        aiohttp.ClientSession(), conf["data_url"], conf["control_url"]
    )

    # Initialize the coordinator for scheduled data fetching
    coordinator = RixensCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN] = coordinator

    # Load platforms (sensors, numbers, switches)
    for platform in ["sensor", "number", "switch"]:
        hass.helpers.discovery.load_platform(platform, DOMAIN, {}, config)
    return True


class RixensApiClient:
    """Handles communication with the Rixens web interface."""

    def __init__(self, session, data_url, control_url):
        self.session = session
        self.data_url = data_url
        self.control_url = control_url

    async def fetch_data(self):
        """Fetches status.xml and parses it."""
        async with async_timeout.timeout(10):
            # Fetch the XML data
            resp = await self.session.get(self.data_url)
            resp.raise_for_status()  # Raise error for bad HTTP status codes
            text = await resp.text()
            return self._parse_xml(text)

    async def set_parameter(self, action_id, value):
        """Sends control command via interface.cgi?act=ID&val=VALUE."""
        params = {"act": action_id, "val": int(value)}
        async with self.session.get(self.control_url, params=params) as resp:
            resp.raise_for_status()

    def _parse_xml(self, xml_string):
        """Parses the XML string into a flattened dictionary."""
        root = ET.fromstring(xml_string)
        data = {}

        # 1. Top-level items
        for key in ["systemheat", "currenttemp", "currenthumidity", "uptime"]:
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

    def __init__(self, hass, api):
        # Renamed the coordinator name
        super().__init__(
            hass, _LOGGER, name="Rixens", update_interval=timedelta(seconds=30)
        )
        self.api = api

    async def _async_update_data(self):
        """Functon called by the update coordinator to fetch data."""
        try:
            return await self.api.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error: {err}")
