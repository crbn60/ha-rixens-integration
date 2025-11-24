# Configuration Guide

This guide explains how to configure the Rixens MCS7 integration using the modern Home Assistant UI-based configuration flow.

## Initial Setup

The Rixens integration uses **Config Flow** for setup - no YAML configuration is needed or supported.

### Adding Your First Controller

1. Go to **Settings** → **Devices & Services** in Home Assistant
2. Click the **+ Add Integration** button
3. Search for "Rixens MCS7"
4. Enter the **Host/IP address** of your Rixens MCS7 controller
   - Example: `192.168.1.100` or `mcs7.local`
   - The host/IP cannot be empty
   - Leading/trailing whitespace will be automatically trimmed

5. Click **Submit**

The integration will create a config entry and start polling your controller.

## Multi-Instance Support

You can add **multiple Rixens MCS7 controllers** to Home Assistant:

1. Each controller is added as a separate integration instance
2. Each instance has its own polling interval and options
3. Controllers are identified by their host/IP address (case-insensitive)
4. You cannot add the same controller twice

### Example Multi-Instance Setup

- Controller 1: `192.168.1.100` (garage heater)
- Controller 2: `192.168.1.101` (workshop heater)
- Controller 3: `mcs7-basement.local` (basement heater)

Each instance will have its own set of entities with unique entity IDs.

## Options Configuration

After adding a controller, you can configure advanced options:

1. Go to **Settings** → **Devices & Services**
2. Find your Rixens MCS7 integration
3. Click **Configure** (or the gear icon)

### Available Options

#### Polling Interval

**Default:** 15 seconds  
**Range:** 2-3600 seconds (1 hour)

Controls how often Home Assistant polls the controller for updates.

- **Lower values** (2-10s): More responsive, higher network traffic
- **Moderate values** (15-30s): Balanced (recommended for most users)
- **Higher values** (60-3600s): Less network traffic, slower updates

**Important:** Changes to the polling interval will take effect after saving. The integration will automatically reload with the new interval.

### Validation

The integration validates all inputs:

- **Host/IP:** Cannot be empty or contain only whitespace
- **Polling Interval:** Must be between 2 and 3600 seconds
- **Duplicate Detection:** Same controller cannot be added twice (case-insensitive)

## Entities

Once configured, the integration creates several entities:

### Sensors (Read-Only)
- `sensor.rixens_current_temperature` - Current temperature reading
- `sensor.rixens_current_humidity` - Current humidity reading
- `sensor.rixens_heater_state_code` - Current heater state
- `sensor.rixens_fault_*` - Fault codes (if any)

### Numbers (Read/Write)
- `number.rixens_setpoint` - Temperature setpoint
- `number.rixens_fan_speed` - Fan speed control

### Switches (Read/Write)
- `switch.rixens_engineenable` - Engine heater enable/disable
- `switch.rixens_electricenable` - Electric heater enable/disable
- `switch.rixens_floorenable` - Floor heating enable/disable

## Troubleshooting

### Cannot Add Integration

**Problem:** Integration doesn't appear in the list  
**Solution:** 
- Ensure the integration is properly installed via HACS
- Restart Home Assistant
- Clear browser cache

### Duplicate Controller Error

**Problem:** "This controller is already configured"  
**Solution:** 
- Check if the controller is already added (Settings → Devices & Services)
- Note: Host matching is case-insensitive (`mcs7.local` = `MCS7.LOCAL`)
- If you need to re-add it, remove the existing entry first

### Invalid Polling Interval

**Problem:** "Polling interval must be between 2 and 3600 seconds"  
**Solution:**
- Use a value between 2 and 3600 seconds
- The UI selector should prevent invalid values, but validation is also done server-side

### No Updates from Controller

**Problem:** Entities not updating  
**Solutions:**
- Check that the host/IP is correct and reachable
- Verify the controller is online and responding
- Check Home Assistant logs for connection errors
- Consider increasing the polling interval if network is unstable

## Migration from YAML (Not Applicable)

This integration has **always used Config Flow** and never supported YAML configuration. If you're migrating from another integration, you'll need to:

1. Remove the old integration
2. Add the Rixens MCS7 integration via UI as described above
3. Reconfigure any automations that referenced old entity IDs

## Advanced Topics

### Diagnostics

The integration provides diagnostic information that can help with troubleshooting:

1. Go to **Settings** → **Devices & Services**
2. Find your Rixens MCS7 device
3. Click on the device name
4. Click **Download Diagnostics**

This will provide detailed information about the controller's state and configuration.

### Entity Customization

You can customize entity names, icons, and areas as with any Home Assistant entity:

1. Click on the entity in the UI
2. Click the gear icon
3. Modify the name, icon, or area as desired

### Removing a Controller

To remove a controller:

1. Go to **Settings** → **Devices & Services**
2. Find your Rixens MCS7 integration
3. Click the three dots (⋮) menu
4. Select **Delete**
5. Confirm the deletion

All entities associated with that controller will be removed.
