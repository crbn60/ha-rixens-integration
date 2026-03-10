"""Tests for the Rixens API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.rixens.api import (
    RixensApi,
    RixensApiError,
    RixensConnectionError,
    RixensData,
    RixensHeaterData,
    RixensSettings,
)

from .conftest import SAMPLE_XML


# ---------------------------------------------------------------------------
# Construction & URL building
# ---------------------------------------------------------------------------


class TestRixensApiInit:
    """Tests for RixensApi initialization."""

    def test_default_port(self):
        api = RixensApi(host="192.168.1.1")
        assert api._base_url == "http://192.168.1.1"

    def test_port_80_no_port_in_url(self):
        api = RixensApi(host="192.168.1.1", port=80)
        assert api._base_url == "http://192.168.1.1"

    def test_custom_port(self):
        api = RixensApi(host="192.168.1.1", port=8080)
        assert api._base_url == "http://192.168.1.1:8080"

    def test_session_stored(self):
        session = MagicMock(spec=aiohttp.ClientSession)
        api = RixensApi(host="192.168.1.1", session=session)
        assert api._session is session

    def test_session_none_by_default(self):
        api = RixensApi(host="192.168.1.1")
        assert api._session is None


# ---------------------------------------------------------------------------
# _get_session
# ---------------------------------------------------------------------------


class TestGetSession:
    """Tests for lazy session creation."""

    async def test_creates_session_if_none(self):
        api = RixensApi(host="192.168.1.1")
        session = await api._get_session()
        assert isinstance(session, aiohttp.ClientSession)
        await session.close()

    async def test_reuses_existing_session(self):
        session = aiohttp.ClientSession()
        api = RixensApi(host="192.168.1.1", session=session)
        result = await api._get_session()
        assert result is session
        await session.close()


# ---------------------------------------------------------------------------
# _request & retry logic
# ---------------------------------------------------------------------------


class TestRequest:
    """Tests for HTTP request handling with retries."""

    async def test_successful_request(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", body=SAMPLE_XML)
            api = RixensApi(host="192.168.1.1")
            result = await api._request("/status.xml")
            assert "<version>" in result
            await api.close()

    async def test_timeout_raises_connection_error(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            api = RixensApi(host="192.168.1.1")
            with pytest.raises(RixensConnectionError, match="Timeout"):
                await api._request("/status.xml")
            await api.close()

    async def test_client_error_raises_connection_error(self):
        with aioresponses() as m:
            exc = aiohttp.ClientError("connection refused")
            m.get("http://192.168.1.1/status.xml", exception=exc)
            m.get("http://192.168.1.1/status.xml", exception=exc)
            m.get("http://192.168.1.1/status.xml", exception=exc)
            api = RixensApi(host="192.168.1.1")
            with pytest.raises(RixensConnectionError, match="Error connecting"):
                await api._request("/status.xml")
            await api.close()

    async def test_retry_then_success(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            m.get("http://192.168.1.1/status.xml", body="<ok/>")
            api = RixensApi(host="192.168.1.1")
            result = await api._request("/status.xml")
            assert result == "<ok/>"
            await api.close()

    async def test_no_retry_when_disabled(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            api = RixensApi(host="192.168.1.1")
            with pytest.raises(RixensConnectionError):
                await api._request("/status.xml", retry=False)
            await api.close()

    async def test_http_error_status(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", status=500)
            m.get("http://192.168.1.1/status.xml", status=500)
            m.get("http://192.168.1.1/status.xml", status=500)
            api = RixensApi(host="192.168.1.1")
            with pytest.raises(RixensConnectionError):
                await api._request("/status.xml")
            await api.close()


# ---------------------------------------------------------------------------
# test_connection
# ---------------------------------------------------------------------------


class TestTestConnection:
    """Tests for the test_connection method."""

    async def test_returns_true_on_success(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", body=SAMPLE_XML)
            api = RixensApi(host="192.168.1.1")
            assert await api.test_connection() is True
            await api.close()

    async def test_returns_false_on_failure(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            m.get("http://192.168.1.1/status.xml", exception=asyncio.TimeoutError())
            api = RixensApi(host="192.168.1.1")
            assert await api.test_connection() is False
            await api.close()


# ---------------------------------------------------------------------------
# get_status & _parse_status
# ---------------------------------------------------------------------------


class TestParseStatus:
    """Tests for XML parsing."""

    def _parse(self, xml: str) -> RixensData:
        api = RixensApi(host="192.168.1.1")
        return api._parse_status(xml)

    def test_parses_sample_xml(self):
        data = self._parse(SAMPLE_XML)
        assert data.version == "HW2-1.205 2025_11_20 RIXENS"
        assert data.heat_version == "1.06 2025-11-21 PID"
        assert data.mode == 1
        assert data.uptime == 146691
        assert data.system_heat is True
        assert data.heater_state == 20
        assert data.current_temp == 17.1
        assert data.current_humidity == 14.5

    def test_heater_data(self):
        data = self._parse(SAMPLE_XML)
        h = data.heater
        assert h.heat_on is True
        assert h.battery_voltage == 12.5
        assert h.runtime == 114236
        assert h.pid_speed == 73
        assert h.flame_temp == 145.25
        assert h.inlet_temp == 70.75
        assert h.outlet_temp == 73.0
        assert h.atmospheric_pressure == 997.2
        assert h.dosing_pump == 1.6
        assert h.burner_motor == 3532
        assert h.glow_pin == 0
        assert h.preheat == 0

    def test_faults(self):
        data = self._parse(SAMPLE_XML)
        assert "AF" in data.heater.faults
        assert data.heater.faults["AF"] == 0
        assert "F1" in data.heater.faults

    def test_settings(self):
        data = self._parse(SAMPLE_XML)
        s = data.settings
        assert s.setpoint == 18.0
        assert s.fan_speed == "Auto"
        assert s.pump_state is True
        assert s.fan_state is True
        assert s.floor_enable is True
        assert s.electric_enable is True
        assert s.furnace_src == 2
        assert s.electric_src == 0
        assert s.engine_src == 0
        assert s.floor_src == 2

    def test_invalid_xml_raises_api_error(self):
        with pytest.raises(RixensApiError, match="Failed to parse"):
            self._parse("not xml at all <<<")

    def test_missing_heater1_element(self):
        xml = "<response><version>1.0</version><currenttemp>200</currenttemp></response>"
        data = self._parse(xml)
        assert data.heater.heat_on is False
        assert data.heater.battery_voltage == 0.0
        assert data.current_temp == 20.0

    def test_missing_settings_element(self):
        xml = "<response><version>1.0</version></response>"
        data = self._parse(xml)
        assert data.settings.setpoint == 20.0
        assert data.settings.fan_speed == "Auto"
        assert data.settings.furnace_src == 0

    def test_empty_text_defaults(self):
        xml = """<response>
        <version></version>
        <currenttemp></currenttemp>
        <heater1><heaton></heaton><battv></battv></heater1>
        <settings><setpoint></setpoint></settings>
        </response>"""
        data = self._parse(xml)
        assert data.version == "Unknown"  # empty text triggers default
        assert data.current_temp == 0.0

    async def test_get_status_integration(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/status.xml", body=SAMPLE_XML)
            api = RixensApi(host="192.168.1.1")
            data = await api.get_status()
            assert isinstance(data, RixensData)
            assert data.version == "HW2-1.205 2025_11_20 RIXENS"
            await api.close()


# ---------------------------------------------------------------------------
# Control methods
# ---------------------------------------------------------------------------


class TestControlMethods:
    """Tests for device control methods."""

    async def test_set_temperature(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=1&val=225", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_temperature(22.5)
            await api.close()

    async def test_set_fan_speed(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=2&val=50", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_fan_speed(50)
            await api.close()

    async def test_set_fan_speed_auto(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=2&val=999", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_fan_speed(999)
            await api.close()

    async def test_set_furnace_on(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=5&val=1", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_furnace(True)
            await api.close()

    async def test_set_furnace_off(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=5&val=0", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_furnace(False)
            await api.close()

    async def test_set_floor_heat_on(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=10&val=1", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_floor_heat(True)
            await api.close()

    async def test_set_floor_heat_off(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=10&val=0", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_floor_heat(False)
            await api.close()

    async def test_set_fan_on(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=8&val=1", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_fan(True)
            await api.close()

    async def test_set_fan_off(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=8&val=0", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_fan(False)
            await api.close()

    async def test_set_electric_heat_on(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=4&val=1", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_electric_heat(True)
            await api.close()

    async def test_set_electric_heat_off(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=4&val=0", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_electric_heat(False)
            await api.close()

    async def test_set_continuous_heat_on(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=6&val=1", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_continuous_heat(True)
            await api.close()

    async def test_set_continuous_heat_off(self):
        with aioresponses() as m:
            m.get("http://192.168.1.1/interface.cgi?act=6&val=0", body="OK")
            api = RixensApi(host="192.168.1.1")
            await api.set_continuous_heat(False)
            await api.close()


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


class TestClose:
    """Tests for session cleanup."""

    async def test_close_with_session(self):
        api = RixensApi(host="192.168.1.1")
        # Create a session first
        await api._get_session()
        assert api._session is not None
        await api.close()
        assert api._session is None

    async def test_close_without_session(self):
        api = RixensApi(host="192.168.1.1")
        await api.close()
        assert api._session is None
