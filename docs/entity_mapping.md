# Entity Mapping Reference

This document describes how Rixens MCS7 controller parameters are mapped to Home Assistant entities. It serves as a reference for maintainers and developers.

## Overview

The integration parses `status.xml` from the MCS7 controller and maps each parameter to an appropriate Home Assistant entity type:

| Platform | Purpose | Examples |
|----------|---------|----------|
| **Sensor** | Read-only values | Temperature, humidity, heater state |
| **Switch** | Boolean on/off controls | Engine enable, electric heater enable |
| **Number** | Adjustable numeric values | Temperature setpoint, fan speed |

## XML Schema Mapping

### Flat Key Structure
Most parameters are flat key-value pairs:
```xml
<status>
    <currenttemp>720</currenttemp>
    <setpoint>680</setpoint>
    <engineenable>1</engineenable>
</status>
```

### Nested Structures
Nested elements are flattened with prefix:
```xml
<status>
    <heater>
        <temp>720</temp>
        <state>3</state>
    </heater>
</status>
```
Maps to: `heater_temp`, `heater_state`

### Fault Codes
Faults use a special structure:
```xml
<faults>
    <fault>
        <name>overtemp</name>
        <value>0</value>
    </fault>
</faults>
```
Maps to: `fault_overtemp`

## Scaling Factors

### Temperature Values
Raw values from the controller are in tenths of a degree Fahrenheit:
- **Divisor:** 10
- **Example:** Raw `720` → Display `72.0°F`

This applies to:
- `currenttemp` (Current Temperature sensor)
- `setpoint` (Temperature Setpoint number)
- `battv` (Battery Voltage sensor - same divisor)

### Percentage Values
Fan speed and humidity are direct percentages (no scaling):
- `currenthumidity`: 0-100%
- `fanspeed`: 0-100%

## Sensor Entities (Read-Only)

| Key | Name | Device Class | Unit | Scaling | Icon |
|-----|------|--------------|------|---------|------|
| `currenttemp` | Current Temperature | temperature | °F | ÷10 | mdi:thermometer |
| `currenthumidity` | Current Humidity | humidity | % | none | mdi:water-percent |
| `heaterstate` | Heater State | - | - | none | mdi:fire |
| `infra_ip` | Controller IP | - | - | none | mdi:ip-network |
| `runtime` | Runtime | duration | s | none | mdi:timer-outline |
| `battv` | Battery Voltage | voltage | V | ÷10 | mdi:car-battery |
| `altitude` | Altitude | distance | m | none | mdi:altimeter |

### Fault Sensors (Dynamic)
Fault sensors are automatically created for each `fault_*` key found in the data:
- **Name format:** "Fault {FAULT_NAME}"
- **Icon:** mdi:alert-circle-outline
- **Value:** Typically 0 (inactive) or 1 (active)

## Switch Entities (Writable)

| Key | Name | ACT ID | Icon |
|-----|------|--------|------|
| `engineenable` | Engine Heat Source | 201 | mdi:engine |
| `electricenable` | Electric Heater | 202 | mdi:flash |
| `floorenable` | Floor Heat Loop | 203 | mdi:floor-plan |
| `glycol` | Glycol Mode | 204 | mdi:coolant-temperature |
| `fanenabled` | Fan Enabled | 205 | mdi:fan |
| `thermenabled` | Thermostat Mode | 206 | mdi:thermostat-auto |

### Command Format
Switches send: `interface.cgi?act={ACT_ID}&val={0|1}`

## Number Entities (Writable)

| Key | Name | ACT ID | Range | Step | Unit | Scaling | Icon |
|-----|------|--------|-------|------|------|---------|------|
| `setpoint` | Temperature Setpoint | 101 | 50-90 | 0.5 | °F | ÷10 read, ×10 write | mdi:thermostat |
| `fanspeed` | Fan Speed | 102 | 0-100 | 1 | % | none | mdi:fan |

### Scaling for Commands
For `setpoint`:
- **Read:** Raw `720` → Display `72.0°F`
- **Write:** User enters `72.0°F` → Send `720` to controller

For `fanspeed`:
- **Read/Write:** Direct percentage, no scaling

### Command Format
Numbers send: `interface.cgi?act={ACT_ID}&val={scaled_value}`

## Icon Selection Rationale

Icons are selected based on parameter purpose:

| Category | Icon Pattern | Example Keys |
|----------|--------------|--------------|
| Temperature | mdi:thermometer* | currenttemp |
| Humidity | mdi:water-percent | currenthumidity |
| Fan/Airflow | mdi:fan | fanspeed, fanenabled |
| Heating | mdi:fire, mdi:flash | heaterstate, electricenable |
| Engine | mdi:engine | engineenable |
| Floor heating | mdi:floor-plan | floorenable |
| Network/Diagnostic | mdi:ip-network | infra_ip |
| Battery | mdi:car-battery | battv |
| Runtime/Timer | mdi:timer-outline | runtime |
| Faults | mdi:alert-circle-outline | fault_* |
| Thermostat controls | mdi:thermostat* | setpoint, thermenabled |

## Entity Type Selection Logic

The platform assignment follows this logic:

```python
# Switches: Boolean on/off controls with ACT commands
# Keys that end with "enable", "enabled", or are mode toggles
SWITCH_KEYS = ["engineenable", "electricenable", "floorenable", 
               "glycol", "fanenabled", "thermenabled"]

# Numbers: Adjustable values with min/max ranges
# Keys that represent user-configurable settings
NUMBER_KEYS = ["setpoint", "fanspeed"]

# Sensors: Everything else (read-only values)
# Temperature readings, state codes, diagnostics, faults
SENSOR_KEYS = ["currenttemp", "currenthumidity", "heaterstate", 
               "infra_ip", "runtime", "battv", "altitude", "fault_*"]
```

## Diagnostic Keys

Keys included in diagnostic exports (sensitive data redacted):
- `infra_ip` - Controller IP address (redacted)
- `infra_netup` - Network status
- `infra_dhcp` - DHCP status
- `altitude` - Altitude reading
- `runtime` - Total runtime

## Adding New Entities

### Adding a New Sensor
1. Add configuration to `SENSOR_ENTITIES` in `const.py`
2. Define device class, state class, and unit if applicable
3. Add scaling function if needed
4. Add icon to `ICON_MAP`
5. Add tests in `test_entity_mapping.py`

### Adding a New Switch
1. Add configuration to `SWITCH_ENTITIES` in `const.py`
2. Add ACT ID to `CMD_MAP`
3. Add icon to `ICON_MAP`
4. Update `docs/act_map.md` with command details
5. Add tests

### Adding a New Number
1. Add configuration to `NUMBER_ENTITIES` in `const.py`
2. Add ACT ID to `CMD_MAP`
3. Define min/max/step ranges
4. Add scaling functions if needed (value_fn, command_fn)
5. Add icon to `ICON_MAP`
6. Update `docs/act_map.md`
7. Add tests

## Troubleshooting

### Entity Not Appearing
- Check if the key exists in `status.xml`
- Verify the key is configured in the appropriate entity list
- Check coordinator data for the key presence

### Wrong Values
- Verify scaling factor is correct
- Check device class matches the value type
- Review value_fn implementation

### Commands Not Working
- Verify ACT ID in `CMD_MAP`
- Check command_fn scaling (if applicable)
- Test command directly: `http://{host}/interface.cgi?act={id}&val={val}`

---

*Last updated: 2025-11-24*
