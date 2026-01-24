"""Constants for the Rixens integration."""

DOMAIN = "rixens"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"

# Defaults
DEFAULT_PORT = 80

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

# Fuel consumption constants
CONF_FUEL_DOSE = "fuel_dose"
DEFAULT_FUEL_DOSE = 0.0297979798  # ml per dose (improved accuracy)
