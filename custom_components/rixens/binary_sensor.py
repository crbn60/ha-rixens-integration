"""Binary sensor platform for Rixens integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import RixensData
from .const import DOMAIN
from .coordinator import RixensCoordinator


@dataclass(frozen=True, kw_only=True)
class RixensBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Rixens binary sensor entity."""

    value_fn: Callable[[RixensData], bool]
    fault_key: str | None = None


BINARY_SENSOR_DESCRIPTIONS: tuple[RixensBinarySensorEntityDescription, ...] = (
    RixensBinarySensorEntityDescription(
        key="flame_failure",
        translation_key="flame_failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Flame Failure",
        value_fn=lambda data: data.heater.faults.get("Flame Failure", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="ignition_failure",
        translation_key="ignition_failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Ignition Failure",
        value_fn=lambda data: data.heater.faults.get("Ignition Failure", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="overheat",
        translation_key="overheat",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Overheat",
        value_fn=lambda data: data.heater.faults.get("Overheat", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="glow_plug_failure",
        translation_key="glow_plug_failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Glow Plug Failure",
        value_fn=lambda data: data.heater.faults.get("Glow Plug Failure", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="voltage_low",
        translation_key="voltage_low",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Voltage Low",
        value_fn=lambda data: data.heater.faults.get("Voltage Low", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="voltage_high",
        translation_key="voltage_high",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Voltage High",
        value_fn=lambda data: data.heater.faults.get("Voltage High", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="sensor_failure",
        translation_key="sensor_failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Sensor Failure",
        value_fn=lambda data: data.heater.faults.get("Sensor Failure", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="pump_failure",
        translation_key="pump_failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Pump Failure",
        value_fn=lambda data: data.heater.faults.get("Pump Failure", 0) != 0,
    ),
    RixensBinarySensorEntityDescription(
        key="motor_failure",
        translation_key="motor_failure",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        fault_key="Motor Failure",
        value_fn=lambda data: data.heater.faults.get("Motor Failure", 0) != 0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rixens binary sensors based on a config entry."""
    coordinator: RixensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        RixensBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class RixensBinarySensor(CoordinatorEntity[RixensCoordinator], BinarySensorEntity):
    """Representation of a Rixens binary sensor."""

    _attr_has_entity_name = True
    entity_description: RixensBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: RixensCoordinator,
        description: RixensBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        if self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
