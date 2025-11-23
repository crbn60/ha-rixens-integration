# custom_components/rixens/const.py

DOMAIN = "rixens"
UPDATE_INTERVAL = 10

# Key used in config_entry.data (single base URL)
RIXENS_URL = "rixens_url"

# MAPPING: XML Key -> Action ID (integer)
CMD_MAP = {
    "setpoint": 1,
    "fanspeed": 2,
    "floorenable": 3,
    "systemheat": 4,
}
