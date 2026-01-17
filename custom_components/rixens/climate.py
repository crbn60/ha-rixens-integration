"""Climate platform for Rixens integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FAN_SPEED_AUTO,
    FAN_SPEED_MAX,
    FAN_SPEED_MIN,
    HEATER_STATE_OFF,
    TEMP_MAX,
    TEMP_MIN,
)
from .coordinator import RixensCoordinator

FAN_MODES = ["auto", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rixens climate based on a config entry."""
    coordinator: RixensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RixensClimate(coordinator)])


class RixensClimate(CoordinatorEntity[RixensCoordinator], ClimateEntity):
    """Representation of a Rixens climate device."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_fan_modes = FAN_MODES
    _attr_min_temp = TEMP_MIN
    _attr_max_temp = TEMP_MAX
    _attr_target_temperature_step = 0.5
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: RixensCoordinator) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_climate"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Rixens Heater",
            manufacturer="Rixens",
            model="RV Heater",
            sw_version=coordinator.data.version if coordinator.data else None,
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.coordinator.data:
            return self.coordinator.data.current_temp
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        if self.coordinator.data:
            return self.coordinator.data.settings.setpoint
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        if self.coordinator.data and self.coordinator.data.system_heat:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        if not self.coordinator.data:
            return None

        if not self.coordinator.data.system_heat:
            return HVACAction.OFF

        # Check if heater is actively heating by looking at heat_on flag
        # and heater_state (should be non-zero when running)
        if self.coordinator.data.heater.heat_on and self.coordinator.data.heater.heater_state != HEATER_STATE_OFF:
            return HVACAction.HEATING

        return HVACAction.IDLE

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        if not self.coordinator.data:
            return None

        fan_speed = self.coordinator.data.settings.fan_speed
        if fan_speed == "Auto" or fan_speed == str(FAN_SPEED_AUTO):
            return "auto"
        return fan_speed

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.coordinator.api.set_temperature(float(temperature))
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.HEAT:
            await self.coordinator.api.set_system_heat(True)
        elif hvac_mode == HVACMode.OFF:
            await self.coordinator.api.set_system_heat(False)
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        if fan_mode == "auto":
            await self.coordinator.api.set_fan_speed(FAN_SPEED_AUTO)
        else:
            speed = int(fan_mode)
            if FAN_SPEED_MIN <= speed <= FAN_SPEED_MAX:
                await self.coordinator.api.set_fan_speed(speed)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
