"""Climate platform for Rixens integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    PRESET_AWAY,
    PRESET_HOME,
    PRESET_SLEEP,
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
    TEMP_MAX,
    TEMP_MIN,
)
from .coordinator import RixensCoordinator

FAN_MODES = ["auto", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]

# Default preset temperatures (can be customized via integration options)
DEFAULT_PRESET_TEMPS = {
    PRESET_AWAY: 10.0,  # Freeze protection
    PRESET_HOME: 20.0,  # Comfortable living
    PRESET_SLEEP: 18.0,  # Night time
}


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
    _attr_preset_modes = [PRESET_AWAY, PRESET_HOME, PRESET_SLEEP]
    _attr_min_temp = TEMP_MIN
    _attr_max_temp = TEMP_MAX
    _attr_target_temperature_step = 0.5
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.PRESET_MODE
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
        # Track last heat source configuration for state preservation
        self._last_heat_sources: dict[str, bool] | None = None
        # Track current preset mode
        self._preset_mode: str | None = None
        # Load preset temperatures from options or use defaults
        self._load_preset_temps()

    def _load_preset_temps(self) -> None:
        """Load preset temperatures from config entry options."""
        options = self.coordinator.config_entry.options
        self._preset_temps = {
            PRESET_AWAY: options.get("preset_away_temp", DEFAULT_PRESET_TEMPS[PRESET_AWAY]),
            PRESET_HOME: options.get("preset_home_temp", DEFAULT_PRESET_TEMPS[PRESET_HOME]),
            PRESET_SLEEP: options.get("preset_sleep_temp", DEFAULT_PRESET_TEMPS[PRESET_SLEEP]),
        }

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
        """Return the current HVAC mode.

        Mode is based on whether heat sources are enabled, not whether
        heat is currently being called for (system_heat).
        """
        if not self.coordinator.data:
            return HVACMode.OFF

        # HVAC mode is HEAT if any heat source is enabled
        # furnace_src == 2 or electric_src == 2 means that source is enabled
        if (
            self.coordinator.data.settings.furnace_src == 2
            or self.coordinator.data.settings.electric_src == 2
        ):
            return HVACMode.HEAT

        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action.

        Properly distinguishes between:
        - OFF: HVAC mode is OFF
        - IDLE: HVAC mode is HEAT but not calling for heat (temp >= setpoint)
        - HEATING: Calling for heat and actively heating
        """
        if not self.coordinator.data:
            return None

        # If HVAC mode is OFF, action is OFF
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF

        # system_heat indicates thermostat is calling for heat (temp < setpoint)
        if self.coordinator.data.system_heat:
            # Check if actually heating (furnace running or electric on)
            if (
                self.coordinator.data.heater.heat_on
                or self.coordinator.data.settings.electric_src == 2
            ):
                return HVACAction.HEATING
            # Calling for heat but not heating yet (startup delay, etc.)
            return HVACAction.IDLE

        # HVAC mode is HEAT but not calling for heat (temp >= setpoint)
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

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return self._preset_mode

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "furnace_enabled": self.coordinator.data.settings.furnace_src == 2,
            "electric_heat_enabled": self.coordinator.data.settings.electric_src == 2,
            "floor_heat_enabled": self.coordinator.data.settings.floor_src == 2,
            "furnace_active": self.coordinator.data.heater.heat_on,
            "system_calling_for_heat": self.coordinator.data.system_heat,
            "current_humidity": self.coordinator.data.current_humidity,
        }

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.coordinator.api.set_temperature(float(temperature))
            # Clear preset mode when manually setting temperature
            self._preset_mode = None
            # Trigger burst mode for responsive update
            self.coordinator.trigger_burst_mode()
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode.

        Preserves heat source configuration when toggling between OFF and HEAT.
        When turning on, restores previously enabled sources (or defaults to both).
        When turning off, remembers which sources were enabled.
        """
        if hvac_mode == HVACMode.HEAT:
            # Restore previous configuration or default to both sources
            if self._last_heat_sources:
                if self._last_heat_sources.get("furnace"):
                    await self.coordinator.api.set_furnace(True)
                if self._last_heat_sources.get("electric"):
                    await self.coordinator.api.set_electric_heat(True)
            else:
                # Default: enable both heat sources
                await self.coordinator.api.set_furnace(True)
                await self.coordinator.api.set_electric_heat(True)
        elif hvac_mode == HVACMode.OFF:
            # Save current heat source state before turning off
            if self.coordinator.data:
                self._last_heat_sources = {
                    "furnace": self.coordinator.data.settings.furnace_src == 2,
                    "electric": self.coordinator.data.settings.electric_src == 2,
                }
            await self.coordinator.api.set_furnace(False)
            await self.coordinator.api.set_electric_heat(False)
        # Trigger burst mode for responsive update
        self.coordinator.trigger_burst_mode()
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        if fan_mode == "auto":
            await self.coordinator.api.set_fan_speed(FAN_SPEED_AUTO)
        else:
            speed = int(fan_mode)
            if FAN_SPEED_MIN <= speed <= FAN_SPEED_MAX:
                await self.coordinator.api.set_fan_speed(speed)
        # Trigger burst mode for responsive update
        self.coordinator.trigger_burst_mode()
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode.

        Sets temperature to user-configured values for common RV heating scenarios.
        """
        if preset_mode in self._preset_temps:
            await self.coordinator.api.set_temperature(self._preset_temps[preset_mode])
            self._preset_mode = preset_mode
            # Trigger burst mode for responsive update
            self.coordinator.trigger_burst_mode()
            await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the heating system on.

        Delegates to async_set_hvac_mode for consistent state preservation.
        """
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn the heating system off.

        Delegates to async_set_hvac_mode for consistent state preservation.
        """
        await self.async_set_hvac_mode(HVACMode.OFF)
