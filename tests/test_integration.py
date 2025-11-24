"""Integration test for entity mapping with simulated XML data."""

from custom_components.rixens.api import RixensApiClient


def test_xml_parsing_with_entity_config():
    """Test that XML parsing works with entity configuration."""
    # Sample XML from controller
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<status>
  <currenttemp>720</currenttemp>
  <setpoint>185</setpoint>
  <currenthumidity>45</currenthumidity>
  <fanspeed>75</fanspeed>
  <engineenable>1</engineenable>
  <electricenable>0</electricenable>
  <floorenable>1</floorenable>
  <heaterstate>3</heaterstate>
  <battv>136</battv>
  <infra_ip>192.168.1.100</infra_ip>
  <runtime>345600</runtime>
  <heater1-faults>
    <fault>
      <name>AF</name>
      <value>0</value>
    </fault>
    <fault>
      <name>CF</name>
      <value>1</value>
    </fault>
  </heater1-faults>
</status>"""

    # Parse XML using the existing parser
    api = RixensApiClient("test-host", None)
    parsed_data = api._parse_xml(xml_data)

    # Verify parsed data structure
    assert parsed_data["currenttemp"] == 720
    assert parsed_data["setpoint"] == 185
    assert parsed_data["currenthumidity"] == 45
    assert parsed_data["fanspeed"] == 75
    assert parsed_data["engineenable"] == 1
    assert parsed_data["electricenable"] == 0
    assert parsed_data["floorenable"] == 1
    assert parsed_data["heaterstate"] == 3
    assert parsed_data["battv"] == 136
    assert parsed_data["infra_ip"] == "192.168.1.100"
    assert parsed_data["runtime"] == 345600
    assert parsed_data["fault_AF"] == 0
    assert parsed_data["fault_CF"] == 1


def test_entity_scaling_integration():
    """Test that entity scaling works with parsed data."""
    from custom_components.rixens.entity_config import get_entity_config

    # Simulate parsed data
    parsed_data = {
        "currenttemp": 720,
        "setpoint": 185,
        "battv": 136,
        "fanspeed": 75,
    }

    # Test temperature scaling
    temp_config = get_entity_config("currenttemp")
    assert temp_config.scale_value(parsed_data["currenttemp"]) == 72.0

    # Test setpoint scaling
    setpoint_config = get_entity_config("setpoint")
    assert setpoint_config.scale_value(parsed_data["setpoint"]) == 18.5

    # Test voltage scaling
    voltage_config = get_entity_config("battv")
    assert voltage_config.scale_value(parsed_data["battv"]) == 13.6

    # Test no scaling (fan speed)
    fan_config = get_entity_config("fanspeed")
    assert fan_config.scale_value(parsed_data["fanspeed"]) == 75


def test_entity_type_distribution():
    """Test that entities are correctly distributed across platforms."""
    from custom_components.rixens.entity_config import EntityType, get_entities_by_type

    sensors = get_entities_by_type(EntityType.SENSOR)
    numbers = get_entities_by_type(EntityType.NUMBER)
    switches = get_entities_by_type(EntityType.SWITCH)

    # Verify we have entities in each category
    assert len(sensors) > 0
    assert len(numbers) > 0
    assert len(switches) > 0

    # Verify expected entities are in correct categories
    assert "currenttemp" in sensors
    assert "currenthumidity" in sensors
    assert "heaterstate" in sensors

    assert "setpoint" in numbers
    assert "fanspeed" in numbers

    assert "engineenable" in switches
    assert "electricenable" in switches
    assert "floorenable" in switches


def test_writable_entity_act_ids():
    """Test that all writable entities have ACT IDs for control."""
    from custom_components.rixens.entity_config import get_writable_entities

    writable = get_writable_entities()

    # Expected ACT ID mappings
    expected = {
        "setpoint": 101,
        "fanspeed": 102,
        "engineenable": 201,
        "electricenable": 202,
        "floorenable": 203,
        "glycol": 204,
        "fanenabled": 205,
        "thermenabled": 206,
    }

    for key, expected_act_id in expected.items():
        assert key in writable, f"Writable entity {key} not found"
        assert (
            writable[key].act_id == expected_act_id
        ), f"Wrong ACT ID for {key}: expected {expected_act_id}, got {writable[key].act_id}"


def test_number_entity_value_reversal():
    """Test that scaled values can be converted back to raw for writes."""
    from custom_components.rixens.entity_config import get_entity_config

    # Test setpoint: user sets 19.5°C, should send 195 to controller
    setpoint_config = get_entity_config("setpoint")
    user_value = 19.5
    raw_value = int(user_value * setpoint_config.scaling_factor)
    assert raw_value == 195

    # Test fanspeed: user sets 80%, should send 80 to controller
    fan_config = get_entity_config("fanspeed")
    user_value = 80
    raw_value = int(user_value * fan_config.scaling_factor)
    assert raw_value == 80


def test_all_entities_have_required_attributes():
    """Test that all entity configs have required attributes."""
    from custom_components.rixens.entity_config import ENTITY_CONFIGS

    for key, config in ENTITY_CONFIGS.items():
        # All entities must have
        assert config.key, f"{key} missing key"
        assert config.name, f"{key} missing name"
        assert config.entity_type, f"{key} missing entity_type"
        assert config.icon, f"{key} missing icon"
        assert config.icon.startswith("mdi:"), f"{key} has invalid icon format"

        # Numbers must have range
        if config.entity_type.value == "number":
            assert config.min_value is not None, f"{key} missing min_value"
            assert config.max_value is not None, f"{key} missing max_value"
            assert config.step is not None, f"{key} missing step"

        # Writable entities must have ACT ID
        if config.entity_type.value in ["number", "switch"]:
            assert config.act_id is not None, f"{key} missing act_id"
