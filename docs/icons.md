# Icon Rationale

This document explains the icon selection for each entity in the Rixens MCS7 integration.

## Icon Selection Principles

1. **Clarity**: Icons should immediately convey the parameter's purpose
2. **Consistency**: Similar parameters use related icons
3. **MDI Standard**: All icons use Material Design Icons (mdi:) format
4. **State Awareness**: Some switches may use different icons for on/off states

## Complete Icon Reference

| Entity Key | Icon | Category | Reason |
|------------|------|----------|--------|
| `currenttemp` | mdi:thermometer | Environmental | Standard temperature indicator |
| `currenthumidity` | mdi:water-percent | Environmental | Humidity/moisture reading |
| `setpoint` | mdi:thermostat | Control | User-adjustable temperature target |
| `fanspeed` | mdi:fan | Airflow | Fan speed control/display |
| `fanenabled` | mdi:fan | Airflow | Fan enable/disable toggle |
| `engineenable` | mdi:engine | Heat Source | Engine-based heating |
| `electricenable` | mdi:flash | Heat Source | Electric heating element |
| `floorenable` | mdi:floor-plan | Heat Source | Floor heating loop |
| `glycol` | mdi:coolant-temperature | Heat Source | Glycol circulation mode |
| `thermenabled` | mdi:thermostat-auto | Control | Automatic thermostat mode |
| `heaterstate` | mdi:fire | Status | Active heating indicator |
| `infra_ip` | mdi:ip-network | Network | Controller IP address |
| `infra_netup` | mdi:network | Network | Network connection status |
| `infra_dhcp` | mdi:network-outline | Network | DHCP configuration |
| `battv` | mdi:car-battery | Power | Battery voltage level |
| `glowpin` | mdi:flash-outline | Ignition | Glow plug/ignition component |
| `runtime` | mdi:timer-outline | Counter | Total operation time |
| `altitude` | mdi:altimeter | Environmental | Altitude measurement |
| `fault_*` | mdi:alert-circle-outline | Fault | Any fault/error condition |

## Icon Categories

### Environmental Sensors
- Temperature: `mdi:thermometer`
- Humidity: `mdi:water-percent`
- Altitude: `mdi:altimeter`

### Heat Source Controls
- Engine: `mdi:engine`
- Electric: `mdi:flash`
- Floor: `mdi:floor-plan`
- Glycol: `mdi:coolant-temperature`

### Airflow Controls
- Fan: `mdi:fan`

### Temperature Controls
- Setpoint: `mdi:thermostat`
- Auto mode: `mdi:thermostat-auto`

### Status Indicators
- Heating active: `mdi:fire`
- Faults: `mdi:alert-circle-outline`

### Network/Diagnostic
- IP address: `mdi:ip-network`
- Network status: `mdi:network`
- DHCP: `mdi:network-outline`

### Power/Electrical
- Battery: `mdi:car-battery`
- Glow plug: `mdi:flash-outline`

### Counters
- Runtime: `mdi:timer-outline`

## Adding New Icons

When adding new entities:

1. Choose an icon that clearly represents the parameter
2. Check for existing icons in related entities
3. Use MDI icon browser: https://materialdesignicons.com/
4. Add to `ICON_MAP` in `const.py`
5. Document the choice in this file

---

*Last updated: 2025-11-24*