"""Async API client for the Rixens controller."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from xml.etree import ElementTree as ET

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

STATUS_ENDPOINT = "status.xml"
CONTROL_ENDPOINT = "interface.cgi"


class RixensApiClient:
    def __init__(
        self, host: str, session: aiohttp.ClientSession, timeout: float = 10.0
    ):
        self._host = host.strip().rstrip("/")
        self._session = session
        self._timeout = timeout
        self._lock = asyncio.Lock()

    def _base_url(self) -> str:
        return f"http://{self._host}"

    async def async_get_status(self) -> dict[str, Any]:
        url = f"{self._base_url()}/{STATUS_ENDPOINT}"
        try:
            async with async_timeout.timeout(self._timeout):
                resp = await self._session.get(url)
            resp.raise_for_status()
            text = await resp.text()
        except aiohttp.ClientError as err:
            raise RuntimeError(f"HTTP error fetching status: {err}") from err
        except asyncio.TimeoutError as err:
            raise RuntimeError("Timeout fetching status.xml") from err
        return self._parse_xml(text)

    async def async_set_value(self, act: int, val: int) -> bool:
        url = f"{self._base_url()}/{CONTROL_ENDPOINT}?act={act}&val={val}"
        async with self._lock:
            try:
                async with async_timeout.timeout(self._timeout):
                    resp = await self._session.get(url)
                resp.raise_for_status()
            except aiohttp.ClientError as err:
                _LOGGER.warning("Failed to set act=%s val=%s: %s", act, val, err)
                return False
            except asyncio.TimeoutError:
                _LOGGER.warning("Timeout setting act=%s val=%s", act, val)
                return False
        return True

    def _parse_xml(self, xml_str: str) -> dict[str, Any]:
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as err:
            raise ValueError(f"Invalid XML: {err}") from err

        data: dict[str, Any] = {}

        def recurse(element: ET.Element, prefix: str | None = None):
            for child in element:
                key = f"{prefix}_{child.tag}" if prefix else child.tag
                if len(child):
                    if child.tag in ("heater1-faults", "faults"):
                        for fault in child.findall("fault"):
                            name_el = fault.find("name")
                            val_el = fault.find("value")
                            if name_el is not None and val_el is not None:
                                data[f"fault_{name_el.text.strip()}"] = _coerce(
                                    val_el.text or ""
                                )
                    else:
                        recurse(child, key)
                else:
                    data[key] = _coerce(child.text or "")

        recurse(root)
        return data


def _coerce(value: str) -> Any:
    if value == "":
        return None
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            pass
    return value
