# Control Mapping Documentation

## Overview
This document describes the control interface for the Rixens MCS7 hydronic heating controller, including parameter mappings, validation rules, and usage conventions.

## CMD_MAP Reference

The `CMD_MAP` dictionary in `const.py` defines the mapping between parameter names and their corresponding ACT IDs used in the controller's interface.cgi API.

### Control Parameters

| Parameter Name | ACT ID | Type | Range | Units | Description |
|---------------|--------|------|-------|-------|-------------|
| `setpoint` | 101 | Number | 90-220 | °F (raw) | Target temperature setpoint |
| `fanspeed` | 102 | Number | 0-100 | % | Fan speed percentage |
| `engineenable` | 201 | Boolean | 0/1 | - | Engine heat source enable |
| `electricenable` | 202 | Boolean | 0/1 | - | Electric heater enable |
| `floorenable` | 203 | Boolean | 0/1 | - | Floor loop heating enable |
| `glycol` | 204 | Boolean | 0/1 | - | Glycol mode enable |
| `fanenabled` | 205 | Boolean | 0/1 | - | Master fan enable |
| `thermenabled` | 206 | Boolean | 0/1 | - | Thermostat logic enable |

## API Usage

### Setting Parameters by ACT ID

Direct control using ACT ID:

```python
from custom_components.rixens.api import RixensApiClient

# Set setpoint to 180°F
success = await api_client.async_set_value(act=101, val=180)
```

### Setting Parameters by Name

Convenient control using parameter names (recommended):

```python
from custom_components.rixens.api import RixensApiClient
from custom_components.rixens.const import CMD_MAP

# Set setpoint to 180°F using parameter name
success = await api_client.async_set_parameter("setpoint", 180, CMD_MAP)

# Enable engine heat source
success = await api_client.async_set_parameter("engineenable", 1, CMD_MAP)

# Disable electric heater
success = await api_client.async_set_parameter("electricenable", 0, CMD_MAP)
```

## Entity Types

### Number Entities
Number entities provide adjustable numeric values with min/max validation.

- **Setpoint** (`number.rixens_setpoint`)
  - Range: 90-220
  - Step: 1
  - Unit: °F (raw value)
  
- **Fan Speed** (`number.rixens_fan_speed`)
  - Range: 0-100
  - Step: 1
  - Unit: %

### Switch Entities
Switch entities provide on/off control for various system features.

- **Engine Enable** (`switch.rixens_engineenable`) - Controls engine heat source
- **Electric Enable** (`switch.rixens_electricenable`) - Controls electric heater
- **Floor Enable** (`switch.rixens_floorenable`) - Controls floor loop heating
- **Glycol** (`switch.rixens_glycol`) - Controls glycol mode
- **Fan Enabled** (`switch.rixens_fanenabled`) - Controls master fan
- **Therm Enabled** (`switch.rixens_thermenabled`) - Controls thermostat logic

## Sign Conventions

### Boolean Values
- `0` = Off/Disabled
- `1` = On/Enabled

All boolean parameters use standard 0/1 convention.

### Numeric Values
- **Temperature values** are represented as raw integers (e.g., 180 for 180°F)
- **Fan speed** is represented as percentage (0-100)
- Negative values are not used in this system

## Validation Rules

### Range Validation
All number entities enforce their configured min/max ranges at the Home Assistant level. The integration uses the following ranges:

- **Setpoint**: 90-220 (configured in `NUMBER_ENTITIES`)
- **Fan Speed**: 0-100 (configured in `NUMBER_ENTITIES`)

### Type Conversion
Float values passed to number entities are automatically converted to integers before transmission:
```python
await number_entity.async_set_native_value(180.5)  # Sent as 180 to controller
```

### Error Handling
- Invalid parameter names raise `ValueError`
- HTTP errors during transmission return `False` without raising exceptions
- Timeouts return `False` without raising exceptions
- On failure, entity refresh is not triggered to avoid inconsistent state

## Write Access Permissions

All parameters in CMD_MAP are writable through the interface.cgi endpoint. The controller determines actual write permissions based on its internal state and configuration.

### Entity-Level Permissions
From Home Assistant's perspective, all entities mapped in CMD_MAP are writable:
- Number entities: Allow value adjustment within defined ranges
- Switch entities: Allow on/off toggling

### Controller-Level Restrictions
The controller may reject commands based on:
- Current operational mode
- Safety interlocks
- Hardware limitations
- Configuration settings

## API Endpoint Details

### Control Endpoint
```
GET http://<controller-ip>/interface.cgi?act=<ACT_ID>&val=<VALUE>
```

**Parameters:**
- `act`: Action ID from CMD_MAP
- `val`: Integer value (0/1 for booleans, range value for numbers)

**Response:**
- HTTP 200 on success
- HTTP error codes on failure

**Notes:**
- Uses GET method for compatibility
- Synchronous operation
- No response body validation currently implemented
- Commands are sent with a lock to prevent concurrent writes

## Best Practices

### 1. Use Parameter Names
```python
# Good - readable and maintainable
await api_client.async_set_parameter("setpoint", 180, CMD_MAP)

# Avoid - harder to maintain
await api_client.async_set_value(101, 180)
```

### 2. Check Return Values
```python
success = await api_client.async_set_parameter("engineenable", 1, CMD_MAP)
if not success:
    _LOGGER.warning("Failed to enable engine heat source")
```

### 3. Coordinate Refresh
Entity implementations automatically request coordinator refresh on successful writes:
```python
if await self.coordinator.api.async_set_value(act, value):
    await self.coordinator.async_request_refresh()
```

### 4. Validate Before Sending
Number entities validate ranges before transmission. For custom code:
```python
# Validate setpoint is within range
if 90 <= setpoint <= 220:
    await api_client.async_set_parameter("setpoint", setpoint, CMD_MAP)
```

## Testing

Comprehensive unit tests cover:
- CMD_MAP validation (uniqueness, types, completeness)
- Parameter name lookup and validation
- Switch on/off operations
- Number value setting and boundary conditions
- Error handling for failed API calls
- Mock coordinator refresh behavior

Run tests with:
```bash
pytest tests/test_api.py tests/test_switch.py tests/test_number.py -v
```

## Security Considerations

### No Authentication
The interface.cgi endpoint does not require authentication. Ensure the controller is on a trusted network.

### Input Validation
- All numeric inputs are validated for type and range
- Parameter names are validated against CMD_MAP
- No SQL injection risk (no database queries)
- No command injection risk (parameters are integers only)

### Network Security
- Uses HTTP (not HTTPS)
- Consider network segmentation for production deployments
- Controller should not be exposed to untrusted networks

## Troubleshooting

### Command Not Working
1. Check network connectivity to controller
2. Verify parameter name is in CMD_MAP
3. Verify value is within valid range
4. Check controller logs for rejection reasons
5. Ensure no safety interlocks are active

### State Not Updating
1. Commands succeed but poll `status.xml` to verify
2. Check coordinator refresh interval (default 15s)
3. Manual refresh available via Home Assistant UI
4. Some changes may take multiple poll cycles to reflect

### Integration Logs
Enable debug logging in configuration.yaml:
```yaml
logger:
  default: info
  logs:
    custom_components.rixens: debug
```

## Future Enhancements

Potential improvements for consideration:
- Response body validation from interface.cgi
- Batch command support for multiple parameter updates
- Command queuing for reliability
- State confirmation after write operations
- Additional parameter discovery from status.xml
- Support for additional ACT IDs as they are identified
