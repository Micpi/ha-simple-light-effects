import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_ENTITY_ID

class SimpleLightEffectsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # On utilise le nom de la lumière comme titre de l'intégration
            return self.async_create_entry(title=user_input[CONF_ENTITY_ID], data=user_input)

        # Formulaire pour choisir la lumière
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ENTITY_ID): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="light")
                ),
            })
        )