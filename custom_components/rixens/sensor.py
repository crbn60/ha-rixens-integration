"""Sensor platform for Rixens integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import RixensData
from .const import DOMAIN
from .coordinator import RixensCoordinator


@dataclass(frozen=True, kw_only=True)
class RixensSensorEntityDescription(SensorEntityDescription):
    """Describes a Rixens sensor entity."""

    value_fn: Callable[[RixensData], float | int | str | None]


SENSOR_DESCRIPTIONS: tuple[RixensSensorEntityDescription, ...] = (
    RixensSensorEntityDescription(
        key="current_temperature",
        translation_key="current_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.current_temp,
    ),
    RixensSensorEntityDescription(
        key="current_humidity",
        translation_key="current_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.current_humidity,
    ),
    RixensSensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.battery_voltage,
    ),
    RixensSensorEntityDescription(
        key="flame_temperature",
        translation_key="flame_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.flame_temp,
    ),
    RixensSensorEntityDescription(
        key="inlet_temperature",
        translation_key="inlet_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.inlet_temp,
    ),
    RixensSensorEntityDescription(
        key="outlet_temperature",
        translation_key="outlet_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.outlet_temp,
    ),
    RixensSensorEntityDescription(
        key="altitude",
        translation_key="altitude",
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.altitude,
    ),
    RixensSensorEntityDescription(
        key="heater_runtime",
        translation_key="heater_runtime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.runtime,
    ),
    RixensSensorEntityDescription(
        key="system_uptime",
        translation_key="system_uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.uptime,
    ),
    RixensSensorEntityDescription(
        key="pid_speed",
        translation_key="pid_speed",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.pid_speed,
    ),
    RixensSensorEntityDescription(
        key="burner_motor",
        translation_key="burner_motor",
        native_unit_of_measurement="RPM",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.burner_motor,
    ),
    RixensSensorEntityDescription(
        key="dosing_pump",
        translation_key="dosing_pump",
        native_unit_of_measurement="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater.dosing_pump,
    ),
    RixensSensorEntityDescription(
        key="fuel_consumption",
        translation_key="fuel_consumption",
        native_unit_of_measurement=f"{UnitOfVolume.MILLILITERS}/h",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: round(data.heater.dosing_pump * 72, 2) if data.heater.dosing_pump else 0,
    ),
    RixensSensorEntityDescription(
        key="heater_state",
        translation_key="heater_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heater_state,
    ),
    RixensSensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.version,
    ),
    RixensSensorEntityDescription(
        key="heat_firmware_version",
        translation_key="heat_firmware_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.heat_version,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rixens sensors based on a config entry."""
    coordinator: RixensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        RixensSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class RixensSensor(CoordinatorEntity[RixensCoordinator], SensorEntity):
    """Representation of a Rixens sensor."""

    _attr_has_entity_name = True
    entity_description: RixensSensorEntityDescription

    def __init__(
        self,
        coordinator: RixensCoordinator,
        description: RixensSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
        )

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
