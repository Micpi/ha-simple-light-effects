import asyncio
import random
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Stockage des tâches
RUNNING_TASKS = {}

# 1. Configuration via YAML (On le garde vide pour compatibilité, mais on ne l'utilise plus)
async def async_setup(hass: HomeAssistant, config: dict):
    return True

# 2. Configuration via UI (C'est la nouvelle méthode !)
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    
    # --- LOGIQUE DES EFFETS (Copiée de votre version précédente) ---
    async def stop_effect_logic(entity_id):
        if entity_id in RUNNING_TASKS:
            task = RUNNING_TASKS.pop(entity_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    # --- DEFINITION DES SERVICES ---
    async def handle_candle(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        brightness_scale = call.data.get("brightness_scale", 50)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    await hass.services.async_call("light", SERVICE_TURN_ON, {
                        "entity_id": entity_id, "brightness_pct": random.randint(10, brightness_scale),
                        "transition": random.uniform(0.5, 2.0)
                    })
                    await asyncio.sleep(random.uniform(0.5, 3.0))
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_strobe(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        speed = call.data.get("speed", 0.5)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    await hass.services.async_call("light", "toggle", {"entity_id": entity_id})
                    await asyncio.sleep(speed)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_pulse_fast(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0.1})
                    await asyncio.sleep(0.5)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 10, "transition": 0.1})
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_breath(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        speed = call.data.get("speed", 4.0)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": speed})
                    await asyncio.sleep(speed)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 10, "transition": speed})
                    await asyncio.sleep(speed)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_lightning(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    count = random.randint(1, 3)
                    for _ in range(count):
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0})
                        await asyncio.sleep(random.uniform(0.05, 0.2))
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 10, "transition": 0})
                        await asyncio.sleep(random.uniform(0.05, 0.2))
                    await asyncio.sleep(random.uniform(2.0, 10.0))
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_heartbeat(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0.1})
                    await asyncio.sleep(0.2)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 10, "transition": 0.2})
                    await asyncio.sleep(0.2)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 80, "transition": 0.1})
                    await asyncio.sleep(0.2)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 10, "transition": 0.3})
                    await asyncio.sleep(1.0)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_stop(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 80})

    # Enregistrement des services
    hass.services.async_register(DOMAIN, "candle", handle_candle)
    hass.services.async_register(DOMAIN, "strobe", handle_strobe)
    hass.services.async_register(DOMAIN, "alerte", handle_pulse_fast)
    hass.services.async_register(DOMAIN, "respiration", handle_breath)
    hass.services.async_register(DOMAIN, "lightning", handle_lightning)
    hass.services.async_register(DOMAIN, "heartbeat", handle_heartbeat)
    hass.services.async_register(DOMAIN, "stop", handle_stop)

    return True

# 3. Suppression de l'intégration (Nettoyage)
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # On supprime les services quand on retire l'intégration
    hass.services.async_remove(DOMAIN, "candle")
    hass.services.async_remove(DOMAIN, "strobe")
    hass.services.async_remove(DOMAIN, "alerte")
    hass.services.async_remove(DOMAIN, "respiration")
    hass.services.async_remove(DOMAIN, "lightning")
    hass.services.async_remove(DOMAIN, "heartbeat")
    hass.services.async_remove(DOMAIN, "stop")
    return True