# Developer Guide

This document covers the technical architecture, entity details, and development workflow for the Rixens Home Assistant integration.

## Architecture

```
custom_components/rixens/
├── __init__.py      # Integration setup, coordinator initialization, platform forwarding
├── api.py           # HTTP API client for device communication
├── coordinator.py   # DataUpdateCoordinator for polling device status
├── config_flow.py   # UI-based configuration flow with connection validation
├── const.py         # Domain and configuration constants
├── climate.py       # Climate entity (thermostat control)
├── sensor.py        # Sensor entities (temp, humidity, diagnostics)
├── switch.py        # Switch entities (furnace, fan, heat zones)
├── number.py        # Number entity (fan speed slider)
├── manifest.json    # Integration metadata
├── strings.json     # Translatable strings (source)
└── translations/    # Localized UI strings
```

## Key Patterns

- **Coordinator pattern**: `RixensCoordinator` polls the device every 5 seconds and distributes data to all entities
- **Entity descriptions**: Sensors and switches use dataclass descriptions with `value_fn` callbacks for clean state extraction
- **API client**: `RixensApi` handles HTTP communication and XML parsing, uses Home Assistant's shared aiohttp session
- **Entities**: All entities inherit from `CoordinatorEntity` for automatic updates

## Device API

The Rixens device exposes an HTTP API:

### Status Endpoint

`GET /status.xml` — Returns XML with all device state.

- All temperature values are in **tenths of a degree Celsius** (e.g., 171 = 17.1°C)
- Home Assistant handles display unit conversion based on user preferences

### Control Endpoints

All use GET requests:

| Endpoint                         | Description                                |
| -------------------------------- | ------------------------------------------ |
| `/interface.cgi?act=1&val=XXX`   | Set temperature setpoint (in tenths of °C) |
| `/interface.cgi?act=2&val=XXX`   | Set fan speed (10-100, or 999 for auto)    |
| `/interface.cgi?act=4&val=0\|1`  | Electric heat on/off                       |
| `/interface.cgi?act=5&val=0\|1`  | Furnace on/off                             |
| `/interface.cgi?act=6&val=0\|1`  | Continuous heat on/off                     |
| `/interface.cgi?act=8&val=0\|1`  | Fan on/off                                 |
| `/interface.cgi?act=10&val=0\|1` | Floor heat on/off                          |

## Entity Reference

### Climate Entity

- **Rixens Heater** (`climate.rixens_heater`)
  - Set target temperature (5-35°C)
  - View current temperature and humidity
  - Control HVAC mode (Off/Heat)
  - Select fan mode (Auto or 10-100% in 10% increments)
  - Choose preset modes (Away/Home/Sleep)
  - View HVAC action (Off/Idle/Heating)
  - Additional attributes show heat source states and system status

### Sensors

#### Environmental

- **Temperature** — Current room temperature
- **Humidity** — Current room humidity
- **Atmospheric Pressure** — Barometric pressure in hPa (used for altitude compensation)

#### Heater Diagnostics

- **Battery Voltage** — RV battery voltage monitoring
- **Flame Temperature** — Burner flame temperature
- **Inlet Temperature** — Heater inlet coolant temperature
- **Outlet Temperature** — Heater outlet coolant temperature
- **Heater Runtime** — Total heater operating time in seconds
- **System Uptime** — Device uptime since last restart

#### Performance

- **PID Speed** — Current PID-controlled fan speed percentage
- **Burner Motor** — Burner motor RPM
- **Dosing Pump** — Fuel pump frequency in Hz
- **Fuel Consumption** — Current fuel consumption rate in ml/h

#### System Information

- **Heater State** — Current operational state code
- **Firmware Version** — Main controller firmware version
- **Heat Firmware Version** — Heater module firmware version

### Switches

- **Furnace** — Enable/disable diesel/propane furnace heating
- **Electric Heat** — Enable/disable electric heating element
- **Floor Heat** — Enable/disable floor heating zone
- **Fan** — Manual fan on/off control
- **Continuous Heat** — Enable/disable continuous heat mode

### Number Entity

- **Fan Speed** — Slider control for manual fan speed (10-100%)
  - Displays actual PID speed when in auto mode
  - Setting a value automatically switches to manual mode

### Binary Sensors

- **Connection** — Device connectivity status (always available, even when device is offline)

## Advanced Behavior

### Heat Source State Preservation

When turning the climate entity on/off:

- The integration remembers which heat sources (furnace, electric) were enabled
- Turning back on restores your previous heat source configuration

### Fan Speed Intelligence

- **Auto Mode**: Displays actual PID-controlled speed from heater
- **Manual Mode**: Shows and controls configured speed setpoint

### HVAC Action States

- **Off**: HVAC mode is off
- **Idle**: Heating enabled but temperature at/above setpoint
- **Heating**: Actively calling for heat and heat sources running

### Error Handling

- **Automatic Retry**: Failed API calls are retried up to 3 times with exponential backoff
- **Graceful Degradation**: Entities remain available with last known data for up to 50 seconds during network issues
- **Connection Monitoring**: Binary sensor shows real-time connection status

## Platforms Summary

| Platform      | Entities                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------ |
| climate       | Main thermostat (setpoint, current temp, fan modes, HVAC modes)                                  |
| sensor        | Temperature, humidity, battery voltage, flame/inlet/outlet temps, altitude, runtime, diagnostics |
| switch        | Furnace, fan, floor heat, electric heat, continuous heat                                         |
| number        | Fan speed (10-100%)                                                                              |
| binary_sensor | Connection status                                                                                |

## Adding New Controls

1. Add API method in `api.py`
2. Add entity description in appropriate platform file
3. Add translation key in `strings.json` and `translations/en.json`

## Contributing

For branching strategy, testing requirements, running tests, and deploying to your Home Assistant instance, see [CONTRIBUTING.md](CONTRIBUTING.md).
