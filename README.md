# Rixens Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/maintainer-%40crbn60-blue.svg)](https://github.com/crbn60)

A custom Home Assistant integration to monitor and control **Rixens Hydronic Systems** (and compatible MCS controllers) via their local Wi-Fi interface.

This integration polls the device's `status.xml` file for real-time data and sends commands via `interface.cgi` to adjust settings like temperature setpoints and fan speeds.

## Features

* **Sensors:** Monitors current temperature, battery voltage, flame temperature, humidity, and uptime.
* **Controls:** Adjust target temperature (Setpoint) and Fan Speed via Number entities.
* **Switches:** Toggle "Floor Heating" and "System Heat" on/off.
* **Local Polling:** Works entirely locally; no cloud connection required.

%% Flowchart for Data and Network Interaction
flowchart LR
    subgraph Home Assistant (HA)
        HA_UI[HA UI / Services]
    end
    subgraph Rixens Integration (Custom Component)
        R_COORD[DataUpdateCoordinator]
        R_API[RixensApiClient]
    end
    subgraph Rixens Device (Local Network)
        R_STATUS["status.xml (Data)"]
        R_CONTROL["interface.cgi (Control)"]
    end

    %% Polling Flow (Every 30s)
    R_COORD -- Scheduled Poll --> R_API
    R_API -- HTTP GET /status.xml --> R_STATUS
    R_STATUS -- XML Data --> R_API
    R_API -- Parsed Dict --> R_COORD
    R_COORD -- Update --> HA_UI

    %% Control Flow (User Action)
    HA_UI -- Service Call (e.g., set_value) --> R_API
    R_API -- HTTP GET /interface.cgi?act=X&val=Y --> R_CONTROL
    R_CONTROL -- HTTP 200 OK --> R_API
    R_API -- Triggers --> R_COORD(Refresh)
    
## Installation

### Option 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the **3 dots** in the top-right corner and select **Custom repositories**.
3. Paste the URL of this repository: `https://github.com/crbn60/ha-rixens-integration`
4. Select Category: **Integration**.
5. Click **Add**, then click **Download** on the new card that appears.
6. Restart Home Assistant.

### Option 2: Manual Installation

1. Download the `custom_components/rixens` folder from this repository.
2. Copy the folder into your Home Assistant's `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml` file. Replace the IP address with the static IP of your Rixens controller.

```yaml
rixens:
  data_url: "[http://192.168.1.50/status.xml](http://192.168.1.50/status.xml)"
  control_url: "[http://192.168.1.50/interface.cgi](http://192.168.1.50/interface.cgi)"
```

### Finding your IP Address

You can usually find the IP address of your controller by looking at your router's client list. It typically appears with the hostname `RIXENS` or `MCS`.

## Entities Created

| Entity ID | Description | Type |
| :--- | :--- | :--- |
| `sensor.rixens_current_temp` | Current ambient temperature | Sensor |
| `sensor.rixens_battery_voltage` | System voltage | Sensor |
| `number.rixens_target_temperature` | Thermostat Setpoint | Number |
| `number.rixens_fan_speed` | Fan Speed Control (0-100) | Number |
| `switch.rixens_floor_heating` | Floor Loop Enable/Disable | Switch |
| `switch.rixens_system_heat` | Main System Heat Switch | Switch |

*(Note: Entity IDs use the `rixens_` prefix, derived from the domain name.)*

## Debugging

If you run into issues, you can enable debug logging to see exactly what XML the device is returning. Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.rixens: debug
```

### Disclaimer

This is an unofficial community integration. It is not affiliated with or supported by Rixens' Enterprises. Use at your own risk.
