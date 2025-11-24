# Entity Mapping Documentation

This document describes the entity mapping system for the Rixens MCS7 integration, which parses `status.xml` and creates Home Assistant entities.

## Architecture Overview

The entity mapping system is centralized in `entity_config.py`, which serves as the single source of truth for all entity definitions. This module defines:

1. **Entity Types**: Sensor (read-only), Number (writable numeric), Switch (writable boolean)
2. **Scaling Factors**: Convert raw XML values to proper units
3. **Icons**: Visual representation for each entity
4. **Device Classes**: Semantic classification for Home Assistant
5. **ACT IDs**: Command identifiers for writable entities

## Entity Configuration Structure

Each entity is defined using the `EntityConfig` dataclass with the following attributes:

```python
@dataclass
class EntityConfig:
    key: str                    # XML parameter key
    name: str                   # Human-readable name
    entity_type: EntityType     # sensor, number, or switch
    icon: str                   # MDI icon identifier
    device_class: DeviceClass   # Optional semantic class
    unit: str | None            # Unit of measurement
    scaling_factor: float       # Divisor for raw value
    value_transform: Callable   # Optional custom transform
    min_value: float            # For number entities
    max_value: float            # For number entities
    step: float                 # For number entities
    act_id: int | None          # Command ID for writes
    diagnostic: bool            # Diagnostic entity flag
```

## Entity Categories

### 1. Temperature Sensors (Read-Only)

Temperature values from the controller are raw integers that must be divided by 10 to get Celsius values.

| Key | Name | Raw Value | Scaled Value | Formula |
|-----|------|-----------|--------------|---------|
| currenttemp | Current Temperature | 720 | 72.0°C | raw / 10 |
| enginetemp | Engine Temperature | 850 | 85.0°C | raw / 10 |
| floortemp | Floor Temperature | 680 | 68.0°C | raw / 10 |
| setpoint | Setpoint | 185 | 18.5°C | raw / 10 |

**Scaling Factor**: `10.0`  
**Device Class**: `temperature`  
**Unit**: `°C` (UnitOfTemperature.FAHRENHEIT)  
**Icon**: `mdi:thermometer` (or context-specific)

### 2. Humidity Sensor (Read-Only)

| Key | Name | Unit | Icon |
|-----|------|------|------|
| currenthumidity | Current Humidity | % | mdi:water-percent |

**Scaling Factor**: `1.0` (no scaling)  
**Device Class**: `humidity`

### 3. Number Entities (Writable)

Number entities allow setting numeric values with range constraints.

| Key | Name | Range (Scaled) | Step | ACT ID | Unit |
|-----|------|----------------|------|--------|------|
| setpoint | Setpoint | 9.0 - 22.0°C | 0.1 | 101 | °C |
| fanspeed | Fan Speed | 0 - 100% | 1 | 102 | % |

**Notes**:
- Setpoint values are scaled (raw range 90-220 → 9.0-22.0°C)
- Fan speed is direct percentage (0-100)
- Changes are sent via `interface.cgi?act=<ACT>&val=<value>`

### 4. Switch Entities (Writable)

Switches control boolean states (0=off, 1=on).

| Key | Name | ACT ID | Icon |
|-----|------|--------|------|
| engineenable | Engine Enable | 201 | mdi:engine |
| electricenable | Electric Enable | 202 | mdi:flash |
| floorenable | Floor Enable | 203 | mdi:floor-plan |
| glycol | Glycol Mode | 204 | mdi:water-circle |
| fanenabled | Fan Enabled | 205 | mdi:fan |
| thermenabled | Thermostat Enabled | 206 | mdi:thermostat |

**Values**: 0 (off) or 1 (on)  
**Command**: `interface.cgi?act=<ACT>&val=<0|1>`

### 5. Status Sensors (Read-Only)

| Key | Name | Icon | Description |
|-----|------|------|-------------|
| heaterstate | Heater State Code | mdi:fire | Current operational state |
| glowpin | Glow Pin State | mdi:flash-outline | Ignition system status |

### 6. Electrical Sensors (Read-Only)

Battery voltage requires scaling (divide by 10 to get volts).

| Key | Name | Raw Value | Scaled Value | Formula |
|-----|------|-----------|--------------|---------|
| battv | Battery Voltage | 136 | 13.6V | raw / 10 |

**Scaling Factor**: `10.0`  
**Device Class**: `voltage`  
**Unit**: `V` (UnitOfElectricPotential.VOLT)  
**Icon**: `mdi:car-battery`

### 7. Diagnostic Entities (Read-Only)

Diagnostic entities are hidden by default but available for troubleshooting.

| Key | Name | Icon | Diagnostic |
|-----|------|------|-----------|
| infra_ip | Infrastructure IP | mdi:ip-network | ✅ |
| infra_netup | Network Status | mdi:network | ✅ |
| infra_dhcp | DHCP Status | mdi:network-outline | ✅ |
| altitude | Altitude | mdi:elevation-rise | ✅ |
| runtime | Heater Runtime | mdi:timer-outline | ✅ |

### 8. Fault Sensors (Dynamic, Read-Only)

Fault sensors are created dynamically based on the `<heater1-faults>` section in status.xml.

**XML Structure**:
```xml
<heater1-faults>
  <fault>
    <name>AF</name>
    <value>0</value>
  </fault>
  <fault>
    <name>BF</name>
    <value>1</value>
  </fault>
</heater1-faults>
```

**Entity Pattern**: `fault_<NAME>`  
**Icon**: `mdi:alert-circle-outline`  
**Values**: 0 (no fault) or 1 (fault active)

