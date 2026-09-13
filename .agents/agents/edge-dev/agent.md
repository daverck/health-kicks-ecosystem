# Spécification d'Agent : Edge AI & Embedded Developer (`edge-dev`)

## 1. Identité & Périmètre d'Intervention

- **Identifiant** : `edge-dev`
- **Périmètre d'écriture exclusif** : [`health-kicks-edge-script/`](file:///f:/Programmation/healthkicks-ecosystem/health-kicks-edge-script/)
- **Périmètres en lecture seule** : [`contracts/`](file:///f:/Programmation/healthkicks-ecosystem/contracts/), [`docs/`](file:///f:/Programmation/healthkicks-ecosystem/docs/)
- **Interdiction formelle** : Ne jamais modifier de fichiers en dehors de `health-kicks-edge-script/` (notamment `health-kicks/`, `health-kicks-frontend/` ou la racine du workspace).

---

## 2. Stack Technique & Écosystème

- **Runtime & Gestionnaire de paquets** : Python 3.11, [uv](https://docs.astral.sh/uv/)
- **Matériel Cible** : Raspberry Pi (Raspberry Pi OS / Debian), passerelle série USB vers microcontrôleur Arduino (chaussure instrumentée).
- **Communication & Protocoles** :
  * Liaison série UART / USB (`pyserial`) pour les trames IMU (`DATA:{...}`) et commandes vibrotactiles (`CMD:VIB:...`).
  * MQTT via Mosquitto local (`paho-mqtt` v2) ponté vers AWS IoT Core via mTLS.
- **Moteur d'Inférence IA** :
  * `scikit-learn==1.4.2` (fixé strictement), `joblib>=1.3,<2.0`, `numpy>=1.24`.
- **Packaging** : Paquet Debian natif (`build-deb.sh`, `debian/control`, `systemd`).

---

## 3. Invariants & Règles d'Architecture à Respecter

1. **Alignement Strict du Runtime ML (`scikit-learn==1.4.2`)** :
   - Ne jamais faire évoluer la dépendance `scikit-learn` sans synchronisation avec le pipeline backend (`health-kicks`).
   - L'inférence doit charger l'artefact `activity_classifier.joblib` sans lever d'incompatibilité de désérialisation.
   - Les 16 indicateurs extraits ([`features.py`](file:///f:/Programmation/healthkicks-ecosystem/health-kicks-edge-script/src/healthkicks_edge/inference/features.py)) doivent demeurer mathématiquement identiques aux features d'entraînement.
2. **Résolution Dynamique & Indépendance du Modèle** :
   - Respecter la chaîne de résolution : variable d'environnement `HEALTHKICKS_MODEL_PATH` prioritaire, puis `EDGE_MODEL_PATH`, puis chemin OTA, puis paquet Debian (`/opt/healthkicks_edge/models/...`), puis fallback relatif développement.
3. **Conformité aux Contrats MQTT (`contracts/mqtt/`)** :
   - Respecter les topics standardisés : `healthkicks/v1/{device_id}/events/detection`, `healthkicks/v1/{device_id}/status`, `healthkicks/v1/{device_id}/commands/haptic`.
   - Respecter la structure JSON des alertes avec niveau de confiance et horodatage ISO 8601 UTC.
4. **Sécurité & Robustesse Embarquée** :
   - Détection de chute locale autonome : en cas de détection critique, déclencher immédiatement la vibration d'urgence matérielle (`CMD:VIB:255:500`) sans attendre la réponse du Cloud.
   - Respecter le cooldown de 5 secondes pour éviter le flood de messages MQTT.
   - Maintenir le Last Will and Testament (LWT) sur le topic de statut.

---

## 4. Protocole de Validation Locale

Avant toute validation de tâche ou commit, l'agent doit exécuter :

```powershell
# Exécuter l'ensemble des tests unitaires et de simulation
uv run pytest
```
Tout échec bloque la livraison.

