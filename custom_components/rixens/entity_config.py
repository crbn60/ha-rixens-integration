"""Entity configuration and mapping for Rixens integration.

This module provides a comprehensive mapping of all status.xml parameters to
Home Assistant entities, including:
- Entity type (sensor, number, switch)
- Scaling factors for unit conversion
- Icons for visual representation
- Units of measurement
- Value range constraints
- Device class assignments

This serves as the single source of truth for entity definitions and should be
referenced when adding new entities or updating existing ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfTime,
)


class EntityType(str, Enum):
    """Entity platform types."""

    SENSOR = "sensor"
    NUMBER = "number"
    SWITCH = "switch"


class DeviceClass(str, Enum):
    """Device classes for entities."""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    VOLTAGE = "voltage"
    DURATION = "duration"
    NONE = "none"


@dataclass
class EntityConfig:
    """Configuration for a single entity.

    Attributes:
        key: The XML parameter key from status.xml
        name: Human-readable entity name
        entity_type: Platform type (sensor, number, switch)
        icon: MDI icon identifier
        device_class: Optional device class for semantic meaning
        unit: Unit of measurement (None for dimensionless)
        scaling_factor: Divisor to convert raw value to actual value
        value_transform: Optional function to transform raw value
        min_value: Minimum value for number entities
        max_value: Maximum value for number entities
        step: Step size for number entities
        act_id: ACT command ID for writable entities (None for read-only)
        diagnostic: Whether this is a diagnostic entity
    """

    key: str
    name: str
    entity_type: EntityType
    icon: str
    device_class: DeviceClass = DeviceClass.NONE
    unit: str | None = None
    scaling_factor: float = 1.0
    value_transform: Callable[[Any], Any] | None = None
    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None
    act_id: int | None = None
    diagnostic: bool = False

    def scale_value(self, raw_value: Any) -> Any:
        """Apply scaling factor to raw value.

        Args:
            raw_value: The raw value from status.xml

        Returns:
            Scaled value, or original value if not numeric
        """
        if raw_value is None:
            return None
        if self.value_transform:
            try:
                return self.value_transform(raw_value)
            except Exception:
                pass
        if isinstance(raw_value, (int, float)) and self.scaling_factor != 1.0:
            return raw_value / self.scaling_factor
        return raw_value

    @property
    def is_writable(self) -> bool:
        """Check if entity supports writes."""
        return self.act_id is not None


# Temperature scaling: Rixens uses raw values that need to be divided by 10
# to get Celsius values
TEMP_SCALING = 10.0

# Voltage scaling: Battery voltage is in 0.1V units
VOLTAGE_SCALING = 10.0


# Master entity configuration registry
# This is the single source of truth for all entity mappings
ENTITY_CONFIGS: dict[str, EntityConfig] = {
    # ============================================================================
    # TEMPERATURE SENSORS (read-only, scaled from raw values)
    # ============================================================================
    "currenttemp": EntityConfig(
        key="currenttemp",
        name="Current Temperature",
        entity_type=EntityType.SENSOR,
        icon="mdi:thermometer",
        device_class=DeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        scaling_factor=TEMP_SCALING,
    ),
    "enginetemp": EntityConfig(
        key="enginetemp",
        name="Engine Temperature",
        entity_type=EntityType.SENSOR,
        icon="mdi:engine",
        device_class=DeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        scaling_factor=TEMP_SCALING,
    ),
    "floortemp": EntityConfig(
        key="floortemp",
        name="Floor Temperature",
        entity_type=EntityType.SENSOR,
        icon="mdi:floor-plan",
        device_class=DeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        scaling_factor=TEMP_SCALING,
    ),
    # ============================================================================
    # HUMIDITY SENSOR (read-only)
    # ============================================================================
    "currenthumidity": EntityConfig(
        key="currenthumidity",
        name="Current Humidity",
        entity_type=EntityType.SENSOR,
        icon="mdi:water-percent",
        device_class=DeviceClass.HUMIDITY,
        unit=PERCENTAGE,
    ),
    # ============================================================================
    # SETPOINT & FAN CONTROL (writable numbers)
    # ============================================================================
    "setpoint": EntityConfig(
        key="setpoint",
        name="Setpoint",
        entity_type=EntityType.NUMBER,
        icon="mdi:thermostat",
        device_class=DeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        scaling_factor=TEMP_SCALING,
        min_value=9.0,  # 90 raw / 10 = 9°C (48°F) min
        max_value=22.0,  # 220 raw / 10 = 22°C (72°F) max
        step=0.1,
        act_id=101,
    ),
    "fanspeed": EntityConfig(
        key="fanspeed",
        name="Fan Speed",
        entity_type=EntityType.NUMBER,
        icon="mdi:fan",
        unit=PERCENTAGE,
        min_value=0,
        max_value=100,
        step=1,
        act_id=102,
    ),
    # ============================================================================
    # HEAT SOURCE ENABLE SWITCHES (writable)
    # ============================================================================
    "engineenable": EntityConfig(
        key="engineenable",
        name="Engine Enable",
        entity_type=EntityType.SWITCH,
        icon="mdi:engine",
        act_id=201,
    ),
    "electricenable": EntityConfig(
        key="electricenable",
        name="Electric Enable",
        entity_type=EntityType.SWITCH,
        icon="mdi:flash",
        act_id=202,
    ),
    "floorenable": EntityConfig(
        key="floorenable",
        name="Floor Enable",
        entity_type=EntityType.SWITCH,
        icon="mdi:floor-plan",
        act_id=203,
    ),
    "glycol": EntityConfig(
        key="glycol",
        name="Glycol Mode",
        entity_type=EntityType.SWITCH,
        icon="mdi:water-circle",
        act_id=204,
    ),
    "fanenabled": EntityConfig(
        key="fanenabled",
        name="Fan Enabled",
        entity_type=EntityType.SWITCH,
        icon="mdi:fan",
        act_id=205,
    ),
    "thermenabled": EntityConfig(
        key="thermenabled",
        name="Thermostat Enabled",
        entity_type=EntityType.SWITCH,
        icon="mdi:thermostat",
        act_id=206,
    ),
    # ============================================================================
    # STATE & STATUS SENSORS (read-only)
    # ============================================================================
    "heaterstate": EntityConfig(
        key="heaterstate",
        name="Heater State Code",
        entity_type=EntityType.SENSOR,
        icon="mdi:fire",
    ),
    "glowpin": EntityConfig(
        key="glowpin",
        name="Glow Pin State",
        entity_type=EntityType.SENSOR,
        icon="mdi:flash-outline",
    ),
    # ============================================================================
    # ELECTRICAL SENSORS (read-only, with scaling)
    # ============================================================================
    "battv": EntityConfig(
        key="battv",
        name="Battery Voltage",
        entity_type=EntityType.SENSOR,
        icon="mdi:car-battery",
        device_class=DeviceClass.VOLTAGE,
        unit=UnitOfElectricPotential.VOLT,
        scaling_factor=VOLTAGE_SCALING,
    ),
    # ============================================================================
    # INFRASTRUCTURE / DIAGNOSTIC SENSORS (read-only)
    # ============================================================================
    "infra_ip": EntityConfig(
        key="infra_ip",
        name="Infrastructure IP",
        entity_type=EntityType.SENSOR,
        icon="mdi:ip-network",
        diagnostic=True,
    ),
    "infra_netup": EntityConfig(
        key="infra_netup",
        name="Network Status",
        entity_type=EntityType.SENSOR,
        icon="mdi:network",
        diagnostic=True,
    ),
    "infra_dhcp": EntityConfig(
        key="infra_dhcp",
        name="DHCP Status",
        entity_type=EntityType.SENSOR,
        icon="mdi:network-outline",
        diagnostic=True,
    ),
    "altitude": EntityConfig(
        key="altitude",
        name="Altitude",
        entity_type=EntityType.SENSOR,
        icon="mdi:elevation-rise",
        unit="ft",
        diagnostic=True,
    ),
    "runtime": EntityConfig(
        key="runtime",
        name="Heater Runtime",
        entity_type=EntityType.SENSOR,
        icon="mdi:timer-outline",
        device_class=DeviceClass.DURATION,
        unit=UnitOfTime.SECONDS,
        diagnostic=True,
    ),
}


def get_entity_config(key: str) -> EntityConfig | None:
    """Get entity configuration by key.

    Args:
        key: The entity key from status.xml

    Returns:
        EntityConfig if found, None otherwise
    """
    return ENTITY_CONFIGS.get(key)


def get_entities_by_type(entity_type: EntityType) -> dict[str, EntityConfig]:
    """Get all entity configurations of a specific type.

    Args:
        entity_type: The entity type to filter by

    Returns:
        Dictionary of key -> EntityConfig for matching entities
    """
    return {
        key: config
        for key, config in ENTITY_CONFIGS.items()
        if config.entity_type == entity_type
    }


def get_writable_entities() -> dict[str, EntityConfig]:
    """Get all writable entity configurations.

    Returns:
        Dictionary of key -> EntityConfig for writable entities
    """
    return {key: config for key, config in ENTITY_CONFIGS.items() if config.is_writable}


def get_diagnostic_entities() -> dict[str, EntityConfig]:
    """Get all diagnostic entity configurations.

    Returns:
        Dictionary of key -> EntityConfig for diagnostic entities
    """
    return {key: config for key, config in ENTITY_CONFIGS.items() if config.diagnostic}


def get_fault_entity_config(fault_name: str) -> EntityConfig:
    """Create entity configuration for a fault sensor.

    Fault sensors are dynamically created based on XML content.

    Args:
        fault_name: The fault identifier (e.g., 'AF', 'BF')

    Returns:
        EntityConfig for the fault sensor
    """
    key = f"fault_{fault_name}"
    return EntityConfig(
        key=key,
        name=f"Fault {fault_name.upper()}",
        entity_type=EntityType.SENSOR,
        icon="mdi:alert-circle-outline",
    )
