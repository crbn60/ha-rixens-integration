"""Tests for the Rixens number platform (fan speed slider)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.rixens.const import FAN_SPEED_MAX, FAN_SPEED_MIN
from custom_components.rixens.number import RixensFanSpeed

from .conftest import make_rixens_data


class TestFanSpeedInit:
    """Tests for fan speed entity initialization."""

    def test_unique_id(self, mock_coordinator):
        entity = RixensFanSpeed(mock_coordinator)
        assert entity._attr_unique_id == "test_entry_id_fan_speed"

    def test_attributes(self, mock_coordinator):
        entity = RixensFanSpeed(mock_coordinator)
        assert entity._attr_native_min_value == FAN_SPEED_MIN
        assert entity._attr_native_max_value == FAN_SPEED_MAX


class TestIsAutoMode:
    """Tests for auto mode detection."""

    def test_auto_string(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Auto")
        entity = RixensFanSpeed(mock_coordinator)
        assert entity._is_auto_mode() is True

    def test_off_string(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Off")
        entity = RixensFanSpeed(mock_coordinator)
        assert entity._is_auto_mode() is True

    def test_manual_mode(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="50")
        entity = RixensFanSpeed(mock_coordinator)
        assert entity._is_auto_mode() is False

    def test_no_data(self, mock_coordinator):
        mock_coordinator.data = None
        entity = RixensFanSpeed(mock_coordinator)
        assert entity._is_auto_mode() is False


class TestNativeValue:
    """Tests for the native_value property."""

    def test_no_data(self, mock_coordinator):
        mock_coordinator.data = None
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value is None

    def test_auto_mode_returns_pid_speed(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Auto", pid_speed=73)
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value == 73

    def test_auto_mode_pid_zero(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Auto", pid_speed=0)
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value == 0

    def test_auto_mode_pid_clamped_to_min(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Auto", pid_speed=5)
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value == FAN_SPEED_MIN

    def test_auto_mode_pid_clamped_to_max(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Auto", pid_speed=150)
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value == FAN_SPEED_MAX

    def test_manual_mode_returns_setpoint(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="50")
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value == 50

    def test_manual_mode_invalid_speed(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="invalid")
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value is None

    def test_manual_mode_clamped_to_min(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="5")
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.native_value == FAN_SPEED_MIN


class TestExtraAttributes:
    """Tests for extra state attributes."""

    def test_no_data(self, mock_coordinator):
        mock_coordinator.data = None
        entity = RixensFanSpeed(mock_coordinator)
        assert entity.extra_state_attributes == {}

    def test_auto_mode_attributes(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="Auto", pid_speed=73)
        entity = RixensFanSpeed(mock_coordinator)
        attrs = entity.extra_state_attributes
        assert attrs["mode"] == "auto"
        assert attrs["actual_speed"] == 73
        assert "configured_speed" not in attrs

    def test_manual_mode_attributes(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="50", pid_speed=48)
        entity = RixensFanSpeed(mock_coordinator)
        attrs = entity.extra_state_attributes
        assert attrs["mode"] == "manual"
        assert attrs["actual_speed"] == 48
        assert attrs["configured_speed"] == 50

    def test_manual_mode_invalid_speed_no_configured(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_speed="bad")
        entity = RixensFanSpeed(mock_coordinator)
        attrs = entity.extra_state_attributes
        assert attrs["mode"] == "manual"
        assert "configured_speed" not in attrs


class TestSetNativeValue:
    """Tests for setting the fan speed."""

    async def test_set_value(self, mock_coordinator):
        entity = RixensFanSpeed(mock_coordinator)
        await entity.async_set_native_value(60.0)
        mock_coordinator.api.set_fan_speed.assert_awaited_once_with(60)
        mock_coordinator.async_request_refresh.assert_awaited()
