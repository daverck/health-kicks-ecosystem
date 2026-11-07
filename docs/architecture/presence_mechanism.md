# Architecture Specification: Hybrid Presence Mechanism

This document describes the architecture and state synchronization flows for connection state (**presence**) between the mobile companion app, AWS IoT Core broker, AWS Lambda presence relay, and FastAPI API in the **HealthKicks** ecosystem.

---

## 1. Target Architecture Diagram

```text
+-----------------------------------------------------------------------------+
|                           Mobile Application                                |
|  - BLE Connected: Publishes "online" on healthkicks/v1/{device_id}/status   |
|  - BLE Disconnected: Publishes "offline" on healthkicks/v1/{device_id}/status|
|  - MQTT LWT (at CONNECT): healthkicks/v1/users/{user_id}/gateway-status     |
+--------------------------------------+--------------------------------------+
                                       | MQTT / WebSocket
                                       v
+-----------------------------------------------------------------------------+
|                                AWS IoT Core                                 |
|  - Application topic: healthkicks/v1/+/status                               |
|  - LWT topic (network drop / crash): healthkicks/v1/users/+/gateway-status  |
+--------------------------------------+--------------------------------------+
                                       | IoT Rule
                                       v
+-----------------------------------------------------------------------------+
|                            Presence Lambda                                  |
|  - Normalizes event (unitary device_id or global user_id)                   |
|  - Executes HTTPS POST to FastAPI Backend                                   |
+--------------------------------------+--------------------------------------+
                                       | POST /api/v1/internal/device-presence
                                       v
+-----------------------------------------------------------------------------+
|                           FastAPI Backend / Aurora                          |
|  - If device_id: UPDATE devices SET status = :state WHERE id = :device_id   |
|  - If user_id (LWT): UPDATE devices SET status = 'offline'                  |
|                      WHERE user_id = :user_id                               |
|  - Real-time broadcast: WebSocket notification to Web Frontend              |
+-----------------------------------------------------------------------------+
```

---

## 2. Hybrid Presence Detection Principle

HealthKicks connected equipment presence relies on a dual-tier mechanism combining **unitary BLE status** and **sudden disconnection LWT** (_Last Will and Testament_):

### A. Tier 1: Unitary BLE Statuses (Managed by Mobile App)

- As soon as a shoe (`HK-x`) connects and its GATT services are ready, the mobile application immediately publishes a status message on the device's dedicated topic:
  - **Topic:** `healthkicks/v1/{device_id}/status`
  - **Payload:**
    ```json
    {
      "device_id": "HK-2",
      "state": "online",
      "gateway": "mobile",
      "timestamp": "2026-09-16T21:00:00.000Z"
    }
    ```
- Upon voluntary disconnection or radio range loss (broken BLE signal):
  - The mobile app immediately publishes:
    ```json
    {
      "device_id": "HK-2",
      "state": "offline",
      "gateway": "mobile",
      "timestamp": "2026-09-16T21:05:00.000Z"
    }
    ```

### B. Tier 2: Network Drop / Mobile Crash (MQTT LWT)

- The mobile app serves as gateway for multiple sensors attached to a single user (`user_id`).
- When establishing the MQTT connection to AWS IoT Core (`MqttConnectMessage`), the app configures an MQTT LWT linked to the user account:
  - **LWT Topic:** `healthkicks/v1/users/{user_id}/gateway-status`
  - **LWT Payload:**
    ```json
    {
      "user_id": "1",
      "state": "offline",
      "gateway": "mobile"
    }
    ```
  - **QoS:** `1` (`atLeastOnce`).
- In case of sudden connection drop (cellular/Wi-Fi loss, battery depletion, OS force kill), the AWS IoT Core broker automatically publishes this testamentary message.
- The backend then switches **all** devices linked to this `user_id` to `offline`.

---

## 3. AWS Cloud Configuration

The AWS IoT Core rule engine requires a single topic filter per `FROM` clause and forbids aliases starting with an underscore (`_`).
The recommended AWS pattern creates **two targeted IoT rules** triggering the **same Lambda function**:

### A. Rule 1: Unitary BLE Statuses (`healthkicks_device_presence_rule`)

Captures unitary connects and disconnects emitted by mobile during BLE transitions:

```sql
SELECT *, topic() as topic FROM 'healthkicks/v1/+/status'
```

_Action:_ Invoke `healthkicks_presence_handler` Lambda.

### B. Rule 2: Gateway LWT Testament (`healthkicks_user_gateway_presence_rule`)

Captures sudden drops of the mobile gateway app (network loss, crash, battery):

```sql
SELECT *, topic() as topic FROM 'healthkicks/v1/users/+/gateway-status'
```

_Action:_ Invoke the same `healthkicks_presence_handler` Lambda.

### C. AWS Lambda Function (`healthkicks_presence_handler`)

The Lambda function receives the MQTT event, extracts `device_id` or `user_id`, and forwards the notification to the backend internal API:

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

## 4. FastAPI Backend Contract: `POST /api/v1/internal/device-presence`

- **Authentication:** `X-Ingest-Token` (or `X-HealthKicks-Ingest-Token`) header.
- **Pydantic Schema:**
  ```python
  class DevicePresencePayload(BaseModel):
      device_id: str | None = None
      user_id: int | str | None = None
      state: Literal["online", "offline"] | None = None
      status: str | None = None
      timestamp: datetime | None = None
  ```
- **Business Logic:**
  1. If `device_id` is provided:
     - Updates `status` column in `devices` table.
     - If transitioning to `online`: updates `last_seen_utc = timestamp`.
     - If transitioning to `offline`: preserves previous `last_seen_utc` value.
  2. If `user_id` is provided (LWT triggered by gateway failure):
     - Resolves user identifier.
     - Retrieves all attached `device_id` rows via `device_ownership`.
     - Batch update (`UPDATE devices SET status = 'offline' WHERE device_id IN (...)`).
  3. Broadcasts presence status update over real-time channel to the Web frontend.
