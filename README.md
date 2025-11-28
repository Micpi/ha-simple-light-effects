# 🕯️ Simple Light Effects pour Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/votre_pseudo/ha-simple-light-effects)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.11-brightgreen.svg)](https://www.home-assistant.io/)

Une intégration personnalisée (Custom Component) pour **Home Assistant** qui ajoute des effets d'éclairage dynamiques à **n'importe quelle lumière** (ampoules connectées, rubans LED, variateurs).

Contrairement aux effets natifs des ampoules (souvent limités), cette intégration utilise le moteur Python de Home Assistant pour calculer les variations, ce qui la rend compatible avec toutes les marques (Philips Hue, Tuya, Shelly, Zigbee, WiFi, etc.).

---

## ✨ Fonctionnalités

* **Universel :** Fonctionne sur n'importe quelle entité `light.` (même dimmable monochrome).
* **Asynchrone :** Ne bloque pas Home Assistant, même avec plusieurs effets en cours.
* **6 Effets inclus :**
    * 🕯️ **Bougie (Candle) :** Simulation réaliste d'une flamme (variations aléatoires).
    * 🚨 **Stroboscope (Strobe) :** Clignotement rapide (type disco).
    * 👮 **Alerte (Police) :** Pulsation rapide Fort/Faible (type gyrophare monochrome).
    * 😮‍💨 **Respiration (Breath) :** Montée et descente lente et relaxante.
    * ⚡ **Orage (Lightning) :** Flashs aléatoires suivis de pauses.
    * 💓 **Cœur (Heartbeat) :** Double pulsation rythmique (Boum-boum).
