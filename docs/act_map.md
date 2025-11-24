# ACT Mapping (Validated)

This document provides the complete mapping of parameters to ACT IDs for the Rixens MCS7 controller's interface.cgi API.

## Verified Parameters

| Parameter      | ACT ID | Range        | Type    | Entity Platform | Notes |
|----------------|--------|--------------|---------|----------------|-------|
| setpoint       | 101    | 90–220 (raw) | Number  | number         | Temperature setpoint in °F |
| fanspeed       | 102    | 0–100        | Number  | number         | Fan speed percentage |
| engineenable   | 201    | 0/1          | Boolean | switch         | Engine heat source |
| electricenable | 202    | 0/1          | Boolean | switch         | Electric heater |
| floorenable    | 203    | 0/1          | Boolean | switch         | Floor loop |
| glycol         | 204    | 0/1          | Boolean | switch         | Glycol mode |
| fanenabled     | 205    | 0/1          | Boolean | switch         | Master fan |
| thermenabled   | 206    | 0/1          | Boolean | switch         | Thermostat logic |

## Implementation Status

✅ All parameters in this table are:
- Defined in `CMD_MAP` (const.py)
- Implemented in entity platforms (switch.py, number.py)
- Covered by unit tests
- Documented with icons

## Usage

### Control Command Format
```
GET http://<controller-ip>/interface.cgi?act=<ACT_ID>&val=<VALUE>
```

### Examples
```
# Set temperature setpoint to 180°F
GET http://10.0.22.6/interface.cgi?act=101&val=180

# Enable engine heat source
GET http://10.0.22.6/interface.cgi?act=201&val=1

# Set fan speed to 75%
GET http://10.0.22.6/interface.cgi?act=102&val=75

# Disable electric heater
GET http://10.0.22.6/interface.cgi?act=202&val=0
```

## Data Sources

### Read (Polling)
Status data is read from `status.xml` endpoint at configured poll interval (default: 15 seconds).

### Write (Control)
Control commands are sent via `interface.cgi` with act/val parameters.

## Validation

All parameters have been validated for:
1. **Type correctness**: Boolean (0/1) or Number with proper ranges
2. **CMD_MAP completeness**: All parameters mapped to unique ACT IDs
3. **Entity coverage**: All parameters exposed through appropriate entities
4. **Test coverage**: Comprehensive unit tests for all control flows

## See Also

- [Control Mapping Documentation](control_mapping.md) - Detailed API usage and conventions
- [Icons Documentation](icons.md) - Icon mapping for dashboard display
- [README.md](../README.md) - Integration overview and features
