"""Tests for the Rixens binary sensor platform."""

from __future__ import annotations

import pytest

from custom_components.rixens.binary_sensor import RixensConnectionSensor


class TestConnectionSensor:
    """Tests for the connection binary sensor."""

    def test_unique_id(self, mock_coordinator):
        sensor = RixensConnectionSensor(mock_coordinator)
        assert sensor._attr_unique_id == "test_entry_id_connection"

    def test_translation_key(self, mock_coordinator):
        sensor = RixensConnectionSensor(mock_coordinator)
        assert sensor._attr_translation_key == "connection"

    def test_is_on_when_available(self, mock_coordinator):
        mock_coordinator.is_available = True
        sensor = RixensConnectionSensor(mock_coordinator)
        assert sensor.is_on is True

    def test_is_on_when_unavailable(self, mock_coordinator):
        mock_coordinator.is_available = False
        sensor = RixensConnectionSensor(mock_coordinator)
        assert sensor.is_on is False

    def test_always_available(self, mock_coordinator):
        sensor = RixensConnectionSensor(mock_coordinator)
        assert sensor.available is True
