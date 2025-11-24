"""Number platform for Rixens MCS7 controller.

Creates writable number entities for setpoints and control values.
See const.py for NUMBER_ENTITIES configuration and docs/entity_mapping.md for details.
"""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CMD_MAP, DOMAIN, NUMBER_ENTITIES, NumberEntityConfig
from .coordinator import RixensDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Rixens number entities from a config entry."""
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensNumber] = []
    data = coordinator.data or {}

    # Add configured number entities that exist in the data
    for config in NUMBER_ENTITIES:
        if config.key in data:
            entities.append(RixensNumber(coordinator, entry, config))

    async_add_entities(entities)


class RixensNumber(CoordinatorEntity[RixensDataCoordinator], NumberEntity):
    """Representation of a Rixens number entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RixensDataCoordinator,
        entry: ConfigEntry,
        config: NumberEntityConfig,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{config.key}"
        self._attr_name = config.name
        self._attr_icon = config.icon
        self._attr_native_min_value = config.native_min
        self._attr_native_max_value = config.native_max
        self._attr_native_step = config.native_step

        # Set unit and device class from config
        if config.native_unit:
            self._attr_native_unit_of_measurement = config.native_unit
        if config.device_class:
            self._attr_device_class = config.device_class

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        raw = self.coordinator.data.get(self._config.key)
        if self._config.value_fn is not None:
            try:
                return self._config.value_fn(raw)
            except (TypeError, ValueError):
                return None
        if isinstance(raw, (int, float)):
            return float(raw)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        act = CMD_MAP.get(self._config.key)
        if act is None:
            return

        # Apply command transformation if defined
        if self._config.command_fn is not None:
            command_value = self._config.command_fn(value)
        else:
            command_value = int(value)

        if await self.coordinator.api.async_set_value(act, command_value):
            await self.coordinator.async_request_refresh()
