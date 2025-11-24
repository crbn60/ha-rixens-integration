"""Switch platform for Rixens (enable/disable sources)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RixensDataCoordinator
from .entity_config import EntityType, get_entities_by_type


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Rixens switch entities."""
    coordinator: RixensDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RixensSwitch] = []

    # Get all switch configurations from entity_config
    switch_configs = get_entities_by_type(EntityType.SWITCH)

    # Create entities for configured switches that exist in data
    for key, config in switch_configs.items():
        if key in coordinator.data:
            entities.append(RixensSwitch(coordinator, entry, config))

    async_add_entities(entities)


class RixensSwitch(CoordinatorEntity[RixensDataCoordinator], SwitchEntity):
    """Rixens switch entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: RixensDataCoordinator, entry: ConfigEntry, config
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
        """Return true if switch is on."""
        return bool(self.coordinator.data.get(self._config.key))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if (
            self._config.act_id is not None
            and await self.coordinator.api.async_set_value(self._config.act_id, 1)
        ):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if (
            self._config.act_id is not None
            and await self.coordinator.api.async_set_value(self._config.act_id, 0)
        ):
            await self.coordinator.async_request_refresh()
