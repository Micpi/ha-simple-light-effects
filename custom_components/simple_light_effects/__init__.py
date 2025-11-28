import asyncio
import random
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
RUNNING_TASKS = {}

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    
    # --- HELPER: Nettoyage ---
    async def stop_effect_logic(entity_id):
        if entity_id in RUNNING_TASKS:
            task = RUNNING_TASKS.pop(entity_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    # ================= ANCIENS EFFETS =================

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

    # ================= NOUVEAUX EFFETS =================

    # 7. NEON DEFECTUEUX
    async def handle_neon(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    # Grésillement rapide
                    for _ in range(random.randint(2, 6)):
                        bright = random.choice([0, 100, 20])
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": bright, "transition": 0})
                        await asyncio.sleep(random.uniform(0.05, 0.15))
                    
                    # Stabilisation temporaire
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 90, "transition": 0.1})
                    await asyncio.sleep(random.uniform(2.0, 5.0))
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    # 8. PHARE (LIGHTHOUSE)
    async def handle_lighthouse(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        speed = call.data.get("speed", 2.0) # Vitesse de rotation
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    # Flash rapide (Le phare nous fait face)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0.5})
                    await asyncio.sleep(0.5)
                    # Extinction lente (Le phare tourne)
                    await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 1, "transition": speed})
                    await asyncio.sleep(speed)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    # 9. SIGNAL SOS
    async def handle_sos(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    # 3 COURTS (S)
                    for _ in range(3):
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0})
                        await asyncio.sleep(0.3)
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 0, "transition": 0})
                        await asyncio.sleep(0.3)
                    await asyncio.sleep(0.5)
                    
                    # 3 LONGS (O)
                    for _ in range(3):
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0})
                        await asyncio.sleep(1.0)
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 0, "transition": 0})
                        await asyncio.sleep(0.3)
                    await asyncio.sleep(0.5)
                    
                    # 3 COURTS (S)
                    for _ in range(3):
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 100, "transition": 0})
                        await asyncio.sleep(0.3)
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 0, "transition": 0})
                        await asyncio.sleep(0.3)
                    
                    # Pause avant de répéter
                    await asyncio.sleep(3.0)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    # 10. FEU DE CAMP
    async def handle_campfire(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        async def loop():
            try:
                while True:
                    # Variation douce de base
                    await hass.services.async_call("light", SERVICE_TURN_ON, {
                        "entity_id": entity_id, "brightness_pct": random.randint(40, 80),
                        "transition": random.uniform(0.5, 1.5)
                    })
                    await asyncio.sleep(random.uniform(0.2, 1.0))
                    
                    # Occasionnellement : Craquement du bois (chute brutale)
                    if random.random() < 0.2: # 20% de chance
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 10, "transition": 0.05})
                        await asyncio.sleep(0.1)
                        # Remontée rapide (étincelle)
                        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 90, "transition": 0.1})
                        await asyncio.sleep(0.2)
            except asyncio.CancelledError: pass
        RUNNING_TASKS[entity_id] = hass.async_create_task(loop())

    async def handle_stop(call: ServiceCall):
        entity_id = call.data.get(ATTR_ENTITY_ID)
        await stop_effect_logic(entity_id)
        await hass.services.async_call("light", SERVICE_TURN_ON, {"entity_id": entity_id, "brightness_pct": 80})

    # ENREGISTREMENT TOTAL
    hass.services.async_register(DOMAIN, "candle", handle_candle)
    hass.services.async_register(DOMAIN, "strobe", handle_strobe)
    hass.services.async_register(DOMAIN, "police", handle_pulse_fast)
    hass.services.async_register(DOMAIN, "color_loop", handle_breath)
    hass.services.async_register(DOMAIN, "lightning", handle_lightning)
    hass.services.async_register(DOMAIN, "heartbeat", handle_heartbeat)
    hass.services.async_register(DOMAIN, "neon", handle_neon)        # NEW
    hass.services.async_register(DOMAIN, "lighthouse", handle_lighthouse) # NEW
    hass.services.async_register(DOMAIN, "sos", handle_sos)          # NEW
    hass.services.async_register(DOMAIN, "campfire", handle_campfire) # NEW
    hass.services.async_register(DOMAIN, "stop", handle_stop)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    services = ["candle", "strobe", "police", "color_loop", "lightning", "heartbeat", "neon", "lighthouse", "sos", "campfire", "stop"]
    for s in services:
        hass.services.async_remove(DOMAIN, s)
    return True