"""Switch platform for Rixens (enable/disable sources)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CMD_MAP, ICON_MAP
from .coordinator import RixensDataCoordinator

SWITCH_KEYS = ["engineenable", "electricenable", "floorenable", "fanenabled", "thermenabled"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensSwitch] = []

    for key in SWITCH_KEYS:
        if key in coordinator.data:
            entities.append(RixensSwitch(coordinator, entry, key))

    async_add_entities(entities)


class RixensSwitch(CoordinatorEntity[RixensDataCoordinator], SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: RixensDataCoordinator, entry: ConfigEntry, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = key
        self._attr_icon = ICON_MAP.get(key)

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._key))

    async def async_turn_on(self, **kwargs: Any) -> None:
        act = CMD_MAP.get(self._key)
        if act is not None and await self.coordinator.api.async_set_value(act, 1):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        act = CMD_MAP.get(self._key)
        if act is not None and await self.coordinator.api.async_set_value(act, 0):
            await self.coordinator.async_request_refresh()