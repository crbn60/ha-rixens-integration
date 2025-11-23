DOMAIN = "rixens"
UPDATE_INTERVAL = 30

# MAPPING: XML Key -> Action ID (integer)
# IMPORTANT: Update these IDs to match your device's interface.cgi 'act' values
CMD_MAP = {
    "setpoint": 1,
    "fanspeed": 2,
    "floorenable": 3,
    "systemheat": 4,
}