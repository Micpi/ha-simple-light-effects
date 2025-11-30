# Copilot Instructions for `ha-simple-light-effects`

This is a Home Assistant Custom Component that adds dynamic light effects to any `light.` entity.

## 🏗 Architecture

- **Core Logic**: `EffectsCoordinator` class in `__init__.py`. It manages the active effect loop as an `asyncio.Task`.
- **State Management**: The coordinator holds the state (`current_effect`, `speed`, `intensity`) and restarts the effect task whenever settings change.
- **Integration Point**: One `EffectsCoordinator` is created per Config Entry and stored in `hass.data[DOMAIN][entry_id]`.
- **User Interface**: 
  - `select.py`: Controls the active effect.
  - `number.py`: Controls speed and intensity parameters.

## 🚀 Developer Workflows

### Adding a New Effect
To add a new light effect, you must modify two files:

1.  **Implement Logic (`__init__.py`)**:
    -   Add a new async method `_loop_YOUR_EFFECT(self)` to `EffectsCoordinator`.
    -   Use an infinite `while True` loop.
    -   Control lights using `self.hass.services.async_call("light", ...)`
    -   **Crucial**: Wrap the loop in `try...except asyncio.CancelledError: pass` to handle clean stops.

2.  **Register Dispatch (`__init__.py`)**:
    -   Update `start_effect(self)` method.
    -   Add an `elif self.current_effect == "YOUR_EFFECT_NAME":` block to create the task.

3.  **Expose to UI (`select.py`)**:
    -   Add "YOUR_EFFECT_NAME" to `self._attr_options` in `EffectModeSelect` class.

## 🧩 Code Patterns & Conventions

### Effect Loop Pattern
All effects must follow this non-blocking async pattern:

```python
async def _loop_example(self):
    try:
        while True:
            # Use self.speed or self.intensity to modulate parameters
            await self.hass.services.async_call(
                "light", 
                SERVICE_TURN_ON, 
                {
                    "entity_id": self.light_id, 
                    "brightness_pct": int(self.intensity), 
                    "transition": self.speed
                }
            )
            await asyncio.sleep(self.speed)
    except asyncio.CancelledError:
        # Mandatory for clean task cancellation
        pass
```

### Service Calls
- Always use `await self.hass.services.async_call(...)`.
- Do not use blocking calls.
- Target `self.light_id` which is stored in the coordinator.

### Configuration
- This integration uses **Config Flow** (`config_flow.py`).
- There is **no YAML configuration** support for setup.
- `services.yaml` exists for documentation but services are currently not explicitly registered in `__init__.py` (logic is entity-driven).

## ⚠️ Critical Constraints
- **Asyncio**: All loops must yield control (`await asyncio.sleep`).
- **Error Handling**: Effect loops must handle `CancelledError` silently to allow switching effects without errors.
- **Dependencies**: Relies on standard HA constants from `homeassistant.const`.
