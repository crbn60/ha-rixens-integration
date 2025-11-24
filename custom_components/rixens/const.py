"""Constants for the Rixens integration."""
DOMAIN = "rixens"

CONF_HOST = "host"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 15
MIN_POLL_INTERVAL = 2
MAX_POLL_INTERVAL = 3600

PLATFORMS: list[str] = ["sensor", "switch", "number"]

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

ICON_MAP = {
    "currenttemp": "mdi:thermometer",
    "currenthumidity": "mdi:water-percent",
    "fanspeed": "mdi:fan",
    "setpoint": "mdi:thermostat",
    "engineenable": "mdi:engine",
    "electricenable": "mdi:flash",
    "floorenable": "mdi:floor-plan",
    "heaterstate": "mdi:fire",
    "infra_ip": "mdi:ip-network",
    "battv": "mdi:car-battery",
    "glowpin": "mdi:flash-outline",
    "fault": "mdi:alert-circle-outline",
}

RAW_TEMP_DIVISOR = 1
DIAGNOSTIC_KEYS = {"infra_ip", "infra_netup", "infra_dhcp", "altitude", "runtime"}
FAULT_PREFIX = "fault_"