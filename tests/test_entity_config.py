"""Tests for entity configuration and mapping."""

from homeassistant.const import PERCENTAGE, UnitOfTemperature

from custom_components.rixens.entity_config import (
    ENTITY_CONFIGS,
    DeviceClass,
    EntityType,
    get_diagnostic_entities,
    get_entities_by_type,
    get_entity_config,
    get_fault_entity_config,
    get_writable_entities,
)


def test_get_entity_config():
    """Test retrieving entity configuration."""
    config = get_entity_config("currenttemp")
    assert config is not None
    assert config.key == "currenttemp"
    assert config.name == "Current Temperature"
    assert config.entity_type == EntityType.SENSOR
    assert config.icon == "mdi:thermometer"


def test_get_entity_config_missing():
    """Test retrieving non-existent entity."""
    config = get_entity_config("nonexistent")
    assert config is None


def test_temperature_scaling():
    """Test temperature value scaling."""
    config = get_entity_config("currenttemp")
    assert config is not None

    # Raw value 720 should scale to 72.0°F
    scaled = config.scale_value(720)
    assert scaled == 72.0

    # Test with different values
    assert config.scale_value(850) == 85.0
    assert config.scale_value(185) == 18.5


def test_voltage_scaling():
    """Test battery voltage scaling."""
    config = get_entity_config("battv")
    assert config is not None

    # Raw value 136 should scale to 13.6V
    scaled = config.scale_value(136)
    assert scaled == 13.6

    assert config.scale_value(120) == 12.0


def test_no_scaling():
    """Test entities without scaling."""
    config = get_entity_config("currenthumidity")
    assert config is not None

    # No scaling should be applied
    assert config.scale_value(45) == 45
    assert config.scale_value(100) == 100


def test_get_entities_by_type_sensor():
    """Test filtering entities by sensor type."""
    sensors = get_entities_by_type(EntityType.SENSOR)

    assert "currenttemp" in sensors
    assert "currenthumidity" in sensors
    assert "heaterstate" in sensors

    # Should not include numbers or switches
    assert "setpoint" not in sensors
    assert "fanspeed" not in sensors
    assert "engineenable" not in sensors


def test_get_entities_by_type_number():
    """Test filtering entities by number type."""
    numbers = get_entities_by_type(EntityType.NUMBER)

    assert "setpoint" in numbers
    assert "fanspeed" in numbers

    # Should not include sensors or switches
    assert "currenttemp" not in numbers
    assert "engineenable" not in numbers


def test_get_entities_by_type_switch():
    """Test filtering entities by switch type."""
    switches = get_entities_by_type(EntityType.SWITCH)

    assert "engineenable" in switches
    assert "electricenable" in switches
    assert "floorenable" in switches
    assert "glycol" in switches

    # Should not include sensors or numbers
    assert "currenttemp" not in switches
    assert "setpoint" not in switches


def test_get_writable_entities():
    """Test retrieving writable entities."""
    writable = get_writable_entities()

    # All numbers should be writable
    assert "setpoint" in writable
    assert "fanspeed" in writable

    # All switches should be writable
    assert "engineenable" in writable
    assert "electricenable" in writable

    # Read-only sensors should not be writable
    assert "currenttemp" not in writable
    assert "currenthumidity" not in writable


def test_get_diagnostic_entities():
    """Test retrieving diagnostic entities."""
    diagnostics = get_diagnostic_entities()

    assert "infra_ip" in diagnostics
    assert "infra_netup" in diagnostics
    assert "runtime" in diagnostics
    assert "altitude" in diagnostics

    # Regular entities should not be diagnostic
    assert "currenttemp" not in diagnostics
    assert "setpoint" not in diagnostics


def test_writable_entity_act_ids():
    """Test that writable entities have ACT IDs."""
    writable = get_writable_entities()

    for key, config in writable.items():
        assert config.act_id is not None, f"Writable entity {key} missing act_id"
        assert config.is_writable


def test_number_entity_ranges():
    """Test that number entities have valid ranges."""
    numbers = get_entities_by_type(EntityType.NUMBER)

    for key, config in numbers.items():
        assert config.min_value is not None, f"Number {key} missing min_value"
        assert config.max_value is not None, f"Number {key} missing max_value"
        assert config.step is not None, f"Number {key} missing step"
        assert config.min_value < config.max_value, f"Number {key} has invalid range"


