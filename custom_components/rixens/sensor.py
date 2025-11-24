"""Sensor platform for Rixens MCS7 controller.

Creates read-only sensor entities from status.xml parameters.
See const.py for SENSOR_ENTITIES configuration and docs/entity_mapping.md for details.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FAULT_PREFIX,
    SENSOR_ENTITIES,
    SensorEntityConfig,
    create_fault_config,
)
from .coordinator import RixensDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Rixens sensor entities from a config entry."""
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensSensor] = []
    data = coordinator.data or {}

    # Add configured sensor entities that exist in the data
    for config in SENSOR_ENTITIES:
        if config.key in data:
            entities.append(RixensSensor(coordinator, entry, config))

    # Dynamically create fault sensors from fault_* keys
    for key in data.keys():
        if key.startswith(FAULT_PREFIX):
            fault_config = create_fault_config(key)
            entities.append(RixensFaultSensor(coordinator, entry, fault_config))

    async_add_entities(entities)


class RixensSensor(CoordinatorEntity[RixensDataCoordinator], SensorEntity):
    """Representation of a Rixens sensor entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RixensDataCoordinator,
        entry: ConfigEntry,
        config: SensorEntityConfig,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{config.key}"
        self._attr_name = config.name
        self._attr_icon = config.icon

        # Set device class and state class from config
        if config.device_class:
            self._attr_device_class = config.device_class
        if config.state_class:
            self._attr_state_class = config.state_class
        if config.native_unit:
            self._attr_native_unit_of_measurement = config.native_unit
        if config.suggested_display_precision is not None:
            self._attr_suggested_display_precision = config.suggested_display_precision

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        raw = self.coordinator.data.get(self._config.key)
        if self._config.value_fn is not None:
            try:
                return self._config.value_fn(raw)
            except (TypeError, ValueError):
                return raw
        return raw


class RixensFaultSensor(CoordinatorEntity[RixensDataCoordinator], SensorEntity):
    """Representation of a Rixens fault sensor entity.

    Fault sensors are dynamically created from fault_* keys in status.xml.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RixensDataCoordinator,
        entry: ConfigEntry,
        config: Any,  # FaultEntityConfig
    ) -> None:
        """Initialize the fault sensor."""
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{config.key}"
        self._attr_name = config.name
        self._attr_icon = config.icon

    @property
    def native_value(self) -> Any:
        """Return the current fault value (typically 0 or 1)."""
        return self.coordinator.data.get(self._config.key)
