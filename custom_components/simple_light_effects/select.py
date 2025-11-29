from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EffectModeSelect(coordinator, entry.title)])

class EffectModeSelect(SelectEntity):
    def __init__(self, coordinator, name):
        self._coordinator = coordinator
        self._attr_name = f"{name} Mode Effet"
        self._attr_unique_id = f"{coordinator.light_id}_effect_mode"
        self._attr_options = ["Arrêt", "Bougie", "Stroboscope", "Phare"] # Ajoutez les autres ici
        self._attr_current_option = "Arrêt"
        self._attr_icon = "mdi:creation"

    async def async_select_option(self, option: str) -> None:
        """Appelé quand l'utilisateur change le menu"""
        self._attr_current_option = option
        await self._coordinator.update_settings(effect=option)
        self.async_write_ha_state() # Met à jour l'interface