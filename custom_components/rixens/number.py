from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CMD_MAP

NUMBERS = {
    "setpoint": ("Target Temperature", 0, 250, 1),
    "fanspeed": ("Fan Speed", 0, 100, 1),
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    coordinator = hass.data[DOMAIN]
    entities = []
    for key, (name, min_val, max_val, step) in NUMBERS.items():
        if key in CMD_MAP:
            entities.append(
                RixensNumber(
                    coordinator, key, name, min_val, max_val, step, CMD_MAP[key]
                )
            )
    async_add_entities(entities)


class RixensNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, key, name, min_v, max_v, step, action_id):
        super().__init__(coordinator)
        self._key = key
        self._action_id = action_id
        self._attr_name = name
        self._attr_native_min_value = min_v
        self._attr_native_max_value = max_v
        self._attr_native_step = step
        self._attr_unique_id = f"rixens_{key}"

    @property
    def native_value(self):
        try:
            return float(self.coordinator.data.get(self._key))
        except:
            return None

    async def async_set_native_value(self, value):
        await self.coordinator.api.set_parameter(self._action_id, value)
        await self.coordinator.async_request_refresh()
