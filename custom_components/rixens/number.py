"""Number platform for Rixens (setpoint, fanspeed)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CMD_MAP, ICON_MAP
from .coordinator import RixensDataCoordinator

NUMBER_ENTITIES = {
    "setpoint": {"name": "Setpoint", "min": 90, "max": 220, "step": 1, "icon": ICON_MAP.get("setpoint")},
    "fanspeed": {"name": "Fan Speed", "min": 0, "max": 100, "step": 1, "icon": ICON_MAP.get("fanspeed")},
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensNumber] = []

    for key, meta in NUMBER_ENTITIES.items():
        if key in coordinator.data:
            entities.append(RixensNumber(coordinator, entry, key, meta))

    async_add_entities(entities)


class RixensNumber(CoordinatorEntity[RixensDataCoordinator], NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: RixensDataCoordinator, entry: ConfigEntry, key: str, meta: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = meta["name"]
        self._attr_icon = meta.get("icon")
        self._attr_native_min_value = meta["min"]
        self._attr_native_max_value = meta["max"]
        self._attr_native_step = meta["step"]

    @property
    def native_value(self) -> float | None:
        val = self.coordinator.data.get(self._key)
        if isinstance(val, (int, float)):
            return float(val)
        return None

    async def async_set_native_value(self, value: float) -> None:
        act = CMD_MAP.get(self._key)
        if act is None:
            return
        if await self.coordinator.api.async_set_value(act, int(value)):
            await self.coordinator.async_request_refresh()