"""Number platform for Rixens integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FAN_SPEED_AUTO, FAN_SPEED_MAX, FAN_SPEED_MIN, FAN_SPEED_STEP
from .coordinator import RixensCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rixens number entities based on a config entry."""
    coordinator: RixensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RixensFanSpeed(coordinator)])


class RixensFanSpeed(CoordinatorEntity[RixensCoordinator], NumberEntity):
    """Representation of Rixens fan speed control."""

    _attr_has_entity_name = True
    _attr_translation_key = "fan_speed"
    _attr_native_min_value = FAN_SPEED_MIN
    _attr_native_max_value = FAN_SPEED_MAX
    _attr_native_step = FAN_SPEED_STEP
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: RixensCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_fan_speed"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
        )

    @property
    def native_value(self) -> float | None:
        """Return the current fan speed."""
        if not self.coordinator.data:
            return None

        fan_speed = self.coordinator.data.settings.fan_speed
        if fan_speed == "Auto" or fan_speed == str(FAN_SPEED_AUTO):
            # Return max value to indicate auto mode (or could return None)
            return FAN_SPEED_MAX
        try:
            speed = int(fan_speed)
            # Clamp to valid range
            return max(FAN_SPEED_MIN, min(FAN_SPEED_MAX, speed))
        except ValueError:
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the fan speed."""
        await self.coordinator.api.set_fan_speed(int(value))
        await self.coordinator.async_request_refresh()
