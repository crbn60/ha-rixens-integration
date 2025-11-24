"""Sensor platform for Rixens."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RixensDataCoordinator
from .entity_config import (
    DeviceClass,
    EntityType,
    get_entities_by_type,
    get_fault_entity_config,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Rixens sensor entities."""
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensSensor] = []
    data = coordinator.data or {}

    # Get all sensor configurations from entity_config
    sensor_configs = get_entities_by_type(EntityType.SENSOR)

    # Create entities for configured sensors that exist in data
    for key, config in sensor_configs.items():
        if key in data:
            entities.append(RixensSensor(coordinator, entry, config))

    # Create dynamic fault sensors
    for key in data.keys():
        if key.startswith("fault_"):
            fault_name = key.removeprefix("fault_")
            fault_config = get_fault_entity_config(fault_name)
            entities.append(RixensSensor(coordinator, entry, fault_config))

    async_add_entities(entities)


class RixensSensor(CoordinatorEntity[RixensDataCoordinator], SensorEntity):
    """Rixens sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: RixensDataCoordinator, entry: ConfigEntry, config
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{config.key}"
        self._attr_name = config.name
        self._attr_icon = config.icon

        # Set device class if specified
        if config.device_class != DeviceClass.NONE:
            if config.device_class == DeviceClass.TEMPERATURE:
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
            elif config.device_class == DeviceClass.HUMIDITY:
                self._attr_device_class = SensorDeviceClass.HUMIDITY
            elif config.device_class == DeviceClass.VOLTAGE:
                self._attr_device_class = SensorDeviceClass.VOLTAGE
            elif config.device_class == DeviceClass.DURATION:
                self._attr_device_class = SensorDeviceClass.DURATION

        # Set entity category for diagnostic entities
        if config.diagnostic:
            self._attr_entity_category = "diagnostic"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        raw = self.coordinator.data.get(self._config.key)
        # Apply scaling from entity config
        return self._config.scale_value(raw)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self._config.unit
