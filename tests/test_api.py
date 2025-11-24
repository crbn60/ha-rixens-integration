"""Tests for the Rixens API client."""

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.rixens.api import RixensApiClient

MOCK_STATUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<status>
    <currenttemp>720</currenttemp>
    <currenthumidity>45</currenthumidity>
    <heaterstate>3</heaterstate>
    <setpoint>680</setpoint>
    <fanspeed>50</fanspeed>
    <engineenable>1</engineenable>
    <electricenable>0</electricenable>
    <floorenable>1</floorenable>
    <fanenabled>1</fanenabled>
    <thermenabled>1</thermenabled>
    <infra_ip>192.168.1.100</infra_ip>
    <runtime>12345</runtime>
    <faults>
        <fault>
            <name>overtemp</name>
            <value>0</value>
        </fault>
        <fault>
            <name>flame</name>
            <value>0</value>
        </fault>
    </faults>
</status>
"""


@pytest.mark.asyncio
async def test_async_get_status_success():
    """Test successful status fetch and XML parsing."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/status.xml", status=200, body=MOCK_STATUS_XML)

            result = await client.async_get_status()

            # Verify parsed data
            assert result["currenttemp"] == 720
            assert result["currenthumidity"] == 45
            assert result["heaterstate"] == 3
            assert result["setpoint"] == 680
            assert result["fanspeed"] == 50
            assert result["engineenable"] == 1
            assert result["electricenable"] == 0
            assert result["floorenable"] == 1
            assert result["fanenabled"] == 1
            assert result["thermenabled"] == 1
            assert result["infra_ip"] == "192.168.1.100"
            assert result["runtime"] == 12345
            assert result["fault_overtemp"] == 0
            assert result["fault_flame"] == 0


@pytest.mark.asyncio
async def test_async_get_status_empty_values():
    """Test XML parsing with empty values."""
    xml_with_empty = """<?xml version="1.0" encoding="UTF-8"?>
<status>
    <currenttemp>720</currenttemp>
    <currenthumidity></currenthumidity>
    <heaterstate>3</heaterstate>
</status>
"""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/status.xml", status=200, body=xml_with_empty)

            result = await client.async_get_status()

            assert result["currenttemp"] == 720
            assert result["currenthumidity"] is None
            assert result["heaterstate"] == 3


@pytest.mark.asyncio
async def test_async_get_status_nested_elements():
    """Test XML parsing with nested elements."""
    xml_nested = """<?xml version="1.0" encoding="UTF-8"?>
<status>
    <heater>
        <temp>720</temp>
        <state>3</state>
    </heater>
</status>
"""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/status.xml", status=200, body=xml_nested)

            result = await client.async_get_status()

            # Nested elements should be flattened with prefix
            assert result["heater_temp"] == 720
            assert result["heater_state"] == 3


@pytest.mark.asyncio
async def test_async_get_status_http_error():
    """Test handling of HTTP errors."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/status.xml", status=500)

            with pytest.raises(RuntimeError, match="HTTP error fetching status"):
                await client.async_get_status()


@pytest.mark.asyncio
async def test_async_get_status_invalid_xml():
    """Test handling of invalid XML."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get(
                "http://10.0.22.6/status.xml", status=200, body="Not valid XML {{{"
            )

            with pytest.raises(ValueError, match="Invalid XML"):
                await client.async_get_status()


@pytest.mark.asyncio
async def test_async_get_status_timeout():
    """Test handling of timeout."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session, timeout=0.1)

        with aioresponses() as mock:
            # Simulate timeout by not responding
            mock.get("http://10.0.22.6/status.xml", exception=TimeoutError())

            with pytest.raises(RuntimeError, match="Timeout fetching status.xml"):
                await client.async_get_status()


@pytest.mark.asyncio
async def test_async_set_value_success():
    """Test successful value setting."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/interface.cgi?act=101&val=680", status=200)

            result = await client.async_set_value(act=101, val=680)

            assert result is True


@pytest.mark.asyncio
async def test_async_set_value_http_error():
    """Test handling of HTTP errors when setting value."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/interface.cgi?act=101&val=680", status=500)

            result = await client.async_set_value(act=101, val=680)

            # Should return False on error, not raise
            assert result is False


@pytest.mark.asyncio
async def test_async_set_value_timeout():
    """Test handling of timeout when setting value."""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session, timeout=0.1)

        with aioresponses() as mock:
            mock.get(
                "http://10.0.22.6/interface.cgi?act=101&val=680",
                exception=TimeoutError(),
            )

            result = await client.async_set_value(act=101, val=680)

            # Should return False on timeout, not raise
            assert result is False


@pytest.mark.asyncio
async def test_host_normalization():
    """Test that host is properly normalized."""
    async with aiohttp.ClientSession() as session:
        # Test with trailing slash
        client = RixensApiClient(host="10.0.22.6/", session=session)
        assert client._base_url() == "http://10.0.22.6"

        # Test with whitespace
        client = RixensApiClient(host="  10.0.22.6  ", session=session)
        assert client._base_url() == "http://10.0.22.6"


@pytest.mark.asyncio
async def test_value_coercion():
    """Test that values are properly coerced to int/float."""
    xml_types = """<?xml version="1.0" encoding="UTF-8"?>
<status>
    <integer>42</integer>
    <float>3.14</float>
    <string>hello</string>
    <empty></empty>
</status>
"""
    async with aiohttp.ClientSession() as session:
        client = RixensApiClient(host="10.0.22.6", session=session)

        with aioresponses() as mock:
            mock.get("http://10.0.22.6/status.xml", status=200, body=xml_types)

            result = await client.async_get_status()

            assert result["integer"] == 42
            assert isinstance(result["integer"], int)
            assert result["float"] == 3.14
            assert isinstance(result["float"], float)
            assert result["string"] == "hello"
            assert isinstance(result["string"], str)
            assert result["empty"] is None
