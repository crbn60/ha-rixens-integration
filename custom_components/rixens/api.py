"""API client for Rixens devices."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree

import aiohttp

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10


@dataclass
class RixensHeaterData:
    """Heater-specific data from the Rixens device."""

    heat_on: bool
    battery_voltage: float
    runtime: int
    pid_speed: int
    flame_temp: float
    inlet_temp: float
    outlet_temp: float
    altitude: float
    dosing_pump: int
    burner_motor: int
    heater_state: int
    glow_pin: int
    preheat: int
    faults: dict[str, int]


@dataclass
class RixensSettings:
    """Settings data from the Rixens device."""

    setpoint: float  # Temperature in Celsius
    fan_speed: str
    pump_state: bool
    fan_state: bool
    floor_enable: bool
    electric_enable: bool
    engine_enable: bool
    preheat_enable: bool
    aux_enable: bool
    fan_enabled: bool
    therm_enabled: bool
    glycol: bool


@dataclass
class RixensData:
    """Data from the Rixens device."""

    version: str
    heat_version: str
    mode: int
    uptime: int
    system_heat: bool
    heater_state: int
    zone2_state: int
    zone3_state: int
    engine_state: int
    glycol_state: int
    current_temp: float  # Temperature in Celsius
    current_humidity: int
    heater: RixensHeaterData
    settings: RixensSettings


class RixensApiError(Exception):
    """Exception for Rixens API errors."""


class RixensConnectionError(RixensApiError):
    """Exception for connection errors."""


class RixensApi:
    """API client for Rixens devices."""

    def __init__(
        self,
        host: str,
        port: int = 80,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._session = session
        self._base_url = f"http://{host}:{port}" if port != 80 else f"http://{host}"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, path: str) -> str:
        """Make a request to the device."""
        session = await self._get_session()
        url = f"{self._base_url}{path}"
        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
        except asyncio.TimeoutError as err:
            raise RixensConnectionError(f"Timeout connecting to {url}") from err
        except aiohttp.ClientError as err:
            raise RixensConnectionError(f"Error connecting to {url}: {err}") from err

    async def test_connection(self) -> bool:
        """Test the connection to the device."""
        try:
            await self.get_status()
            return True
        except RixensApiError:
            return False

    async def get_status(self) -> RixensData:
        """Get the current status from the device."""
        response = await self._request("/status.xml")
        return self._parse_status(response)

    def _parse_status(self, xml_text: str) -> RixensData:
        """Parse the status XML response."""
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as err:
            raise RixensApiError(f"Failed to parse status XML: {err}") from err

        def get_text(parent: ElementTree.Element, tag: str, default: str = "0") -> str:
            elem = parent.find(tag)
            return elem.text if elem is not None and elem.text else default

        def get_int(parent: ElementTree.Element, tag: str, default: int = 0) -> int:
            try:
                return int(get_text(parent, tag, str(default)))
            except ValueError:
                return default

        def get_float(parent: ElementTree.Element, tag: str, default: float = 0.0) -> float:
            try:
                return float(get_text(parent, tag, str(default)))
            except ValueError:
                return default

        def get_bool(parent: ElementTree.Element, tag: str, default: bool = False) -> bool:
            return get_int(parent, tag, 1 if default else 0) == 1

        # Parse heater1 data
        # Note: All temperatures from API are in tenths of a degree Celsius
        heater1 = root.find("heater1")
        heater_data = RixensHeaterData(
            heat_on=get_bool(heater1, "heaton") if heater1 is not None else False,
            battery_voltage=get_int(heater1, "battv") / 10.0 if heater1 is not None else 0.0,
            runtime=get_int(heater1, "runtime") if heater1 is not None else 0,
            pid_speed=get_int(heater1, "pidspeed") if heater1 is not None else 0,
            flame_temp=get_int(heater1, "flametemp") / 10.0 if heater1 is not None else 0.0,
            inlet_temp=get_int(heater1, "inlettemp") / 10.0 if heater1 is not None else 0.0,
            outlet_temp=get_int(heater1, "outlettemp") / 10.0 if heater1 is not None else 0.0,
            altitude=get_float(heater1, "altitude") if heater1 is not None else 0.0,
            dosing_pump=get_int(heater1, "dosingpump") if heater1 is not None else 0,
            burner_motor=get_int(heater1, "burnermotor") if heater1 is not None else 0,
            heater_state=get_int(heater1, "heaterstate") if heater1 is not None else 0,
            glow_pin=get_int(heater1, "glowpin") if heater1 is not None else 0,
            preheat=get_int(heater1, "preheat") if heater1 is not None else 0,
            faults={},
        )

        # Parse faults
        faults_elem = root.find("heater1-faults")
        if faults_elem is not None:
            for fault in faults_elem.findall("fault"):
                name = get_text(fault, "name", "")
                value = get_int(fault, "value")
                if name:
                    heater_data.faults[name] = value

        # Parse settings
        # Note: setpoint is also in tenths of a degree Celsius
        settings_elem = root.find("settings")
        fan_speed_text = get_text(settings_elem, "fanspeed", "Auto") if settings_elem is not None else "Auto"
        raw_setpoint = get_int(settings_elem, "setpoint", 200) if settings_elem is not None else 200
        settings = RixensSettings(
            setpoint=raw_setpoint / 10.0,
            fan_speed=fan_speed_text,
            pump_state=get_bool(settings_elem, "pumpstate") if settings_elem is not None else False,
            fan_state=get_bool(settings_elem, "fanstate") if settings_elem is not None else False,
            floor_enable=get_bool(settings_elem, "floorenable") if settings_elem is not None else False,
            electric_enable=get_bool(settings_elem, "electricenable") if settings_elem is not None else False,
            engine_enable=get_bool(settings_elem, "engineenable") if settings_elem is not None else False,
            preheat_enable=get_bool(settings_elem, "preheatenable") if settings_elem is not None else False,
            aux_enable=get_bool(settings_elem, "auxenable") if settings_elem is not None else False,
            fan_enabled=get_bool(settings_elem, "fanenabled") if settings_elem is not None else False,
            therm_enabled=get_bool(settings_elem, "thermenabled") if settings_elem is not None else False,
            glycol=get_bool(settings_elem, "glycol") if settings_elem is not None else False,
        )

        return RixensData(
            version=get_text(root, "version", "Unknown"),
            heat_version=get_text(root, "heatversion", "Unknown"),
            mode=get_int(root, "mode"),
            uptime=get_int(root, "uptime"),
            system_heat=get_bool(root, "systemheat"),
            heater_state=get_int(root, "heaterstate"),
            zone2_state=get_int(root, "zone2state"),
            zone3_state=get_int(root, "zone3state"),
            engine_state=get_int(root, "enginestate"),
            glycol_state=get_int(root, "glycolstate"),
            current_temp=get_int(root, "currenttemp") / 10.0,
            current_humidity=get_int(root, "currenthumidity"),
            heater=heater_data,
            settings=settings,
        )

    # Control methods
    async def set_temperature(self, temperature: float) -> None:
        """Set the target temperature in Celsius (converted to tenths for API)."""
        # API expects temperature in tenths of a degree Celsius
        raw_temp = int(temperature * 10)
        await self._request(f"/interface.cgi?act=1&val={raw_temp}")

    async def set_fan_speed(self, speed: int) -> None:
        """Set the fan speed (10-100, or 999 for auto)."""
        await self._request(f"/interface.cgi?act=2&val={speed}")

    async def set_pump(self, on: bool) -> None:
        """Turn the pump on or off."""
        await self._request(f"/interface.cgi?act=4&val={1 if on else 0}")

    async def set_fan(self, on: bool) -> None:
        """Turn the fan on or off."""
        await self._request(f"/interface.cgi?act=5&val={1 if on else 0}")

    async def set_floor_heat(self, on: bool) -> None:
        """Turn floor heat on or off."""
        await self._request(f"/interface.cgi?act=6&val={1 if on else 0}")

    async def set_thermostat(self, on: bool) -> None:
        """Turn thermostat mode on or off."""
        await self._request(f"/interface.cgi?act=8&val={1 if on else 0}")

    async def set_electric_heat(self, on: bool) -> None:
        """Turn electric heat on or off."""
        await self._request(f"/interface.cgi?act=10&val={1 if on else 0}")

    async def set_system_heat(self, on: bool) -> None:
        """Turn the main heating system on or off."""
        await self._request(f"/buttons.cgi?act=20&val={1 if on else 0}")

    async def press_zone_button(self, zone_id: int, mode: int = 0) -> None:
        """Press a zone button."""
        await self._request(f"/buttons.cgi?act=11&id={zone_id}&mode={mode}")

    async def close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None
