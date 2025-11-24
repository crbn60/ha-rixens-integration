"""Switch platform for Rixens MCS7 controller.

Creates writable switch entities for enabling/disabling heat sources and features.
See const.py for SWITCH_ENTITIES configuration and docs/entity_mapping.md for details.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CMD_MAP, DOMAIN, SWITCH_ENTITIES, SwitchEntityConfig
from .coordinator import RixensDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Rixens switch entities from a config entry."""
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensSwitch] = []
    data = coordinator.data or {}

    # Add configured switch entities that exist in the data
    for config in SWITCH_ENTITIES:
        if config.key in data:
            entities.append(RixensSwitch(coordinator, entry, config))

    async_add_entities(entities)


class RixensSwitch(CoordinatorEntity[RixensDataCoordinator], SwitchEntity):
    """Representation of a Rixens switch entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RixensDataCoordinator,
        entry: ConfigEntry,
        config: SwitchEntityConfig,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{config.key}"
        self._attr_name = config.name
        self._attr_icon = config.icon

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return bool(self.coordinator.data.get(self._config.key))

    @property
    def icon(self) -> str:
        """Return icon based on switch state."""
        if self._config.icon_off and not self.is_on:
            return self._config.icon_off
        return self._config.icon

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        act = CMD_MAP.get(self._config.key)
        if act is not None and await self.coordinator.api.async_set_value(act, 1):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        act = CMD_MAP.get(self._config.key)
        if act is not None and await self.coordinator.api.async_set_value(act, 0):
            await self.coordinator.async_request_refresh()
