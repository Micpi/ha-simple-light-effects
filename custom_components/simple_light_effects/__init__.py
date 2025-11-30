import asyncio
import random
import logging
import os
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.components.http import StaticPathConfig
from .const import DOMAIN, PLATFORMS, CONF_ENTITY_ID

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Simple Light Effects component services."""
    
    # Register static path for the card
    try:
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                "/simple_light_effects/card.js",
                hass.config.path("custom_components/simple_light_effects/www/simple-light-effects-card.js"),
                True,
            )
        ])
    except Exception:
        _LOGGER.debug("Could not register static path at startup")

    async def handle_effect_service(call: ServiceCall):
        service_to_effect = {
            "candle": "Bougie",
            "strobe": "Stroboscope",
            "police": "Alerte",
            "color_loop": "Respiration",
            "lightning": "Orage",
            "heartbeat": "Coeur",
            "stop": "Arrêt",
            "neon": "Néon",
            "lighthouse": "Phare",
            "sos": "SOS",
            "campfire": "Feu de camp"
        }
        
        effect_name = service_to_effect.get(call.service)
        if not effect_name:
            return

        entity_ids = call.data.get("entity_id", [])
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]
            
        speed = call.data.get("speed", 1.0)
        intensity = call.data.get("brightness_scale", 50)

        # Ensure manager exists
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = EffectsManager(hass)
        
        manager = hass.data[DOMAIN]
        
        for entity_id in entity_ids:
            await manager.start_effect(entity_id, effect_name, speed, intensity)

    for service in ["candle", "strobe", "police", "color_loop", "lightning", "heartbeat", "stop", "neon", "lighthouse", "sos", "campfire"]:
        hass.services.async_register(DOMAIN, service, handle_effect_service)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, EffectsManager(hass))
    
    # Copy card to www if possible
    try:
        www_dir = hass.config.path("www")
        if www_dir and os.path.isdir(www_dir):
            src = hass.config.path("custom_components/simple_light_effects/www/simple-light-effects-card.js")
            dst = os.path.join(www_dir, "simple-light-effects-card.js")
            import shutil
            if (not os.path.exists(dst)) or (os.path.getmtime(src) > os.path.getmtime(dst)):
                shutil.copyfile(src, dst)
    except Exception:
        pass
        
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if DOMAIN in hass.data:
        await hass.data[DOMAIN].stop_all()
    return True

class EffectsManager:
    def __init__(self, hass):
        self.hass = hass
        self.coordinators = {}

    async def start_effect(self, entity_id, effect, speed, intensity):
        if entity_id not in self.coordinators:
            self.coordinators[entity_id] = EffectsCoordinator(self.hass, entity_id)
        
        await self.coordinators[entity_id].update_settings(effect, speed, intensity)

    async def stop_all(self):
        for coordinator in self.coordinators.values():
            await coordinator.stop_effect()
        self.coordinators.clear()

# --- COORDINATEUR COMPLET ---
class EffectsCoordinator:
    def __init__(self, hass, light_entity_id):
        self.hass = hass
        self.light_id = light_entity_id
        self.task = None
        self.current_effect = "Arrêt"
        self.speed = 1.0
        self.intensity = 50

    async def update_settings(self, effect=None, speed=None, intensity=None):
        if effect: self.current_effect = effect
        if speed: self.speed = float(speed)
        if intensity: self.intensity = int(intensity)
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
            await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "effect": "none"})
            return

        # AIGUILLAGE DES EFFETS
        if self.current_effect == "Bougie":
            self.task = self.hass.async_create_task(self._loop_candle())
        elif self.current_effect == "Stroboscope":
            self.task = self.hass.async_create_task(self._loop_strobe())
        elif self.current_effect == "Alerte":
            self.task = self.hass.async_create_task(self._loop_pulse_fast())
        elif self.current_effect == "Respiration":
            self.task = self.hass.async_create_task(self._loop_breath())
        elif self.current_effect == "Orage":
            self.task = self.hass.async_create_task(self._loop_lightning())
        elif self.current_effect == "Coeur":
            self.task = self.hass.async_create_task(self._loop_heartbeat())
        elif self.current_effect == "Néon":
            self.task = self.hass.async_create_task(self._loop_neon())
        elif self.current_effect == "Phare":
            self.task = self.hass.async_create_task(self._loop_lighthouse())
        elif self.current_effect == "SOS":
            self.task = self.hass.async_create_task(self._loop_sos())
        elif self.current_effect == "Feu de camp":
            self.task = self.hass.async_create_task(self._loop_campfire())

    # --- BOUCLES D'EFFETS ---

    async def _loop_candle(self):
        try:
            while True:
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {
                    "entity_id": self.light_id, "brightness_pct": random.randint(10, int(self.intensity)),
                    "transition": random.uniform(0.5, 2.0)
                })
                await asyncio.sleep(random.uniform(0.5, 3.0))
        except asyncio.CancelledError: pass

    async def _loop_strobe(self):
        try:
            while True:
                await self.hass.services.async_call("light", "toggle", {"entity_id": self.light_id})
                await asyncio.sleep(self.speed)
        except asyncio.CancelledError: pass

    async def _loop_pulse_fast(self):
        try:
            while True:
                # Alerte ignore les réglages pour être percutant
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0.1})
                await asyncio.sleep(0.5)
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 10, "transition": 0.1})
                await asyncio.sleep(0.5)
        except asyncio.CancelledError: pass

    async def _loop_breath(self):
        try:
            while True:
                # Utilise Vitesse
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": self.speed})
                await asyncio.sleep(self.speed)
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 10, "transition": self.speed})
                await asyncio.sleep(self.speed)
        except asyncio.CancelledError: pass

    async def _loop_lightning(self):
        try:
            while True:
                count = random.randint(1, 3)
                for _ in range(count):
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0})
                    await asyncio.sleep(random.uniform(0.05, 0.2))
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 10, "transition": 0})
                    await asyncio.sleep(random.uniform(0.05, 0.2))
                await asyncio.sleep(random.uniform(2.0, 10.0))
        except asyncio.CancelledError: pass

    async def _loop_heartbeat(self):
        try:
            while True:
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0.1})
                await asyncio.sleep(0.2)
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 10, "transition": 0.2})
                await asyncio.sleep(0.2)
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 80, "transition": 0.1})
                await asyncio.sleep(0.2)
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 10, "transition": 0.3})
                await asyncio.sleep(1.0)
        except asyncio.CancelledError: pass

    async def _loop_neon(self):
        try:
            while True:
                for _ in range(random.randint(2, 6)):
                    bright = random.choice([0, int(self.intensity), 20])
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": bright, "transition": 0})
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 90, "transition": 0.1})
                await asyncio.sleep(random.uniform(2.0, 5.0))
        except asyncio.CancelledError: pass

    async def _loop_lighthouse(self):
        try:
            while True:
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0.5})
                await asyncio.sleep(0.5)
                # Utilise Vitesse pour la rotation
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 1, "transition": self.speed})
                await asyncio.sleep(self.speed)
        except asyncio.CancelledError: pass

    async def _loop_sos(self):
        try:
            while True:
                # S
                for _ in range(3):
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0})
                    await asyncio.sleep(0.3)
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 0, "transition": 0})
                    await asyncio.sleep(0.3)
                await asyncio.sleep(0.5)
                # O
                for _ in range(3):
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0})
                    await asyncio.sleep(1.0)
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 0, "transition": 0})
                    await asyncio.sleep(0.3)
                await asyncio.sleep(0.5)
                # S
                for _ in range(3):
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 100, "transition": 0})
                    await asyncio.sleep(0.3)
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 0, "transition": 0})
                    await asyncio.sleep(0.3)
                await asyncio.sleep(3.0)
        except asyncio.CancelledError: pass

    async def _loop_campfire(self):
        try:
            while True:
                await self.hass.services.async_call("light", SERVICE_TURN_ON, {
                    "entity_id": self.light_id, "brightness_pct": random.randint(int(self.intensity)-20, int(self.intensity)),
                    "transition": random.uniform(0.5, 1.5)
                })
                await asyncio.sleep(random.uniform(0.2, 1.0))
                if random.random() < 0.2:
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 10, "transition": 0.05})
                    await asyncio.sleep(0.1)
                    await self.hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": self.light_id, "brightness_pct": 90, "transition": 0.1})
                    await asyncio.sleep(0.2)
        except asyncio.CancelledError: pass