def test_setpoint_configuration():
    """Test setpoint entity configuration."""
    config = get_entity_config("setpoint")
    assert config is not None

    assert config.entity_type == EntityType.NUMBER
    assert config.scaling_factor == 10.0
    assert config.min_value == 9.0
    assert config.max_value == 22.0
    assert config.step == 0.1
    assert config.act_id == 101
    assert config.unit == UnitOfTemperature.CELSIUS
    assert config.device_class == DeviceClass.TEMPERATURE


def test_fanspeed_configuration():
    """Test fan speed entity configuration."""
    config = get_entity_config("fanspeed")
    assert config is not None

    assert config.entity_type == EntityType.NUMBER
    assert config.scaling_factor == 1.0  # No scaling
    assert config.min_value == 0
    assert config.max_value == 100
    assert config.step == 1
    assert config.act_id == 102
    assert config.unit == PERCENTAGE


def test_switch_act_ids():
    """Test switch entity ACT IDs."""
    expected_act_ids = {
        "engineenable": 201,
        "electricenable": 202,
        "floorenable": 203,
        "glycol": 204,
        "fanenabled": 205,
        "thermenabled": 206,
    }

    for key, expected_act_id in expected_act_ids.items():
        config = get_entity_config(key)
        assert config is not None
        assert config.act_id == expected_act_id
        assert config.entity_type == EntityType.SWITCH


def test_all_entities_have_icons():
    """Test that all entities have icons defined."""
    for key, config in ENTITY_CONFIGS.items():
        assert config.icon is not None, f"Entity {key} missing icon"
        assert config.icon.startswith("mdi:"), f"Entity {key} has invalid icon format"


def test_all_entities_have_names():
    """Test that all entities have human-readable names."""
    for key, config in ENTITY_CONFIGS.items():
        assert config.name, f"Entity {key} missing name"
        assert len(config.name) > 0


def test_fault_entity_config():
    """Test dynamic fault entity configuration."""
    config = get_fault_entity_config("AF")

    assert config.key == "fault_AF"
    assert config.name == "Fault AF"
    assert config.entity_type == EntityType.SENSOR
    assert config.icon == "mdi:alert-circle-outline"

    # Test with different fault code
    config2 = get_fault_entity_config("BF")
    assert config2.key == "fault_BF"
    assert config2.name == "Fault BF"


def test_scale_value_with_none():
    """Test scaling with None value."""
    config = get_entity_config("currenttemp")
    assert config is not None

    scaled = config.scale_value(None)
    assert scaled is None


def test_scale_value_with_non_numeric():
    """Test scaling with non-numeric value."""
    config = get_entity_config("currenttemp")
    assert config is not None

    # String values should be returned as-is
    scaled = config.scale_value("test")
    assert scaled == "test"


def test_entity_device_classes():
    """Test that appropriate entities have device classes."""
    # Temperature sensors should have temperature device class
    temp_entities = ["currenttemp", "enginetemp", "floortemp"]
    for key in temp_entities:
        config = get_entity_config(key)
        assert config is not None
        assert config.device_class == DeviceClass.TEMPERATURE

    # Humidity sensor should have humidity device class
    config = get_entity_config("currenthumidity")
    assert config is not None
    assert config.device_class == DeviceClass.HUMIDITY

    # Voltage sensor should have voltage device class
    config = get_entity_config("battv")
    assert config is not None
    assert config.device_class == DeviceClass.VOLTAGE


def test_entity_units():
    """Test that entities have correct units."""
    # Temperature entities
    temp_entities = ["currenttemp", "enginetemp", "floortemp", "setpoint"]
    for key in temp_entities:
        config = get_entity_config(key)
        assert config is not None
        assert config.unit == UnitOfTemperature.CELSIUS

    # Humidity
    config = get_entity_config("currenthumidity")
    assert config is not None
    assert config.unit == PERCENTAGE

    # Fan speed
    config = get_entity_config("fanspeed")
    assert config is not None
    assert config.unit == PERCENTAGE
