"""Tests for the Rixens switch platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.rixens.switch import (
    SWITCH_DESCRIPTIONS,
    RixensSwitch,
    RixensSwitchEntityDescription,
)

from .conftest import make_rixens_data


class TestSwitchDescriptions:
    """Tests for switch entity descriptions."""

    def test_all_descriptions_have_required_fns(self):
        for desc in SWITCH_DESCRIPTIONS:
            assert callable(desc.value_fn)
            assert callable(desc.turn_on_fn)
            assert callable(desc.turn_off_fn)

    def test_description_keys_unique(self):
        keys = [d.key for d in SWITCH_DESCRIPTIONS]
        assert len(keys) == len(set(keys))


class TestSwitchEntity:
    """Tests for the RixensSwitch entity class."""

    def _make_switch(self, mock_coordinator, key: str = "furnace"):
        desc = next(d for d in SWITCH_DESCRIPTIONS if d.key == key)
        return RixensSwitch(mock_coordinator, desc)

    def test_unique_id(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator)
        assert switch._attr_unique_id == "test_entry_id_furnace"

    # --- Furnace ---

    def test_furnace_on(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(furnace_src=2)
        switch = self._make_switch(mock_coordinator, "furnace")
        assert switch.is_on is True

    def test_furnace_off(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(furnace_src=0)
        switch = self._make_switch(mock_coordinator, "furnace")
        assert switch.is_on is False

    async def test_furnace_turn_on(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "furnace")
        await switch.async_turn_on()
        mock_coordinator.api.set_furnace.assert_awaited_once_with(True)
        mock_coordinator.async_request_refresh.assert_awaited()

    async def test_furnace_turn_off(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "furnace")
        await switch.async_turn_off()
        mock_coordinator.api.set_furnace.assert_awaited_once_with(False)

    # --- Floor heat ---

    def test_floor_heat_on(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(floor_src=2)
        switch = self._make_switch(mock_coordinator, "floor_heat")
        assert switch.is_on is True

    def test_floor_heat_off(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(floor_src=0)
        switch = self._make_switch(mock_coordinator, "floor_heat")
        assert switch.is_on is False

    async def test_floor_heat_turn_on(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "floor_heat")
        await switch.async_turn_on()
        mock_coordinator.api.set_floor_heat.assert_awaited_once_with(True)

    async def test_floor_heat_turn_off(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "floor_heat")
        await switch.async_turn_off()
        mock_coordinator.api.set_floor_heat.assert_awaited_once_with(False)

    # --- Electric heat ---

    def test_electric_heat_on(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(electric_src=1)
        switch = self._make_switch(mock_coordinator, "electric_heat")
        assert switch.is_on is True

    def test_electric_heat_off(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(electric_src=0)
        switch = self._make_switch(mock_coordinator, "electric_heat")
        assert switch.is_on is False

    async def test_electric_heat_turn_on(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "electric_heat")
        await switch.async_turn_on()
        mock_coordinator.api.set_electric_heat.assert_awaited_once_with(True)

    async def test_electric_heat_turn_off(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "electric_heat")
        await switch.async_turn_off()
        mock_coordinator.api.set_electric_heat.assert_awaited_once_with(False)

    # --- Fan ---

    def test_fan_on(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_state=True)
        switch = self._make_switch(mock_coordinator, "fan")
        assert switch.is_on is True

    def test_fan_off(self, mock_coordinator):
        mock_coordinator.data = make_rixens_data(fan_state=False)
        switch = self._make_switch(mock_coordinator, "fan")
        assert switch.is_on is False

    async def test_fan_turn_on(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "fan")
        await switch.async_turn_on()
        mock_coordinator.api.set_fan.assert_awaited_once_with(True)

    async def test_fan_turn_off(self, mock_coordinator):
        switch = self._make_switch(mock_coordinator, "fan")
        await switch.async_turn_off()
        mock_coordinator.api.set_fan.assert_awaited_once_with(False)

    # --- No data ---

    def test_is_on_no_data(self, mock_coordinator):
        mock_coordinator.data = None
        switch = self._make_switch(mock_coordinator, "furnace")
        assert switch.is_on is None

    def test_all_switches_instantiate(self, mock_coordinator):
        """Verify all switch descriptions can create entities."""
        for desc in SWITCH_DESCRIPTIONS:
            switch = RixensSwitch(mock_coordinator, desc)
            assert switch.is_on is not None or mock_coordinator.data is None
