from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        EffectSpeedNumber(coordinator, entry.title),
        EffectIntensityNumber(coordinator, entry.title)
    ])

class EffectSpeedNumber(NumberEntity):
    def __init__(self, coordinator, name):
        self._coordinator = coordinator
        self._attr_name = f"{name} Vitesse Effet"
        self._attr_unique_id = f"{coordinator.light_id}_speed"
        self._attr_native_min_value = 0.1
        self._attr_native_max_value = 5.0
        self._attr_native_step = 0.1
        self._attr_native_value = 1.0
        self._attr_icon = "mdi:speedometer"
        self._attr_native_unit_of_measurement = "s"

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        await self._coordinator.update_settings(speed=value)
        self.async_write_ha_state()

class EffectIntensityNumber(NumberEntity):
    def __init__(self, coordinator, name):
        self._coordinator = coordinator
        self._attr_name = f"{name} Intensité Effet"
        self._attr_unique_id = f"{coordinator.light_id}_intensity"
        self._attr_native_min_value = 10
        self._attr_native_max_value = 100
        self._attr_native_step = 5
        self._attr_native_value = 50
        self._attr_icon = "mdi:brightness-6"
        self._attr_native_unit_of_measurement = "%"

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        await self._coordinator.update_settings(intensity=int(value))
        self.async_write_ha_state()