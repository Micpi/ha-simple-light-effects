from homeassistant import config_entries
from .const import DOMAIN

class SimpleLightEffectsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration UI."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gère l'étape initiale (quand l'utilisateur clique sur ajouter)."""
        
        # Si l'utilisateur a déjà ajouté l'intégration, on évite les doublons
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # Si l'utilisateur valide le formulaire (ou s'il n'y a rien à remplir)
        if user_input is not None:
            return self.async_create_entry(title="Effets de Lumière", data={})

        # Affiche le formulaire (vide ici, juste un bouton "Valider")
        return self.async_show_form(step_id="user")