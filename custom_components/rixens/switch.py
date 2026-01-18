"""Switch platform for Rixens integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import RixensApi, RixensData
from .const import DOMAIN
from .coordinator import RixensCoordinator


@dataclass(frozen=True, kw_only=True)
class RixensSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Rixens switch entity."""

    value_fn: Callable[[RixensData], bool]
    turn_on_fn: Callable[[RixensApi], Awaitable[None]]
    turn_off_fn: Callable[[RixensApi], Awaitable[None]]


SWITCH_DESCRIPTIONS: tuple[RixensSwitchEntityDescription, ...] = (
    RixensSwitchEntityDescription(
        key="furnace",
        translation_key="furnace",
        value_fn=lambda data: data.settings.furnace_src == 2,  # 2 = active
        turn_on_fn=lambda api: api.set_furnace(True),
        turn_off_fn=lambda api: api.set_furnace(False),
    ),
    RixensSwitchEntityDescription(
        key="floor_heat",
        translation_key="floor_heat",
        value_fn=lambda data: data.settings.floor_src == 2,  # 2 = active
        turn_on_fn=lambda api: api.set_floor_heat(True),
        turn_off_fn=lambda api: api.set_floor_heat(False),
    ),
    RixensSwitchEntityDescription(
        key="electric_heat",
        translation_key="electric_heat",
        value_fn=lambda data: data.settings.electric_src == 2,  # 2 = active
        turn_on_fn=lambda api: api.set_electric_heat(True),
        turn_off_fn=lambda api: api.set_electric_heat(False),
    ),
    RixensSwitchEntityDescription(
        key="fan",
        translation_key="fan",
        value_fn=lambda data: data.settings.fan_state,
        turn_on_fn=lambda api: api.set_fan(True),
        turn_off_fn=lambda api: api.set_fan(False),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Rixens switches based on a config entry."""
    coordinator: RixensCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        RixensSwitch(coordinator, description) for description in SWITCH_DESCRIPTIONS
    )


class RixensSwitch(CoordinatorEntity[RixensCoordinator], SwitchEntity):
    """Representation of a Rixens switch."""

    _attr_has_entity_name = True
    entity_description: RixensSwitchEntityDescription

    def __init__(
        self,
        coordinator: RixensCoordinator,
        description: RixensSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        if self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(self.coordinator.api)
        # Trigger burst mode for responsive update
        self.coordinator.trigger_burst_mode()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(self.coordinator.api)
        # Trigger burst mode for responsive update
        self.coordinator.trigger_burst_mode()
        await self.coordinator.async_request_refresh()
