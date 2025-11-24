"""Tests for entity mapping and scaling functionality."""

from custom_components.rixens.const import (
    FAULT_PREFIX,
    NUMBER_ENTITIES,
    NUMBER_ENTITY_MAP,
    RAW_TEMP_DIVISOR,
    SENSOR_ENTITIES,
    SENSOR_ENTITY_MAP,
    SWITCH_ENTITIES,
    SWITCH_ENTITY_MAP,
    _scale_temp,
    _scale_temp_for_command,
    create_fault_config,
)


class TestScalingFunctions:
    """Test scaling functions for unit conversion."""

    def test_scale_temp_integer(self):
        """Test temperature scaling with integer input."""
        assert _scale_temp(720) == 72.0
        assert _scale_temp(680) == 68.0
        assert _scale_temp(0) == 0.0

    def test_scale_temp_float(self):
        """Test temperature scaling with float input."""
        assert _scale_temp(725.5) == 72.55
        assert _scale_temp(72.5) == 7.25

    def test_scale_temp_invalid(self):
        """Test temperature scaling with invalid input."""
        assert _scale_temp(None) is None
        assert _scale_temp("invalid") is None
        assert _scale_temp([720]) is None

    def test_scale_temp_for_command(self):
        """Test reverse temperature scaling for commands."""
        assert _scale_temp_for_command(72.0) == 720
        assert _scale_temp_for_command(68.0) == 680
        assert _scale_temp_for_command(72.5) == 725

    def test_raw_temp_divisor_value(self):
        """Verify RAW_TEMP_DIVISOR is correct."""
        assert RAW_TEMP_DIVISOR == 10


class TestSensorEntityConfig:
    """Test sensor entity configurations."""

    def test_sensor_entities_exist(self):
        """Test that sensor entities are defined."""
        assert len(SENSOR_ENTITIES) > 0

    def test_current_temp_sensor_config(self):
        """Test current temperature sensor configuration."""
        assert "currenttemp" in SENSOR_ENTITY_MAP
        config = SENSOR_ENTITY_MAP["currenttemp"]
        assert config.name == "Current Temperature"
        assert config.icon == "mdi:thermometer"
        assert config.native_unit == "°F"
        assert config.value_fn is not None
        # Test value scaling
        assert config.value_fn(720) == 72.0

    def test_current_humidity_sensor_config(self):
        """Test current humidity sensor configuration."""
        assert "currenthumidity" in SENSOR_ENTITY_MAP
        config = SENSOR_ENTITY_MAP["currenthumidity"]
        assert config.name == "Current Humidity"
        assert config.icon == "mdi:water-percent"
        assert config.native_unit == "%"

    def test_heater_state_sensor_config(self):
        """Test heater state sensor configuration."""
        assert "heaterstate" in SENSOR_ENTITY_MAP
        config = SENSOR_ENTITY_MAP["heaterstate"]
        assert config.name == "Heater State"
        assert config.icon == "mdi:fire"

    def test_runtime_sensor_config(self):
        """Test runtime sensor configuration."""
        assert "runtime" in SENSOR_ENTITY_MAP
        config = SENSOR_ENTITY_MAP["runtime"]
        assert config.name == "Runtime"
        assert config.native_unit == "s"

    def test_all_sensors_have_icons(self):
        """Test that all sensor entities have icons defined."""
        for config in SENSOR_ENTITIES:
            assert config.icon is not None, f"Sensor {config.key} missing icon"
            assert config.icon.startswith("mdi:"), f"Sensor {config.key} invalid icon"


