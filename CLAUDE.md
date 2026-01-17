# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for Rixens RV heating/climate control systems, distributed via HACS. The integration communicates with Rixens devices over HTTP using a local polling approach.

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
├── switch.py        # Switch entities (pump, fan, heat zones)
├── number.py        # Number entity (fan speed slider)
├── manifest.json    # Integration metadata
├── strings.json     # Translatable strings (source)
└── translations/    # Localized UI strings
```

## Device API

The Rixens device exposes an HTTP API:

**Status endpoint:** `GET /status.xml` - Returns XML with all device state
- All temperature values are in **tenths of a degree Celsius** (e.g., 171 = 17.1°C)
- Home Assistant handles display unit conversion based on user preferences

**Control endpoints:** All use GET requests
- `/interface.cgi?act=1&val=XXX` - Set temperature setpoint (in tenths of °C)
- `/interface.cgi?act=2&val=XXX` - Set fan speed (10-100, or 999 for auto)
- `/interface.cgi?act=4&val=0|1` - Pump on/off
- `/interface.cgi?act=5&val=0|1` - Fan on/off
- `/interface.cgi?act=6&val=0|1` - Floor heat on/off
- `/interface.cgi?act=8&val=0|1` - Thermostat mode on/off
- `/interface.cgi?act=10&val=0|1` - Electric heat on/off
- `/buttons.cgi?act=20&val=0|1` - System heat on/off
- `/buttons.cgi?act=11&id=X&mode=0` - Zone button press

## Key Patterns

- **Coordinator pattern**: `RixensCoordinator` polls the device every 5 seconds and distributes data to all entities
- **Entity descriptions**: Sensors and switches use dataclass descriptions with `value_fn` callbacks for clean state extraction
- **API client**: `RixensApi` handles HTTP communication and XML parsing, uses Home Assistant's shared aiohttp session
- **Entities**: All entities inherit from `CoordinatorEntity` for automatic updates

## Platforms

| Platform | Entities |
|----------|----------|
| climate  | Main thermostat (setpoint, current temp, fan modes, HVAC modes) |
| sensor   | Temperature, humidity, battery voltage, flame/inlet/outlet temps, altitude, runtime, diagnostics |
| switch   | System heat, pump, fan, floor heat, electric heat, thermostat mode |
| number   | Fan speed (10-100%) |

## Development

**Testing in Home Assistant:**
1. Copy `custom_components/rixens/` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via Settings > Devices & Services > Add Integration > Rixens
4. Enter device IP address (port defaults to 80)

**Adding new controls:**
1. Add API method in `api.py`
2. Add entity description in appropriate platform file
3. Add translation key in `strings.json` and `translations/en.json`
