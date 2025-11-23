from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from .const import DOMAIN

SENSORS = {
    "currenttemp": ("Temperature", "°C", SensorDeviceClass.TEMPERATURE, 10),
    "battv": ("Battery Voltage", "V", SensorDeviceClass.VOLTAGE, 10),
    "flametemp": ("Flame Temperature", "°C", SensorDeviceClass.TEMPERATURE, 100),
    "currenthumidity": ("Humidity", "%", SensorDeviceClass.HUMIDITY, 100),
    "uptime": ("Uptime", "s", None, 1),
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Backwards compatibility for YAML-style setup: coordinator stored at hass.data[DOMAIN]
    coordinator = hass.data.get(DOMAIN)
    if not coordinator:
        _LOGGER = __import__("logging").getLogger(__name__)
        _LOGGER.warning("No coordinator found in hass.data for legacy platform setup")
        return
    entities = []
    for key, (name, unit, dev_class, divider) in SENSORS.items():
        entities.append(RixensSensor(coordinator, key, name, unit, dev_class, divider))
    async_add_entities(entities)


async def async_setup_entry(hass, entry, async_add_entities):
    # New-style setup using config entries. Coordinator is stored at hass.data[DOMAIN][entry.entry_id]
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for key, (name, unit, dev_class, divider) in SENSORS.items():
        entities.append(RixensSensor(coordinator, key, name, unit, dev_class, divider))
    async_add_entities(entities)


class RixensSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, key, name, unit, dev_class, divider):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dev_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._divider = divider
        self._attr_unique_id = f"rixens_{key}"

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._key)
        if raw is not None:
            try:
                return float(raw) / self._divider
            except ValueError:
                return None
        return None