class TestSwitchEntityConfig:
    """Test switch entity configurations."""

    def test_switch_entities_exist(self):
        """Test that switch entities are defined."""
        assert len(SWITCH_ENTITIES) > 0

    def test_engine_enable_switch_config(self):
        """Test engine enable switch configuration."""
        assert "engineenable" in SWITCH_ENTITY_MAP
        config = SWITCH_ENTITY_MAP["engineenable"]
        assert config.name == "Engine Heat Source"
        assert config.icon == "mdi:engine"

    def test_electric_enable_switch_config(self):
        """Test electric enable switch configuration."""
        assert "electricenable" in SWITCH_ENTITY_MAP
        config = SWITCH_ENTITY_MAP["electricenable"]
        assert config.name == "Electric Heater"
        assert config.icon == "mdi:flash"

    def test_floor_enable_switch_config(self):
        """Test floor enable switch configuration."""
        assert "floorenable" in SWITCH_ENTITY_MAP
        config = SWITCH_ENTITY_MAP["floorenable"]
        assert config.name == "Floor Heat Loop"
        assert config.icon == "mdi:floor-plan"

    def test_fan_enabled_switch_config(self):
        """Test fan enabled switch configuration."""
        assert "fanenabled" in SWITCH_ENTITY_MAP
        config = SWITCH_ENTITY_MAP["fanenabled"]
        assert config.name == "Fan Enabled"
        assert config.icon == "mdi:fan"

    def test_therm_enabled_switch_config(self):
        """Test thermostat enabled switch configuration."""
        assert "thermenabled" in SWITCH_ENTITY_MAP
        config = SWITCH_ENTITY_MAP["thermenabled"]
        assert config.name == "Thermostat Mode"

    def test_all_switches_have_icons(self):
        """Test that all switch entities have icons defined."""
        for config in SWITCH_ENTITIES:
            assert config.icon is not None, f"Switch {config.key} missing icon"
            assert config.icon.startswith("mdi:"), f"Switch {config.key} invalid icon"


class TestNumberEntityConfig:
    """Test number entity configurations."""

    def test_number_entities_exist(self):
        """Test that number entities are defined."""
        assert len(NUMBER_ENTITIES) > 0

    def test_setpoint_number_config(self):
        """Test setpoint number configuration."""
        assert "setpoint" in NUMBER_ENTITY_MAP
        config = NUMBER_ENTITY_MAP["setpoint"]
        assert config.name == "Temperature Setpoint"
        assert config.icon == "mdi:thermostat"
        assert config.native_min == 50.0
        assert config.native_max == 90.0
        assert config.native_step == 0.5
        assert config.native_unit == "°F"
        # Test value scaling
        assert config.value_fn(720) == 72.0
        # Test command scaling
        assert config.command_fn(72.0) == 720

    def test_fanspeed_number_config(self):
        """Test fan speed number configuration."""
        assert "fanspeed" in NUMBER_ENTITY_MAP
        config = NUMBER_ENTITY_MAP["fanspeed"]
        assert config.name == "Fan Speed"
        assert config.icon == "mdi:fan"
        assert config.native_min == 0.0
        assert config.native_max == 100.0
        assert config.native_step == 1.0
        assert config.native_unit == "%"

    def test_all_numbers_have_icons(self):
        """Test that all number entities have icons defined."""
        for config in NUMBER_ENTITIES:
            assert config.icon is not None, f"Number {config.key} missing icon"
            assert config.icon.startswith("mdi:"), f"Number {config.key} invalid icon"


class TestFaultConfig:
    """Test fault sensor configuration."""

    def test_fault_prefix(self):
        """Test fault prefix constant."""
        assert FAULT_PREFIX == "fault_"

    def test_create_fault_config(self):
        """Test fault configuration creation."""
        config = create_fault_config("fault_overtemp")
        assert config.key == "fault_overtemp"
        assert config.name == "Fault OVERTEMP"
        assert config.icon == "mdi:alert-circle-outline"

    def test_create_fault_config_various_names(self):
        """Test fault configuration with various names."""
        config = create_fault_config("fault_flame")
        assert config.name == "Fault FLAME"

        config = create_fault_config("fault_lowpressure")
        assert config.name == "Fault LOWPRESSURE"


class TestEntityPlatformAssignment:
    """Test entity platform assignments."""

    def test_no_overlap_between_platforms(self):
        """Test that no key is assigned to multiple platforms."""
        sensor_keys = set(SENSOR_ENTITY_MAP.keys())
        switch_keys = set(SWITCH_ENTITY_MAP.keys())
        number_keys = set(NUMBER_ENTITY_MAP.keys())

        # No overlap between sensor and switch
        assert not sensor_keys & switch_keys, "Key overlap between sensor and switch"

        # No overlap between sensor and number
        assert not sensor_keys & number_keys, "Key overlap between sensor and number"

        # No overlap between switch and number
        assert not switch_keys & number_keys, "Key overlap between switch and number"
