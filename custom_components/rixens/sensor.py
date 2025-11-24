"""Sensor platform for Rixens."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICON_MAP, RAW_TEMP_DIVISOR
from .coordinator import RixensDataCoordinator


@dataclass
class SensorDescription:
    key: str
    name: str
    unit_fn: Callable[[Any], str | None] | None = None
    value_fn: Callable[[Any], Any] | None = None
    icon: str | None = None


SENSOR_MAP: list[SensorDescription] = [
    SensorDescription(
        key="currenttemp",
        name="Current Temperature",
        unit_fn=lambda v: UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda v: v / RAW_TEMP_DIVISOR if isinstance(v, (int, float)) else v,
        icon=ICON_MAP.get("currenttemp"),
    ),
    SensorDescription(
        key="currenthumidity",
        name="Current Humidity",
        unit_fn=lambda v: PERCENTAGE,
        icon=ICON_MAP.get("currenthumidity"),
    ),
    SensorDescription(
        key="heaterstate",
        name="Heater State Code",
        icon=ICON_MAP.get("heaterstate"),
    ),
    SensorDescription(
        key="infra_ip",
        name="Infrastructure IP",
        icon=ICON_MAP.get("infra_ip"),
    ),
    SensorDescription(
        key="runtime",
        name="Heater Runtime Seconds",
    ),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensSensor] = []
    data = coordinator.data or {}

    for desc in SENSOR_MAP:
        if desc.key in data:
            entities.append(RixensSensor(coordinator, entry, desc))

    for key, value in data.items():
        if key.startswith("fault_"):
            entities.append(
                RixensSensor(
                    coordinator,
                    entry,
                    SensorDescription(
                        key=key,
                        name=f"Fault {key.removeprefix('fault_').upper()}",
                        icon=ICON_MAP.get("fault"),
                    ),
                )
            )

    async_add_entities(entities)


class RixensSensor(CoordinatorEntity[RixensDataCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: RixensDataCoordinator, entry: ConfigEntry, description: SensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_icon = description.icon

    @property
    def native_value(self) -> Any:
        raw = self.coordinator.data.get(self.entity_description.key)
        if self.entity_description.value_fn:
            try:
                return self.entity_description.value_fn(raw)
            except Exception:
                return raw
        return raw

    @property
    def native_unit_of_measurement(self) -> str | None:
        if self.entity_description.unit_fn:
            return self.entity_description.unit_fn(self.native_value)
        return None
