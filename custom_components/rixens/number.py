"""Number platform for Rixens integration."""

from __future__ import annotations

from typing import Any

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

    def _is_auto_mode(self) -> bool:
        """Check if fan is in auto mode."""
        if not self.coordinator.data:
            return False
        fan_speed = self.coordinator.data.settings.fan_speed
        return fan_speed == "Auto" or fan_speed == str(FAN_SPEED_AUTO)

    @property
    def native_value(self) -> float | None:
        """Return the current fan speed.

        In auto mode, returns the actual PID-controlled speed.
        In manual mode, returns the configured setpoint.
        """
        if not self.coordinator.data:
            return None

        # In auto mode, display actual PID-controlled speed
        if self._is_auto_mode():
            pid_speed = self.coordinator.data.heater.pid_speed
            # Return 0 if heater is off, otherwise clamp to valid range
            if pid_speed == 0:
                return 0
            return max(FAN_SPEED_MIN, min(FAN_SPEED_MAX, pid_speed))

        # In manual mode, display configured setpoint
        fan_speed = self.coordinator.data.settings.fan_speed
        try:
            speed = int(fan_speed)
            return max(FAN_SPEED_MIN, min(FAN_SPEED_MAX, speed))
        except ValueError:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        is_auto = self._is_auto_mode()
        attributes = {
            "mode": "auto" if is_auto else "manual",
            "actual_speed": self.coordinator.data.heater.pid_speed,
        }

        # Add configured speed when in manual mode
        if not is_auto:
            try:
                attributes["configured_speed"] = int(self.coordinator.data.settings.fan_speed)
            except ValueError:
                pass

        return attributes

    async def async_set_native_value(self, value: float) -> None:
        """Set the fan speed.

        If currently in auto mode, this will switch to manual mode
        with the specified speed.
        """
        await self.coordinator.api.set_fan_speed(int(value))
        await self.coordinator.async_request_refresh()
