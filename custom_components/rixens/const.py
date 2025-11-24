"""Constants for the Rixens integration."""

DOMAIN = "rixens"

CONF_HOST = "host"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 15
MIN_POLL_INTERVAL = 2
MAX_POLL_INTERVAL = 3600

PLATFORMS: list[str] = ["sensor", "switch", "number"]

# Legacy constants - maintained for backwards compatibility
# New code should use entity_config.py instead
FAULT_PREFIX = "fault_"
