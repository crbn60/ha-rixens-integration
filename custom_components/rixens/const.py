"""Constants for the Rixens integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime

DOMAIN = "rixens"

CONF_HOST = "host"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 15
MIN_POLL_INTERVAL = 2
MAX_POLL_INTERVAL = 3600

PLATFORMS: list[str] = ["sensor", "switch", "number"]

# ------------------------------------------------------------------------------
# ACT Command Mapping
# Maps XML keys to ACT IDs for control commands via interface.cgi
# See docs/act_map.md for details on each command
# ------------------------------------------------------------------------------
CMD_MAP: dict[str, int] = {
    "setpoint": 101,
    "fanspeed": 102,
    "engineenable": 201,
    "electricenable": 202,
    "floorenable": 203,
    "glycol": 204,
    "fanenabled": 205,
    "thermenabled": 206,
}

# ------------------------------------------------------------------------------
# Scaling Factors
# Applied to raw values from status.xml for unit conversion
# Temperature values from controller are in tenths of a degree (e.g., 720 = 72.0°F)
# ------------------------------------------------------------------------------
RAW_TEMP_DIVISOR = 10  # Divide raw temp by 10 to get actual degrees


# ------------------------------------------------------------------------------
# Entity Platform Assignment
# Determines which Home Assistant platform handles each parameter
# ------------------------------------------------------------------------------
class EntityPlatform(StrEnum):
    """Entity platform types."""

    SENSOR = "sensor"
    SWITCH = "switch"
    NUMBER = "number"


# ------------------------------------------------------------------------------
# Entity Mapping Dataclasses
# Define complete entity configuration for each parameter type
# ------------------------------------------------------------------------------
@dataclass
class SensorEntityConfig:
    """Configuration for sensor entities."""

    key: str
    name: str
    icon: str
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit: str | None = None
    value_fn: Callable[[Any], Any] | None = None
    suggested_display_precision: int | None = None


@dataclass
class SwitchEntityConfig:
    """Configuration for switch entities."""

    key: str
    name: str
    icon: str
    icon_off: str | None = None  # Optional icon when switch is off


@dataclass
class NumberEntityConfig:
    """Configuration for number entities."""

    key: str
    name: str
    icon: str
    native_min: float
    native_max: float
    native_step: float = 1.0
    native_unit: str | None = None
    device_class: NumberDeviceClass | None = None
    value_fn: Callable[[Any], float | None] | None = None
    command_fn: Callable[[float], int] | None = None


# ------------------------------------------------------------------------------
# Icon Definitions
# MDI icons for dashboard display, selected based on parameter purpose
# See docs/icons.md for rationale
# ------------------------------------------------------------------------------
ICON_MAP: dict[str, str] = {
    # Temperature & Environmental
    "currenttemp": "mdi:thermometer",
    "currenthumidity": "mdi:water-percent",
    "setpoint": "mdi:thermostat",
    # Fan & Airflow
    "fanspeed": "mdi:fan",
    "fanenabled": "mdi:fan",
    # Heat Sources
    "engineenable": "mdi:engine",
    "electricenable": "mdi:flash",
    "floorenable": "mdi:floor-plan",
    "glycol": "mdi:coolant-temperature",
    # Heater State
    "heaterstate": "mdi:fire",
    "thermenabled": "mdi:thermostat-auto",
    # Diagnostics & Network
    "infra_ip": "mdi:ip-network",
    "infra_netup": "mdi:network",
    "infra_dhcp": "mdi:network-outline",
    # Power & Electrical
    "battv": "mdi:car-battery",
    "glowpin": "mdi:flash-outline",
    # Runtime & Counters
    "runtime": "mdi:timer-outline",
    "altitude": "mdi:altimeter",
    # Faults & Alerts
    "fault": "mdi:alert-circle-outline",
}


def _scale_temp(raw: Any) -> float | None:
    """Scale raw temperature value by dividing by RAW_TEMP_DIVISOR."""
    if isinstance(raw, (int, float)):
        return raw / RAW_TEMP_DIVISOR
    return None


def _scale_temp_for_command(value: float) -> int:
    """Scale temperature value for command (multiply by divisor)."""
    return int(value * RAW_TEMP_DIVISOR)


# ------------------------------------------------------------------------------
# Sensor Entity Definitions
# Read-only entities for monitoring controller state
# ------------------------------------------------------------------------------
SENSOR_ENTITIES: list[SensorEntityConfig] = [
    SensorEntityConfig(
        key="currenttemp",
        name="Current Temperature",
        icon=ICON_MAP["currenttemp"],
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
        value_fn=_scale_temp,
        suggested_display_precision=1,
    ),
    SensorEntityConfig(
        key="currenthumidity",
        name="Current Humidity",
        icon=ICON_MAP["currenthumidity"],
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=PERCENTAGE,
        suggested_display_precision=0,
    ),
    SensorEntityConfig(
        key="heaterstate",
        name="Heater State",
        icon=ICON_MAP["heaterstate"],
        device_class=None,
        state_class=None,
    ),
    SensorEntityConfig(
        key="infra_ip",
        name="Controller IP",
        icon=ICON_MAP["infra_ip"],
    ),
    SensorEntityConfig(
        key="runtime",
        name="Runtime",
        icon=ICON_MAP["runtime"],
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit=UnitOfTime.SECONDS,
    ),
    SensorEntityConfig(
        key="battv",
        name="Battery Voltage",
        icon=ICON_MAP["battv"],
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit="V",
        value_fn=_scale_temp,  # Same divisor applies to battery voltage
        suggested_display_precision=1,
    ),
    SensorEntityConfig(
        key="altitude",
        name="Altitude",
        icon=ICON_MAP["altitude"],
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit="m",
    ),
]

# Lookup dict for sensor entities by key
SENSOR_ENTITY_MAP: dict[str, SensorEntityConfig] = {e.key: e for e in SENSOR_ENTITIES}


# ------------------------------------------------------------------------------
# Switch Entity Definitions
# Writable entities for enabling/disabling heat sources and features
# ------------------------------------------------------------------------------
SWITCH_ENTITIES: list[SwitchEntityConfig] = [
    SwitchEntityConfig(
        key="engineenable",
        name="Engine Heat Source",
        icon=ICON_MAP["engineenable"],
    ),
    SwitchEntityConfig(
        key="electricenable",
        name="Electric Heater",
        icon=ICON_MAP["electricenable"],
    ),
    SwitchEntityConfig(
        key="floorenable",
        name="Floor Heat Loop",
        icon=ICON_MAP["floorenable"],
    ),
    SwitchEntityConfig(
        key="glycol",
        name="Glycol Mode",
        icon=ICON_MAP["glycol"],
    ),
    SwitchEntityConfig(
        key="fanenabled",
        name="Fan Enabled",
        icon=ICON_MAP["fanenabled"],
    ),
    SwitchEntityConfig(
        key="thermenabled",
        name="Thermostat Mode",
        icon=ICON_MAP["thermenabled"],
    ),
]

# Lookup dict for switch entities by key
SWITCH_ENTITY_MAP: dict[str, SwitchEntityConfig] = {e.key: e for e in SWITCH_ENTITIES}


# ------------------------------------------------------------------------------
# Number Entity Definitions
# Writable entities for setpoints and controls with min/max ranges
# ------------------------------------------------------------------------------
NUMBER_ENTITIES: list[NumberEntityConfig] = [
    NumberEntityConfig(
        key="setpoint",
        name="Temperature Setpoint",
        icon=ICON_MAP["setpoint"],
        native_min=50.0,  # 50°F minimum (500 raw)
        native_max=90.0,  # 90°F maximum (900 raw)
        native_step=0.5,
        native_unit=UnitOfTemperature.FAHRENHEIT,
        device_class=NumberDeviceClass.TEMPERATURE,
        value_fn=_scale_temp,
        command_fn=_scale_temp_for_command,
    ),
    NumberEntityConfig(
        key="fanspeed",
        name="Fan Speed",
        icon=ICON_MAP["fanspeed"],
        native_min=0.0,
        native_max=100.0,
        native_step=1.0,
        native_unit=PERCENTAGE,
    ),
]

# Lookup dict for number entities by key
NUMBER_ENTITY_MAP: dict[str, NumberEntityConfig] = {e.key: e for e in NUMBER_ENTITIES}


# ------------------------------------------------------------------------------
# Fault Sensor Configuration
# Fault codes are dynamically created from fault_* keys in status.xml
# ------------------------------------------------------------------------------
FAULT_PREFIX = "fault_"
FAULT_ICON = ICON_MAP["fault"]


@dataclass
class FaultEntityConfig:
    """Configuration for dynamically created fault sensors."""

    key: str
    name: str
    icon: str = field(default=FAULT_ICON)


def create_fault_config(fault_key: str) -> FaultEntityConfig:
    """Create a fault sensor configuration from a fault_* key."""
    fault_name = fault_key.removeprefix(FAULT_PREFIX).upper()
    return FaultEntityConfig(
        key=fault_key,
        name=f"Fault {fault_name}",
        icon=FAULT_ICON,
    )


# ------------------------------------------------------------------------------
# Diagnostic Keys
# Keys that should be included in diagnostics export (redacted as needed)
# ------------------------------------------------------------------------------
DIAGNOSTIC_KEYS = {"infra_ip", "infra_netup", "infra_dhcp", "altitude", "runtime"}
