"""Constants for the Rixens integration."""

DOMAIN = "rixens"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_POLLING_MODE = "polling_mode"
CONF_ADAPTIVE_ACTIVE = "adaptive_active_interval"
CONF_ADAPTIVE_IDLE = "adaptive_idle_interval"
CONF_ADAPTIVE_OFF = "adaptive_off_interval"
CONF_BURST_MODE = "burst_mode"

# Defaults
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 5
DEFAULT_ADAPTIVE_ACTIVE = 5
DEFAULT_ADAPTIVE_IDLE = 10
DEFAULT_ADAPTIVE_OFF = 20

# Polling modes
POLLING_MODE_FIXED = "fixed"
POLLING_MODE_ADAPTIVE = "adaptive"

# Scan interval limits
SCAN_INTERVAL_MIN = 3
SCAN_INTERVAL_MAX = 30

# Burst mode settings
BURST_INTERVAL = 2
BURST_COUNT = 2

# Fan speed constants
FAN_SPEED_AUTO = 999
FAN_SPEED_MIN = 10
FAN_SPEED_MAX = 100
FAN_SPEED_STEP = 10

# Temperature constants (Celsius)
TEMP_MIN = 5
TEMP_MAX = 35
TEMP_STEP = 0.5

# Heater states
HEATER_STATE_OFF = 0
HEATER_STATE_RUNNING = 20