* **Installation Facile :** Supporte le "Config Flow" (Configuration via l'interface UI).

---

## 🚀 Installation

### Option 1 : Via HACS (Recommandé)

1.  Assurez-vous d'avoir [HACS](https://hacs.xyz/) installé.
2.  Allez dans **HACS** > **Intégrations**.
3.  Cliquez sur le menu (3 points en haut à droite) > **Dépôts personnalisés**.
4.  Ajoutez l'URL de ce dépôt GitHub.
5.  Catégorie : **Intégration**.
6.  Cliquez sur **Télécharger**.
7.  **Redémarrez Home Assistant**.

### Option 2 : Manuelle

1.  Téléchargez le code de ce dépôt.
2.  Copiez le dossier `simple_light_effects` dans votre dossier `/config/custom_components/`.
3.  Vous devriez avoir : `/config/custom_components/simple_light_effects/__init__.py`.
4.  **Redémarrez Home Assistant**.

---

## ⚙️ Configuration

Une fois installé et redémarré :

1.  Allez dans **Paramètres** > **Appareils et services**.
2.  Cliquez sur **+ Ajouter une intégration**.
3.  Cherchez **Simple Light Effects**.
4.  Validez. Aucune configuration YAML n'est nécessaire !

---

## 🎮 Utilisation des Services

L'intégration expose plusieurs services que vous pouvez utiliser dans vos automatisations, scripts ou tableaux de bord.

### 1. `simple_light_effects.candle` (Bougie)
Simule une flamme vacillante.
| Paramètre | Description | Exemple |
| :--- | :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. | `light.salon` |
| `brightness_scale` | Luminosité maximale (1-100). | `60` |

### 2. `simple_light_effects.strobe` (Stroboscope)
Clignotement On/Off régulier.
| Paramètre | Description | Exemple |
| :--- | :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. | `light.cuisine` |
| `speed` | Délai entre les flashs (secondes). | `0.2` (Rapide) |

### 3. `simple_light_effects.police` (Alerte)
Alterne rapidement entre 100% et 10% de luminosité.
| Paramètre | Description |
| :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. |

### 4. `simple_light_effects.color_loop` (Respiration)
Transition douce et lente (Montée/Descente).
| Paramètre | Description | Exemple |
| :--- | :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. | `light.chambre` |
| `speed` | Durée de la transition (secondes). | `4.0` |

### 5. `simple_light_effects.lightning` (Orage)
Génère des éclairs aléatoires (1 à 3 flashs) suivis de longues pauses.
| Paramètre | Description |
| :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. |

### 6. `simple_light_effects.heartbeat` (Battement de cœur)
Double pulsation rythmique.
| Paramètre | Description |
| :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. |

### 7. `simple_light_effects.stop` (Arrêt)
Arrête immédiatement l'effet en cours et remet la lumière à 80% fixe.
| Paramètre | Description |
| :--- | :--- |
| `entity_id` | **Requis.** La lumière cible. |

---

## 📱 Exemple de Carte (Dashboard)

Voici un code complet pour une carte Lovelace "Tout-en-un" pour contrôler vos effets.

```yaml
type: vertical-stack
cards:
  - type: tile
    entity: light.votre_lumiere
    name: Contrôle Principal
    icon: mdi:lightbulb

  - type: grid
    square: false
    columns: 2
    title: Effets d'Ambiance
    cards:
      - type: button
        name: Bougie
        icon: mdi:candle
        tap_action:
          action: perform-action
          perform_action: simple_light_effects.candle
          target: {}
          data:
            entity_id: light.votre_lumiere
            brightness_scale: 50

      - type: button
        name: Orage
        icon: mdi:weather-lightning
        tap_action:
          action: perform-action
          perform_action: simple_light_effects.lightning
          target: {}
          data:
            entity_id: light.votre_lumiere

      - type: button
        name: Cœur
        icon: mdi:heart-pulse
        tap_action:
          action: perform-action
          perform_action: simple_light_effects.heartbeat
          target: {}
          data:
            entity_id: light.votre_lumiere

      - type: button
        name: Strobe
        icon: mdi:alarm-light
        tap_action:
          action: perform-action
          perform_action: simple_light_effects.strobe
          target: {}
          data:
            entity_id: light.votre_lumiere
            speed: 0.3

  - type: button
    name: STOP / NORMAL
    icon: mdi:stop-circle-outline
    tap_action:
      action: perform-action
      perform_action: simple_light_effects.stop
      target: {}
      data:
        entity_id: light.votre_lumiere

---

## 🎛️ Tutoriel : Créer une Console de Contrôle Universelle

Au lieu de créer un bouton par effet, vous pouvez créer une interface "tout-en-un" avec un menu déroulant et des curseurs pour régler la vitesse et l'intensité dynamiquement.

### Étape 1 : Créer les Entrées (Helpers)

Allez dans **Paramètres** > **Appareils et services** > **Entrées** > **Créer une entrée**. Créez les 3 éléments suivants :

**1. Le Menu de choix (Liste déroulante)**
* **Nom :** `Mode Effet Cuisine` (ou adaptez le nom à votre pièce)
* **Options** (Respectez exactement cette liste) :
  * Arrêt
  * Bougie
  * Stroboscope
  * Alerte
  * Respiration
  * Orage
  * Coeur
  * Néon
  * Phare
  * SOS
  * Feu de camp
* **ID d'entité :** `input_select.mode_effet_cuisine`

**2. Le Curseur Vitesse (Nombre)**
* **Nom :** `Vitesse Effet`
* **Min/Max :** 0.1 / 5.0
* **Pas :** 0.1
* **Unité :** sec
* **ID d'entité :** `input_number.vitesse_effet`

**3. Le Curseur Intensité (Nombre)**
* **Nom :** `Intensité Effet`
* **Min/Max :** 10 / 100
* **Pas :** 5
* **Unité :** %
* **ID d'entité :** `input_number.intensite_effet`

### Étape 2 : L'Automatisation

Créez une nouvelle automatisation en mode YAML.
> **Note :** Pensez à remplacer `light.cuisine` par votre propre lumière (ex: `light.salon`) dans le code ci-dessous.

```yaml
alias: "Système : Contrôleur Universel Effets"
mode: restart
trigger:
  - platform: state
    entity_id:
      - input_select.mode_effet_cuisine
      - input_number.vitesse_effet
      - input_number.intensite_effet
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Arrêt"
        sequence:
          - action: simple_light_effects.stop
            data:
              entity_id: light.cuisine
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Bougie"
        sequence:
          - action: simple_light_effects.candle
            data:
              entity_id: light.cuisine
              brightness_scale: "{{ states('input_number.intensite_effet') | int }}"
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Stroboscope"
        sequence:
          - action: simple_light_effects.strobe
            data:
              entity_id: light.cuisine
              speed: "{{ states('input_number.vitesse_effet') | float }}"
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Alerte"
        sequence:
          - action: simple_light_effects.police
            data:
              entity_id: light.cuisine
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Respiration"
        sequence:
          - action: simple_light_effects.color_loop
            data:
              entity_id: light.cuisine
              speed: "{{ states('input_number.vitesse_effet') | float }}"
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Orage"
        sequence:
          - action: simple_light_effects.lightning
            data:
              entity_id: light.cuisine
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Coeur"
        sequence:
          - action: simple_light_effects.heartbeat
            data:
              entity_id: light.cuisine
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Néon"
        sequence:
          - action: simple_light_effects.neon
            data:
              entity_id: light.cuisine
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Phare"
        sequence:
          - action: simple_light_effects.lighthouse
            data:
              entity_id: light.cuisine
              speed: "{{ states('input_number.vitesse_effet') | float }}"
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "SOS"
        sequence:
          - action: simple_light_effects.sos
            data:
              entity_id: light.cuisine
      - conditions:
          - condition: state
            entity_id: input_select.mode_effet_cuisine
            state: "Feu de camp"
        sequence:
          - action: simple_light_effects.campfire
            data:
              entity_id: light.cuisine
