class SimpleLightEffectsCard extends HTMLElement {
    set hass(hass) {
        this._hass = hass;
        if (!this.content) {
            this.innerHTML = `
                <ha-card header="Effets Lumineux">
                    <div class="card-content">
                        <div id="controls">
                            <div class="select-container">
                                <label>Pièce</label>
                                <select id="area-select" class="ha-select"><option value="">Chargement...</option></select>
                            </div>
                            <div class="select-container">
                                <label>Lumière</label>
                                <select id="light-select" class="ha-select" disabled><option value="">Sélectionnez une pièce</option></select>
                            </div>
                        </div>
                        <div id="effects-grid" class="effects-grid"></div>
                        <div id="params" class="params-container" style="display:none;">
                            <div class="param-row">
                                <span>Vitesse</span>
                                <input type="range" id="speed" min="0.1" max="5" step="0.1" value="1">
                            </div>
                            <div class="param-row">
                                <span>Intensité</span>
                                <input type="range" id="intensity" min="1" max="100" step="1" value="50">
                            </div>
                        </div>
                        <button id="stop-btn" class="stop-btn">ARRÊT</button>
                    </div>
                </ha-card>
                <style>
                    ha-card { padding-bottom: 16px; }
                    .card-content { display: flex; flex-direction: column; gap: 16px; }
                    .select-container { display: flex; flex-direction: column; gap: 4px; }
                    .ha-select { padding: 8px; border-radius: 4px; border: 1px solid var(--divider-color, #ccc); background: var(--card-background-color, white); color: var(--primary-text-color); }
                    .effects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 8px; margin-top: 8px; }
                    .effect-btn { 
                        background: var(--primary-color); color: white; border: none; padding: 10px; 
                        border-radius: 8px; cursor: pointer; font-weight: 500; transition: opacity 0.2s;
                        text-align: center; font-size: 0.9em;
                    }
                    .effect-btn:hover { opacity: 0.8; }
                    .stop-btn { 
                        background: var(--error-color, #f44336); color: white; border: none; padding: 12px; 
                        border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 8px;
                    }
                    .params-container { background: var(--secondary-background-color, #f5f5f5); padding: 10px; border-radius: 8px; }
                    .param-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
                    input[type=range] { flex: 1; margin-left: 10px; }
                </style>
            `;
            this.content = this.querySelector(".card-content");
            this._init();
        }
    }

    async _init() {
        this.areas = await this._hass.callWS({ type: 'config/area_registry/list' });
        this.entities = await this._hass.callWS({ type: 'config/entity_registry/list' });
        this.devices = await this._hass.callWS({ type: 'config/device_registry/list' });

        this._populateAreas();
        this._renderEffects();

        this.querySelector("#area-select").addEventListener("change", (e) => this._onAreaChange(e.target.value));
        this.querySelector("#light-select").addEventListener("change", (e) => this._onLightChange(e.target.value));
        this.querySelector("#stop-btn").addEventListener("click", () => this._callService("stop"));
    }

    _populateAreas() {
        const select = this.querySelector("#area-select");
        select.innerHTML = '<option value="">Choisir une pièce...</option>';

        this.areas.sort((a, b) => a.name.localeCompare(b.name)).forEach(area => {
            const opt = document.createElement("option");
            opt.value = area.area_id;
            opt.innerText = area.name;
            select.appendChild(opt);
        });
    }

    _onAreaChange(areaId) {
        const select = this.querySelector("#light-select");
        select.innerHTML = '<option value="">Choisir une lumière...</option>';
        select.disabled = !areaId;

        if (!areaId) return;

        const lights = this.entities.filter(e => {
            if (e.domain !== "light") return false;
            if (e.area_id === areaId) return true;
            if (e.device_id) {
                const device = this.devices.find(d => d.id === e.device_id);
                return device && device.area_id === areaId;
            }
            return false;
        });

        lights.forEach(light => {
            const opt = document.createElement("option");
            opt.value = light.entity_id;
            opt.innerText = light.name || light.original_name;
            select.appendChild(opt);
        });
    }

    _onLightChange(entityId) {
        const params = this.querySelector("#params");
        params.style.display = entityId ? "block" : "none";
        this.currentEntity = entityId;
    }

    _renderEffects() {
        const effects = [
            { id: "candle", name: "Bougie" },
            { id: "strobe", name: "Stroboscope" },
            { id: "police", name: "Alerte" },
            { id: "color_loop", name: "Respiration" },
            { id: "lightning", name: "Orage" },
            { id: "heartbeat", name: "Cœur" },
            { id: "neon", name: "Néon" },
            { id: "lighthouse", name: "Phare" },
            { id: "sos", name: "SOS" },
            { id: "campfire", name: "Feu de camp" }
        ];

        const grid = this.querySelector("#effects-grid");
        effects.forEach(effect => {
            const btn = document.createElement("button");
            btn.className = "effect-btn";
            btn.innerText = effect.name;
            btn.onclick = () => this._callService(effect.id);
            grid.appendChild(btn);
        });
    }

    _callService(effect) {
        if (!this.currentEntity) return alert("Veuillez sélectionner une lumière");

        const speed = this.querySelector("#speed").value;
        const intensity = this.querySelector("#intensity").value;

        this._hass.callService("simple_light_effects", effect, {
            entity_id: this.currentEntity,
            speed: parseFloat(speed),
            brightness_scale: parseInt(intensity)
        });
    }

    setConfig(config) { }
    getCardSize() { return 3; }
}

customElements.define('simple-light-effects-card', SimpleLightEffectsCard);

window.customCards = window.customCards || [];
window.customCards.push({
    type: "simple-light-effects-card",
    name: "Simple Light Effects Card",
    description: "Contrôle des effets lumineux par pièce"
});
