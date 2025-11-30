class SimpleLightEffectsCard extends HTMLElement {
    set hass(hass) {
        this._hass = hass;
        if (!this.content) {
            this.innerHTML = `
                <ha-card header="Effets Lumineux">
                    <div class="card-content">
                        <div id="lights-container" class="lights-container">
                            <div style="text-align:center; padding: 20px;">Chargement des lumières...</div>
                        </div>
                        
                        <div id="effects-grid" class="effects-grid"></div>
                        
                        <div id="params" class="params-container">
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
                    
                    /* Styles copiés/adaptés de Scene Manager */
                    .lights-container { max-height: 400px; overflow-y: auto; border: 1px solid var(--divider-color, #eee); border-radius: 8px; padding: 8px; }
                    details { margin-bottom: 8px; border: 1px solid var(--divider-color, #eee); border-radius: 8px; overflow: hidden; }
                    summary { background: rgba(var(--rgb-primary-color), 0.05); padding: 10px 15px; cursor: pointer; list-style: none; display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 14px; }
                    summary::-webkit-details-marker { display: none; }
                    .room-checkbox { width: 18px; height: 18px; cursor: pointer; accent-color: var(--primary-color); }
                    .room-title { flex: 1; }
                    .summary-arrow::after { content: '▼'; font-size: 10px; transition: transform 0.2s; display:block; }
                    details[open] .summary-arrow::after { transform: rotate(180deg); }
                    .room-content { padding: 5px 10px 10px 10px; display: flex; flex-direction: column; gap: 6px; }
                    .light-row { display: flex; align-items: center; gap: 10px; padding: 4px 0; border-bottom: 1px dashed #eee; }
                    .light-row:last-child { border-bottom: none; }
                    .light-select { width: 18px; height: 18px; cursor: pointer; accent-color: var(--primary-color); margin-left: 10px; }
                    .light-name { font-size: 13px; font-weight: 500; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
                    
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
            this.lightsContainer = this.querySelector("#lights-container");
            this._init();
        }
    }

    async _init() {
        this.areas = await this._hass.callWS({ type: 'config/area_registry/list' });
        this.entities = await this._hass.callWS({ type: 'config/entity_registry/list' });
        this.devices = await this._hass.callWS({ type: 'config/device_registry/list' });

        this._buildLightControls();
        this._renderEffects();

        this.querySelector("#stop-btn").addEventListener("click", () => this._callService("stop"));
    }

    _buildLightControls() {
        const allLights = Object.keys(this._hass.states).filter((eid) => eid.startsWith("light."));
        const lightsByArea = {};
        this.areas.forEach(a => lightsByArea[a.area_id] = []);
        const noAreaLights = [];

        allLights.forEach(eid => {
            let assigned = false;
            const entry = this.entities.find(e => e.entity_id === eid);

            // 1. Check direct area assignment
            if (entry && entry.area_id && lightsByArea[entry.area_id]) {
                lightsByArea[entry.area_id].push(eid);
                assigned = true;
            }

            // 2. Check device area assignment
            if (!assigned && entry && entry.device_id) {
                const device = this.devices.find(d => d.id === entry.device_id);
                if (device && device.area_id && lightsByArea[device.area_id]) {
                    lightsByArea[device.area_id].push(eid);
                    assigned = true;
                }
            }

            // 3. Fallback: Check name matching
            if (!assigned) {
                const stateObj = this._hass.states[eid];
                const friendlyName = stateObj ? stateObj.attributes.friendly_name || "" : "";
                for (const area of this.areas) {
                    if (eid.toLowerCase().includes(area.area_id.toLowerCase()) || friendlyName.toLowerCase().includes(area.name.toLowerCase())) {
                        lightsByArea[area.area_id].push(eid);
                        assigned = true;
                        break;
                    }
                }
            }

            if (!assigned) noAreaLights.push(eid);
        });

        this.lightsContainer.innerHTML = "";

        const createSection = (areaName, lights) => {
            if (!lights || lights.length === 0) return;

            const details = document.createElement("details");
            const summary = document.createElement("summary");

            const masterCheck = document.createElement("input");
            masterCheck.type = "checkbox";
            masterCheck.className = "room-checkbox";

            const title = document.createElement("span");
            title.className = "room-title";
            title.innerText = areaName;

            const arrow = document.createElement("span");
            arrow.className = "summary-arrow";

            summary.appendChild(masterCheck);
            summary.appendChild(title);
            summary.appendChild(arrow);
            details.appendChild(summary);

            const container = document.createElement("div");
            container.className = "room-content";

            lights.sort();
            lights.forEach(eid => {
                const stateObj = this._hass.states[eid];
                const name = stateObj.attributes.friendly_name || eid;

                const row = document.createElement("div");
                row.className = "light-row";
                row.innerHTML = `
                    <input type="checkbox" class="light-select" data-entity="${eid}">
                    <div class="light-name" title="${eid}">${name}</div>
                `;
                container.appendChild(row);
            });

            // Master checkbox logic
            masterCheck.addEventListener("change", (e) => {
                const checkboxes = container.querySelectorAll(".light-select");
                checkboxes.forEach(cb => cb.checked = masterCheck.checked);
            });

            container.addEventListener("change", (e) => {
                if (e.target.classList.contains("light-select")) {
                    const all = container.querySelectorAll(".light-select");
                    const checked = container.querySelectorAll(".light-select:checked");
                    masterCheck.checked = checked.length > 0 && checked.length === all.length;
                    masterCheck.indeterminate = checked.length > 0 && checked.length < all.length;
                }
            });

            details.appendChild(container);
            this.lightsContainer.appendChild(details);
        };

        // Sort areas by name
        this.areas.sort((a, b) => a.name.localeCompare(b.name));

        this.areas.forEach(area => {
            createSection(area.name, lightsByArea[area.area_id]);
        });

        if (noAreaLights.length > 0) {
            createSection("Autres / Non Assignées", noAreaLights);
        }
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
        const checkboxes = this.shadowRoot ? this.shadowRoot.querySelectorAll(".light-select:checked") : this.querySelectorAll(".light-select:checked");
        const selectedLights = Array.from(checkboxes).map(cb => cb.dataset.entity);

        if (selectedLights.length === 0) return alert("Veuillez sélectionner au moins une lumière");

        const speed = this.querySelector("#speed").value;
        const intensity = this.querySelector("#intensity").value;

        this._hass.callService("simple_light_effects", effect, {
            entity_id: selectedLights,
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