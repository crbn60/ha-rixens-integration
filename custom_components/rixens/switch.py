from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CMD_MAP

SWITCHES = {"floorenable": "Floor Heating", "systemheat": "System Heat"}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    coordinator = hass.data[DOMAIN]
    entities = []
    for key, name in SWITCHES.items():
        if key in CMD_MAP:
            entities.append(RixensSwitch(coordinator, key, name, CMD_MAP[key]))
    async_add_entities(entities)


class RixensSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, key, name, action_id):
        super().__init__(coordinator)
        self._key = key
        self._action_id = action_id
        self._attr_name = name
        self._attr_unique_id = f"rixens_{key}"

    @property
    def is_on(self):
        return str(self.coordinator.data.get(self._key)) == "1"

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_parameter(self._action_id, 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_parameter(self._action_id, 0)
        await self.coordinator.async_request_refresh()
