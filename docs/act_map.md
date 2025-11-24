# ACT Command Mapping

This document maps controller parameters to their ACT IDs for control commands.

## Command Format

Control commands are sent via HTTP GET:
```
http://{host}/interface.cgi?act={ACT_ID}&val={VALUE}
```

## Number Controls (Adjustable Values)

| Parameter | ACT ID | Value Range | Unit | Scaling | Notes |
|-----------|--------|-------------|------|---------|-------|
| `setpoint` | 101 | 500-900 (raw) | °F | ×10 | User enters 50-90°F, sent as 500-900 |
| `fanspeed` | 102 | 0-100 | % | none | Direct percentage |

### Setpoint Example
- User sets: 72.0°F
- Sent command: `interface.cgi?act=101&val=720`
- Controller stores: 720 (raw)
- Display shows: 72.0°F (divided by 10)

## Switch Controls (On/Off)

| Parameter | ACT ID | Off | On | Notes |
|-----------|--------|-----|-----|-------|
| `engineenable` | 201 | 0 | 1 | Engine heat source |
| `electricenable` | 202 | 0 | 1 | Electric heater |
| `floorenable` | 203 | 0 | 1 | Floor heat loop |
| `glycol` | 204 | 0 | 1 | Glycol circulation mode |
| `fanenabled` | 205 | 0 | 1 | Master fan enable |
| `thermenabled` | 206 | 0 | 1 | Thermostat logic enable |

### Switch Example
- Turn on engine heat: `interface.cgi?act=201&val=1`
- Turn off engine heat: `interface.cgi?act=201&val=0`

## Code Reference

ACT IDs are defined in `const.py`:
```python
CMD_MAP: dict[str, int] = {
    "setpoint": 101,
    "fanspeed": 102,
    "engineenable": 201,
    "electricenable": 202,
    "floorenable": 203,
    "glycol": 204,
    "fanenabled": 205,
    "thermenabled": 206,
}
```

## Verification Steps

When adding or modifying ACT mappings:

1. **Test the command**: Send `interface.cgi?act={ACT}&val={VALUE}` directly
2. **Poll status**: Verify change in `status.xml`
3. **Update documentation**: Update this file and `CMD_MAP` in `const.py`
4. **Add tests**: Add test cases for the new command

## Safety Considerations

⚠️ **Warning**: Heating equipment control can be sensitive.

- Always test commands with safe values first
- Verify range limits before sending
- Monitor equipment response after command
- Use appropriate polling intervals (not too frequent)

## Pending Verification

The following ACT IDs may need confirmation:
- None currently - all mappings verified

---

*Last updated: 2025-11-24*
