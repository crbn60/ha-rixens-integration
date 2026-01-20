# Rixens Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/crbn60/ha-rixens-integration)](https://github.com/crbn60/ha-rixens-integration/releases)
[![GitHub Issues](https://img.shields.io/github/issues/crbn60/ha-rixens-integration)](https://github.com/crbn60/ha-rixens-integration/issues)

A comprehensive Home Assistant integration for Rixens RV heating and climate control systems. Control your RV's furnace, electric heat, fan, and monitor all critical heating system parameters directly from Home Assistant.

## Overview

The Rixens integration provides complete control and monitoring of your Rixens RV heating system. It communicates with your Rixens device over HTTP on your local network, polling for status updates every 5 seconds by default. All temperature values are automatically converted to your Home Assistant display preferences (Celsius or Fahrenheit).

### Key Features

- **Complete Climate Control** - Full thermostat functionality with temperature setpoint control
- **Multiple Heat Sources** - Control furnace, electric heat, and floor heating independently
- **Smart Presets** - Quick-access temperature presets (Away, Home, Sleep) with customizable temperatures
- **Fan Control** - Auto and manual fan speed control with real-time PID speed monitoring
- **Comprehensive Monitoring** - Track temperature, humidity, fuel consumption, battery voltage, and more
- **Fault Detection** - Real-time monitoring of system faults and errors
- **Connection Resilience** - Automatic retry logic and graceful degradation during network issues
- **Energy Dashboard** - Compatible with Home Assistant Energy Dashboard for tracking consumption

## Entities

After installation, the integration creates the following entities:

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

#### Environmental Sensors
- **Temperature** - Current room temperature
- **Humidity** - Current room humidity
- **Atmospheric Pressure** - Barometric pressure in hPa (used for altitude compensation)

#### Heater Diagnostic Sensors
- **Battery Voltage** - RV battery voltage monitoring
- **Flame Temperature** - Burner flame temperature
- **Inlet Temperature** - Heater inlet coolant temperature
- **Outlet Temperature** - Heater outlet coolant temperature
- **Heater Runtime** - Total heater operating time in seconds
- **System Uptime** - Device uptime since last restart

#### Performance Sensors
- **PID Speed** - Current PID-controlled fan speed percentage
- **Burner Motor** - Burner motor RPM
- **Dosing Pump** - Fuel pump frequency in Hz
- **Fuel Consumption** - Current fuel consumption rate in ml/h

#### System Information
- **Heater State** - Current operational state code
- **Firmware Version** - Main controller firmware version
- **Heat Firmware Version** - Heater module firmware version

### Switches

Control individual heat sources and system components:

- **Furnace** - Enable/disable diesel/propane furnace heating
- **Electric Heat** - Enable/disable electric heating element
- **Floor Heat** - Enable/disable floor heating zone
- **Fan** - Manual fan on/off control

### Number Entity

- **Fan Speed** - Slider control for manual fan speed (10-100%)
  - Displays actual PID speed when in auto mode
  - Setting a value automatically switches to manual mode
  - Extra attributes show mode and actual/configured speeds

### Binary Sensors

- **Connection** - Device connectivity status indicator
  - Shows if the integration can communicate with the device
  - Always available (even when device is offline)

## Configuration

### Initial Setup

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Rixens"
4. Enter your Rixens device details:
   - **Host**: IP address of your Rixens device (e.g., `192.168.1.100`)
   - **Port**: HTTP port (default: `80`)
5. Click **Submit**

The integration will verify connectivity and create all entities.

### Preset Temperature Configuration

Customize the preset temperatures to match your preferences:

1. Go to **Settings** > **Devices & Services**
2. Find the **Rixens** integration
3. Click **Configure**
4. Adjust preset temperatures:
   - **Away**: Freeze protection temperature (default: 10°C)
   - **Home**: Comfortable living temperature (default: 20°C)
   - **Sleep**: Night time temperature (default: 18°C)
5. Click **Submit**

Changes apply immediately without restarting Home Assistant.

## Advanced Features

### Automatic Retry and Error Handling

The integration includes robust error handling:
- **Automatic Retry**: Failed API calls are automatically retried up to 3 times with exponential backoff
- **Graceful Degradation**: During temporary network issues, entities remain available with last known data for up to 50 seconds
- **Connection Monitoring**: Binary sensor shows real-time connection status
- **Detailed Logging**: Comprehensive logging helps troubleshoot connectivity issues

### Heat Source State Preservation

When turning the climate entity on/off:
- The integration remembers which heat sources (furnace, electric) were enabled
- Turning back on restores your previous heat source configuration
- Respects preferences set via individual switch entities

### Fan Speed Intelligence

The fan speed entity adapts based on mode:
- **Auto Mode**: Displays actual PID-controlled speed from heater
- **Manual Mode**: Shows and controls configured speed setpoint
- **State Attributes**: Additional info shows mode, actual speed, and configured speed

### HVAC Action States

The climate entity properly distinguishes between:
- **Off**: HVAC mode is off
- **Idle**: Heating enabled but temperature at/above setpoint
- **Heating**: Actively calling for heat and heat sources running

## Automation Examples

### Freeze Protection

Automatically enable Away mode when leaving:

```yaml
automation:
  - alias: "RV Freeze Protection"
    trigger:
      - platform: state
        entity_id: person.your_name
        from: "home"
        to: "not_home"
        for: "00:30:00"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.rixens_heater
        data:
          preset_mode: "away"
```

### Low Battery Alert

Get notified when battery voltage drops:

```yaml
automation:
  - alias: "RV Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.rixens_heater_battery_voltage
        below: 12.0
    action:
      - service: notify.mobile_app
        data:
          title: "Low RV Battery"
          message: "Battery voltage is {{ states('sensor.rixens_heater_battery_voltage') }}V"
```

### Energy Efficient Heating

Switch to electric heat when on shore power:

```yaml
automation:
  - alias: "Use Electric Heat on Shore Power"
    trigger:
      - platform: state
        entity_id: binary_sensor.shore_power  # Your shore power sensor
        to: "on"
    condition:
      - condition: state
        entity_id: climate.rixens_heater
        state: "heat"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.rixens_heater_furnace
      - service: switch.turn_on
        target:
          entity_id: switch.rixens_heater_electric_heat
```

### Pre-Heat Before Arrival

Use geofencing to pre-heat your RV:

```yaml
automation:
  - alias: "Pre-Heat RV on Approach"
    trigger:
      - platform: zone
        entity_id: person.your_name
        zone: zone.rv_location
        event: enter
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.rixens_heater
        data:
          preset_mode: "home"
```

## Troubleshooting

### Device Not Found

- Verify the Rixens device is powered on and connected to your network
- Check that you can access `http://<device-ip>/status.xml` in a web browser
- Ensure Home Assistant and the Rixens device are on the same network/VLAN
- Check your firewall settings

### Entities Unavailable

- Check the **Connection** binary sensor (`binary_sensor.rixens_heater_connection`)
- Review Home Assistant logs for error messages
- The integration keeps last data for 50 seconds during brief outages
- After 50 seconds of failed updates, entities become unavailable

### Slow Updates

- Default polling interval is 5 seconds
- Check network latency between Home Assistant and Rixens device
- Review Home Assistant logs for timeout warnings

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/crbn60/ha-rixens-integration`
6. Select "Integration" as the category
7. Click "Add"
8. Click "Explore & Download Repositories"
9. Search for "Rixens" and install it
10. Restart Home Assistant
11. Add the integration via Settings > Devices & Services

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/crbn60/ha-rixens-integration/releases)
2. Extract the `custom_components/rixens` folder
3. Copy it to your Home Assistant's `custom_components` directory
4. Restart Home Assistant
5. Add the integration via Settings > Devices & Services

## Device Compatibility

This integration is designed for Rixens RV heating systems that expose an HTTP API on port 80. The device should respond to status requests at `/status.xml` with device state information.

### Tested Devices

- Rixens RV Heater (diesel/propane models)
- Firmware versions: Various (check your device)

### API Compatibility

The integration expects the device to support these API endpoints:
- `GET /status.xml` - Device status (polled every 5 seconds)
- `GET /interface.cgi?act=1&val=XXX` - Set temperature setpoint
- `GET /interface.cgi?act=2&val=XXX` - Set fan speed
- `GET /interface.cgi?act=4&val=X` - Control electric heat
- `GET /interface.cgi?act=5&val=X` - Control furnace
- `GET /interface.cgi?act=8&val=X` - Control fan
- `GET /interface.cgi?act=10&val=X` - Control floor heat

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development

See [CLAUDE.md](CLAUDE.md) for project architecture and development guidelines.

## Support

If you encounter any issues or have questions:

- Check the [Troubleshooting](#troubleshooting) section
- Search existing [issues](https://github.com/crbn60/ha-rixens-integration/issues)
- Open a [new issue](https://github.com/crbn60/ha-rixens-integration/issues/new) with:
  - Home Assistant version
  - Integration version
  - Device model and firmware
  - Relevant logs from Home Assistant
  - Steps to reproduce the issue

## Roadmap

Planned features and enhancements:

- [ ] Energy consumption tracking and cost calculation
- [ ] Smart scheduling and automation helpers
- [ ] Historical analytics and statistics
- [ ] Efficiency monitoring and maintenance alerts
- [ ] Configurable polling intervals
- [ ] Multi-zone support
- [ ] Weather-aware features

See [open issues](https://github.com/crbn60/ha-rixens-integration/issues) for a full list of planned features and known issues.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes in each version.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Home Assistant](https://www.home-assistant.io/)
- Developed with assistance from [Claude Code](https://claude.ai/code)

---

**Disclaimer**: This is a community-developed integration and is not officially affiliated with or endorsed by Rixens. Use at your own risk.
