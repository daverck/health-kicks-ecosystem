# Spécification d'Architecture : Mécanisme de Présence Hybride

Ce document décrit l'architecture et les flux de synchronisation d'état de connexion (**présence**) entre l'application mobile, le broker AWS IoT Core, la fonction AWS Lambda de présence et l'API FastAPI dans l'écosystème **HealthKicks**.

---

## 1. Schéma d'Architecture Cible

```text
+-----------------------------------------------------------------------------+
|                           Application Mobile                                |
|  - Connexion BLE : Publie "online" sur healthkicks/v1/{device_id}/status    |
|  - Déconnexion BLE : Publie "offline" sur healthkicks/v1/{device_id}/status |
|  - MQTT LWT (au CONNECT) : healthkicks/v1/users/{user_id}/gateway-status    |
+--------------------------------------+--------------------------------------+
                                       | MQTT / WebSocket
                                       v
+-----------------------------------------------------------------------------+
|                                AWS IoT Core                                 |
|  - Topic applicatif : healthkicks/v1/+/status                               |
|  - Topic LWT (coupure réseau/crash) : healthkicks/v1/users/+/gateway-status |
+--------------------------------------+--------------------------------------+
                                       | Règle IoT (Rule)
                                       v
+-----------------------------------------------------------------------------+
|                            Lambda de Présence                               |
|  - Normalise l'événement (device_id unitaire ou user_id global)             |
|  - Effectue un POST HTTPS vers le Backend FastAPI                           |
+--------------------------------------+--------------------------------------+
                                       | POST /api/v1/internal/device-presence
                                       v
+-----------------------------------------------------------------------------+
|                           Backend FastAPI / Aurora                          |
|  - Si device_id : UPDATE devices SET status = :state WHERE id = :device_id  |
|  - Si user_id (LWT) : UPDATE devices SET status = 'offline'                 |
|                       WHERE user_id = :user_id                              |
|  - Diffusion temps réel : Notification WebSocket vers le frontend Web       |
+-----------------------------------------------------------------------------+
```

---

## 2. Principe Hybride de Détection de Présence

La présence des équipements connectés HealthKicks repose sur un mécanisme à double niveau combinant **statut unitaire BLE** et **déconnexion brutale LWT** (*Last Will and Testament*) :

### A. Niveau 1 : Statuts BLE Unitaires (Gérés par l'App Mobile)
- Dès qu'une chaussure (`HK-x`) est connectée et que ses services GATT sont prêts, l'application mobile publie immédiatement un message sur le topic dédié de l'équipement :
  - **Topic :** `healthkicks/v1/{device_id}/status`
  - **Payload :**
    ```json
    {
      "device_id": "HK-2",
      "state": "online",
      "gateway": "mobile",
      "timestamp": "2026-09-16T21:00:00.000Z"
    }
    ```
- Lors d'une déconnexion volontaire de l'équipement BLE ou d'une perte de portée radio (signal BLE rompu) :
  - L'application mobile publie immédiatement :
    ```json
    {
      "device_id": "HK-2",
      "state": "offline",
      "gateway": "mobile",
      "timestamp": "2026-09-16T21:05:00.000Z"
    }
    ```

### B. Niveau 2 : Coupure Brutale Réseau / Crash Mobile (MQTT LWT)
- L'application mobile agit comme passerelle pour plusieurs capteurs rattachés à un même utilisateur (`user_id`).
- Lors de l'établissement de la connexion MQTT vers AWS IoT Core (`MqttConnectMessage`), l'application configure un testament MQTT LWT lié au compte utilisateur :
  - **Topic LWT :** `healthkicks/v1/users/{user_id}/gateway-status`
  - **Payload LWT :**
    ```json
    {
      "user_id": "1",
      "state": "offline",
      "gateway": "mobile"
    }
    ```
  - **QoS :** `1` (`atLeastOnce`).
- En cas de perte de connexion brutale (perte réseau 4G/5G/Wi-Fi, coupure de batterie, fermeture forcée de l'application), le broker AWS IoT Core publie automatiquement ce message testamentaire.
- Le backend met alors en `offline` **tous** les périphériques associés à ce `user_id`.

---

## 3. Configuration AWS Cloud

Le moteur de règles AWS IoT Core ne supporte qu'un seul filtre de topic par clause `FROM` et interdit les alias débutant par un underscore (`_`).
La bonne pratique AWS consiste donc à créer **deux règles IoT ciblées** déclenchant la **même fonction Lambda** :

### A. Règle 1 : Statuts BLE Unitaires (`healthkicks_device_presence_rule`)
Capture les connexions et déconnexions unitaires émises par le mobile lors des transitions BLE :
```sql
SELECT *, topic() as topic FROM 'healthkicks/v1/+/status'
```
*Action :* Invoquer la Lambda `healthkicks_presence_handler`.

### B. Règle 2 : Testament Passerelle LWT (`healthkicks_user_gateway_presence_rule`)
Capture la rupture brutale de l'application mobile (perte réseau, crash, batterie) :
```sql
SELECT *, topic() as topic FROM 'healthkicks/v1/users/+/gateway-status'
```
*Action :* Invoquer la même Lambda `healthkicks_presence_handler`.

### C. Fonction Lambda AWS (`healthkicks_presence_handler`)
La fonction Lambda reçoit l'événement MQTT, extrait `device_id` ou `user_id` et transmet la notification à l'API interne du backend :

```python
import json
import os
import urllib.request
from datetime import datetime, timezone

def lambda_handler(event, context):
    api_url = os.environ.get(
        "BACKEND_URL",
        "https://healthkicks.duckdns.org:8443/api/v1/internal/device-presence"
    )
    ingest_token = os.environ.get("INGEST_TOKEN", "xxxxxxxxx")

    device_id = event.get("device_id")
    user_id = event.get("user_id")
    state = event.get("state", "offline").lower()

    payload = {
        "state": state,
        "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat()
    }

    if device_id:
        payload["device_id"] = device_id
    elif user_id:
        payload["user_id"] = user_id
    else:
        print(f"Skipping event: neither device_id nor user_id provided: {json.dumps(event)}")
        return {"status": "ignored"}

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Ingest-Token": ingest_token,
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"Presence synced with backend. Status: {response.status}")
            return {"status": "success", "code": response.status}
    except Exception as e:
        print(f"Error calling backend presence endpoint: {e}")
        raise e
```

---

## 4. Contrat Backend FastAPI : `POST /api/v1/internal/device-presence`

- **Authentification :** En-tête `X-Ingest-Token` (ou `X-HealthKicks-Ingest-Token`).
- **Schéma Pydantic :**
  ```python
  class DevicePresencePayload(BaseModel):
      device_id: str | None = None
      user_id: int | str | None = None
      state: Literal["online", "offline"] | None = None
      status: str | None = None
      timestamp: datetime | None = None
  ```
- **Logique Métier :**
  1. Si `device_id` est spécifié :
     - Mise à jour du champ `status` de la table `devices`.
     - Si passage `online` : mise à jour de `last_seen_utc = timestamp`.
     - Si passage `offline` : conservation de la valeur précédente de `last_seen_utc`.
  2. Si `user_id` est spécifié (déclenchement LWT suite à rupture passerelle) :
     - Résolution de l'identifiant utilisateur (par ID entier, email ou identifiants SSO).
     - Récupération de tous les `device_id` rattachés via `device_ownership`.
     - Mise à jour en lot (`UPDATE devices SET status = 'offline' WHERE device_id IN (...)`).
  3. Relais de l'événement de statut sur le canal d'actualisation temps réel pour le frontend Web.