Examples: `fault_AF`, `fault_BF`, `fault_CF`

## Icon Reference

Icons follow Material Design Icons (MDI) standards:

| Category | Icon | Usage |
|----------|------|-------|
| Temperature | mdi:thermometer | General temperature sensors |
| Engine | mdi:engine | Engine-related entities |
| Electric | mdi:flash | Electrical heater/components |
| Floor | mdi:floor-plan | Floor heating system |
| Fan | mdi:fan | Fan control |
| Thermostat | mdi:thermostat | Temperature control |
| Fire | mdi:fire | Heater state |
| Battery | mdi:car-battery | Battery voltage |
| Network | mdi:ip-network | Network diagnostics |
| Humidity | mdi:water-percent | Humidity sensor |
| Alert | mdi:alert-circle-outline | Fault indicators |
| Water | mdi:water-circle | Glycol/fluid systems |
| Timer | mdi:timer-outline | Runtime counters |
| Ignition | mdi:flash-outline | Glow pin/ignition |

## Usage in Platform Code

### Sensor Platform

```python
from .entity_config import get_entity_config, EntityType

# Get sensor configuration
config = get_entity_config("currenttemp")
if config and config.entity_type == EntityType.SENSOR:
    # Create sensor entity with scaling
    scaled_value = config.scale_value(raw_value)
```

### Number Platform

```python
from .entity_config import get_entities_by_type, EntityType

# Get all number entities
number_configs = get_entities_by_type(EntityType.NUMBER)
for key, config in number_configs.items():
    # Use config.min_value, max_value, step, act_id
```

### Switch Platform

```python
from .entity_config import get_entities_by_type, EntityType

# Get all switch entities
switch_configs = get_entities_by_type(EntityType.SWITCH)
for key, config in switch_configs.items():
    # Use config.act_id for commands
```

## Adding New Entities

To add a new entity:

1. Determine the entity type (sensor, number, or switch)
2. Check if the value needs scaling (e.g., temperatures, voltages)
3. Select an appropriate icon from MDI
4. Assign device class if applicable (temperature, humidity, etc.)
5. For writable entities, determine the ACT command ID
6. Add entry to `ENTITY_CONFIGS` in `entity_config.py`

Example:
```python
"newtemp": EntityConfig(
    key="newtemp",
    name="New Temperature",
    entity_type=EntityType.SENSOR,
    icon="mdi:thermometer",
    device_class=DeviceClass.TEMPERATURE,
    unit=UnitOfTemperature.FAHRENHEIT,
    scaling_factor=10.0,
),
```

## Scaling Reference

| Measurement | Raw Unit | Scaled Unit | Factor | Example |
|-------------|----------|-------------|--------|---------|
| Temperature | raw int | Celsius | ÷ 10 | 720 → 72.0°C |
| Voltage | 0.1V | Volts | ÷ 10 | 136 → 13.6V |
| Percentage | % | % | ÷ 1 | 45 → 45% |
| Boolean | 0/1 | on/off | — | 1 → on |

## Command Reference (ACT IDs)

Commands are sent via: `http://<host>/interface.cgi?act=<ACT>&val=<VALUE>`

| ACT ID | Parameter | Type | Valid Values | Description |
|--------|-----------|------|--------------|-------------|
| 101 | setpoint | number | 90-220 (raw) | Temperature setpoint |
| 102 | fanspeed | number | 0-100 | Fan speed percentage |
| 201 | engineenable | switch | 0, 1 | Engine heat source |
| 202 | electricenable | switch | 0, 1 | Electric heater |
| 203 | floorenable | switch | 0, 1 | Floor heating loop |
| 204 | glycol | switch | 0, 1 | Glycol mode |
| 205 | fanenabled | switch | 0, 1 | Master fan control |
| 206 | thermenabled | switch | 0, 1 | Thermostat logic |

## XML Parsing Flow

1. API fetches `status.xml` from controller
2. XML is parsed into flat dictionary (nested faults handled separately)
3. Each key is looked up in `ENTITY_CONFIGS`
4. If config exists, entity is created with:
   - Scaled value (if scaling_factor ≠ 1.0)
   - Proper unit and device class
   - Correct icon
   - Write capability (if act_id present)
5. Fault sensors are dynamically created from `<heater1-faults>` section

## Testing Entity Configuration

Test that entity config works correctly:

```python
from entity_config import get_entity_config

# Test scaling
config = get_entity_config("currenttemp")
assert config.scale_value(720) == 72.0

# Test type filtering
from entity_config import get_entities_by_type, EntityType
sensors = get_entities_by_type(EntityType.SENSOR)
assert "currenttemp" in sensors

# Test writable detection
assert config.act_id == 101  # For setpoint
assert config.is_writable
```

## Maintenance Notes

- Always update both `ENTITY_CONFIGS` and this documentation when adding entities
- Test scaling factors with actual controller values
- Verify ACT IDs before deployment (incorrect commands could affect heating)
- Keep icons consistent with entity function
- Use diagnostic flag for troubleshooting-only entities
- Document any unusual scaling or transformation logic

## Future Enhancements

Potential improvements to the mapping system:

1. **State-dependent icons**: Change icon based on entity state (e.g., fan spinning vs. stopped)
2. **Dynamic device classes**: Automatically assign device class based on unit
3. **Validation**: Range checking on writes before sending to controller
4. **Localization**: Translate entity names based on language
5. **Entity categories**: Group related entities (heating, cooling, diagnostics)
6. **Value templates**: Complex transformations beyond simple scaling
7. **Binary sensors**: Convert numeric fault codes to binary on/off sensors
