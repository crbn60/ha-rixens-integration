"""Number platform for Rixens (setpoint, fanspeed)."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RixensDataCoordinator
from .entity_config import DeviceClass, EntityType, get_entities_by_type


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Rixens number entities."""
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensNumber] = []

    # Get all number configurations from entity_config
    number_configs = get_entities_by_type(EntityType.NUMBER)

    # Create entities for configured numbers that exist in data
    for key, config in number_configs.items():
        if key in coordinator.data:
            entities.append(RixensNumber(coordinator, entry, config))

    async_add_entities(entities)


class RixensNumber(CoordinatorEntity[RixensDataCoordinator], NumberEntity):
    """Rixens number entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: RixensDataCoordinator, entry: ConfigEntry, config
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._config = config
        self._attr_unique_id = f"{entry.entry_id}_{config.key}"
        self._attr_name = config.name
        self._attr_icon = config.icon
        self._attr_native_min_value = config.min_value
        self._attr_native_max_value = config.max_value
        self._attr_native_step = config.step
        self._attr_native_unit_of_measurement = config.unit

        # Set device class if specified
        if config.device_class == DeviceClass.TEMPERATURE:
            self._attr_device_class = NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        raw = self.coordinator.data.get(self._config.key)
        # Apply scaling from entity config
        scaled = self._config.scale_value(raw)
        if isinstance(scaled, (int, float)):
            return float(scaled)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self._config.act_id is None:
            return

        # Convert scaled value back to raw value for the controller
        raw_value = int(value * self._config.scaling_factor)

        if await self.coordinator.api.async_set_value(self._config.act_id, raw_value):
            await self.coordinator.async_request_refresh()
