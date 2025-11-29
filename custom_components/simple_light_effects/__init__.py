import asyncio
import random
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import SERVICE_TURN_ON
from .const import DOMAIN, PLATFORMS, CONF_ENTITY_ID

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # 1. On récupère la lumière cible choisie lors de l'install
    target_light = entry.data[CONF_ENTITY_ID]
    
    # 2. On crée le coordinateur (le chef d'orchestre pour CETTE lumière)
    coordinator = EffectsCoordinator(hass, target_light)
    
    # 3. On le stocke dans la mémoire de HA pour que les boutons puissent l'utiliser
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # 4. On charge les entités (Menu et Curseurs)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Nettoyage
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.stop_effect() # On arrête tout avant de désinstaller
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

# --- LE COORDINATEUR (LA LOGIQUE) ---
class EffectsCoordinator:
    def __init__(self, hass, light_entity_id):
        self.hass = hass
        self.light_id = light_entity_id
        self.task = None
        # Valeurs par défaut
        self.current_effect = "Arrêt"
        self.speed = 1.0
        self.intensity = 50

    async def update_settings(self, effect=None, speed=None, intensity=None):
        """Appelé quand l'utilisateur touche à un bouton"""
        if effect: self.current_effect = effect
        if speed: self.speed = speed
        if intensity: self.intensity = intensity
        
        # On relance l'effet avec les nouveaux paramètres
        await self.start_effect()

    async def stop_effect(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

    async def start_effect(self):
        await self.stop_effect()
        
        if self.current_effect == "Arrêt":
            # Remise à zéro propre
            await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "effect": "none"})
            return

        # Lancement de la boucle correspondante
        if self.current_effect == "Bougie":
            self.task = self.hass.async_create_task(self._loop_candle())
        elif self.current_effect == "Stroboscope":
            self.task = self.hass.async_create_task(self._loop_strobe())
        elif self.current_effect == "Phare":
            self.task = self.hass.async_create_task(self._loop_lighthouse())
        # ... Ajoutez les autres 'elif' ici pour les autres effets ...

    # --- LES BOUCLES (Versions simplifiées qui utilisent self.speed / self.intensity) ---
    async def _loop_candle(self):
        try:
            while True:
                # Utilise self.intensity
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {
                    "entity_id": self.light_id, 
                    "brightness_pct": random.randint(10, int(self.intensity)),
                    "transition": random.uniform(0.5, 2.0)
                })
                await asyncio.sleep(random.uniform(0.5, 3.0))
        except asyncio.CancelledError: pass

    async def _loop_strobe(self):
        try:
            while True:
                await self.hass.services.async_call("light", "toggle", {"entity_id": self.light_id})
                # Utilise self.speed
                await asyncio.sleep(self.speed)
        except asyncio.CancelledError: pass

    async def _loop_lighthouse(self):
        try:
            while True:
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0.5})
                await asyncio.sleep(0.5)
                # Utilise self.speed
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 1, "transition": self.speed})
                await asyncio.sleep(self.speed)
        except asyncio.CancelledError: pass