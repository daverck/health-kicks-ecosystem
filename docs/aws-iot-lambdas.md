# AWS IoT Core Rules & Lambda Ingestion Architecture

This document describes the AWS IoT Topic Rules, execution environments, environment variables, and handlers deployed to ingest telemetry, presence events, activity detection, and fall alerts into DynamoDB and Aurora PostgreSQL.

---

## 1. Device Presence Ingestion

- **IoT Rule Name:** `healthkicks_device_presence_rule`
- **Rule SQL:**

```sql
SELECT *, topic() as topic FROM 'healthkicks/v1/+/status'
```

- **Trigger:** Published by footwear devices or the mobile gateway when the shoe goes online/offline.
- **Target:** AWS Lambda Function (`healthkicks-device-presence`)

### Environment Variables

| Variable       | Required | Default                                                                | Description                                                               |
| :------------- | :------: | :--------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| `BACKEND_URL`  |   Yes    | `https://healthkicks.duckdns.org:8443/api/v1/internal/device-presence` | FastAPI endpoint for presence ingestion.                                  |
| `INGEST_TOKEN` |   Yes    | `dev-token`                                                            | Secret API authentication token sent via `X-Ingest-Token`.                |
| `VERIFY_SSL`   |    No    | `true`                                                                 | Set to `false` only in development if using self-signed TLS certificates. |

### Source Code (`lambda_function.py`)

```python
import json
import os
import ssl
import urllib.request
from datetime import datetime, timezone


def lambda_handler(event, context):
    print(f"[PRESENCE] Event received: {json.dumps(event)}")

    backend_url = os.environ.get(
        "BACKEND_URL",
        "https://healthkicks.duckdns.org:8443/api/v1/internal/device-presence"
    )
    ingest_token = os.environ.get("INGEST_TOKEN", "dev-token")
    verify_ssl = os.environ.get("VERIFY_SSL", "true").lower() == "true"

    device_id = event.get("device_id")
    user_id = event.get("user_id")
    state = event.get("state", "offline").lower()

    # Normalize payload for FastAPI backend
    payload = {
        "state": state,
        "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat()
    }

    if device_id:
        payload["device_id"] = str(device_id)
    elif user_id:
        payload["user_id"] = str(user_id)
    else:
        print(f"[PRESENCE] Event ignored (missing device_id and user_id): {json.dumps(event)}")
        return {"status": "ignored", "reason": "no device_id or user_id"}

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        backend_url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Ingest-Token": ingest_token,
        },
        method="POST"
    )

    # SSL context (allows unverified certificates if VERIFY_SSL=false)
    ssl_context = None if verify_ssl else ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            resp_body = response.read().decode("utf-8")
            print(f"[PRESENCE] Backend synchronized ({payload}). HTTP {response.status}, Response: {resp_body}")
            return {
                "statusCode": response.status,
                "body": resp_body
            }
    except Exception as e:
        print(f"[PRESENCE] Error calling backend ({backend_url}): {e}")
        raise e
```

---

## 2. User Gateway Presence Ingestion (LWT)

- **IoT Rule Name:** `healthkicks_user_gateway_presence_rule`
- **Rule SQL:**

```sql
SELECT *, topic() as topic FROM 'healthkicks/v1/users/+/gateway-status'
```

- **Trigger:** AWS IoT Core Last Will and Testament (LWT) or mobile app disconnect events.
- **Target:** AWS Lambda Function (`healthkicks-user-gateway-presence`)

### Environment Variables

| Variable       | Required | Default                                                                | Description                                                               |
| :------------- | :------: | :--------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| `BACKEND_URL`  |   Yes    | `https://healthkicks.duckdns.org:8443/api/v1/internal/device-presence` | FastAPI endpoint for gateway presence updates.                            |
| `INGEST_TOKEN` |   Yes    | `dev-token`                                                            | Secret API authentication token sent via `X-Ingest-Token`.                |
| `VERIFY_SSL`   |    No    | `true`                                                                 | Set to `false` only in development if using self-signed TLS certificates. |

### Source Code (`lambda_function.py`)

```python
import json
import os
import ssl
import urllib.request
from datetime import datetime, timezone


def lambda_handler(event, context):
    print(f"[GATEWAY_PRESENCE] Event received: {json.dumps(event)}")

    backend_url = os.environ.get(
        "BACKEND_URL",
        "https://healthkicks.duckdns.org:8443/api/v1/internal/device-presence"
    )
    ingest_token = os.environ.get("INGEST_TOKEN", "dev-token")
    verify_ssl = os.environ.get("VERIFY_SSL", "true").lower() == "true"

    device_id = event.get("device_id")
    user_id = event.get("user_id")
    state = event.get("state", "offline").lower()

    # Normalize payload for FastAPI backend
    payload = {
        "state": state,
        "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat()
    }

    if device_id:
        payload["device_id"] = str(device_id)
    elif user_id:
        payload["user_id"] = str(user_id)
    else:
        print(f"[GATEWAY_PRESENCE] Event ignored (missing device_id and user_id): {json.dumps(event)}")
        return {"status": "ignored", "reason": "no device_id or user_id"}

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        backend_url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Ingest-Token": ingest_token,
        },
        method="POST"
    )

    # SSL context (allows unverified certificates if VERIFY_SSL=false)
    ssl_context = None if verify_ssl else ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            resp_body = response.read().decode("utf-8")
            print(f"[GATEWAY_PRESENCE] Backend synchronized ({payload}). HTTP {response.status}, Response: {resp_body}")
            return {
                "statusCode": response.status,
                "body": resp_body
            }
    except Exception as e:
        print(f"[GATEWAY_PRESENCE] Error calling backend ({backend_url}): {e}")
        raise e
```

---

## 3. Raw Studio Telemetry Ingestion (DynamoDB & Aurora Sync)

- **IoT Rule Name:** `HealthKicksToDynamoDBLambda`
- **Rule SQL:**

```sql
SELECT *, topic(4) as device_id FROM 'healthkicks/v1/+/telemetry/raw'
```

- **Trigger:** Published by the mobile gateway when an IMU burst session finishes.
- **Target:** AWS Lambda Function (`healthkicks-telemetry-ingest`)

### Environment Variables

| Variable             | Required | Default                                                     | Description                                                                                      |
| :------------------- | :------: | :---------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| `TABLE_NAME`         |   Yes    | `healthkicks_telemetry`                                     | Target Amazon DynamoDB table for raw IMU data points.                                            |
| `BACKEND_INGEST_URL` |   Yes    | `https://api.healthkicks.local/api/v1/ingest/telemetry/raw` | FastAPI webhook endpoint used to update session metadata and sample counts in Aurora PostgreSQL. |
| `INGEST_TOKEN`       |    No    | `""`                                                        | Optional API key passed via the `X-HealthKicks-Ingest-Token` header.                             |

### Source Code (`lambda_function.py`)

```python
import json
import boto3
import os
import urllib.request
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB resource and table handle
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'healthkicks_telemetry')
table = dynamodb.Table(TABLE_NAME)

# Backend FastAPI ingestion webhook configuration
BACKEND_INGEST_URL = os.environ.get('BACKEND_INGEST_URL', 'https://api.healthkicks.local/api/v1/ingest/telemetry/raw')
INGEST_TOKEN = os.environ.get('INGEST_TOKEN', '')


def notify_backend_aurora(
    device_id: str,
    session_id: str,
    label: str,
    sample_count: int,
    duration_sec: float | None,
) -> None:
    """Notify the FastAPI backend to update session metadata in Aurora DB."""
    if not BACKEND_INGEST_URL or not session_id:
        return

    payload = {
        "header": {
            "device_id": device_id,
            "session_id": session_id
        },
        "payload": {
            "device_id": device_id,
            "session_id": session_id,
            "label": label or "unlabeled",
            "sample_count": sample_count,
            "duration_sec": duration_sec
        }
    }

    headers = {
        "Content-Type": "application/json"
    }
    if INGEST_TOKEN:
        headers["X-HealthKicks-Ingest-Token"] = INGEST_TOKEN

    try:
        req = urllib.request.Request(
            BACKEND_INGEST_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[BACKEND_SYNC] Aurora updated for session {session_id}: HTTP {resp.status}")
    except Exception as err:
        print(f"[BACKEND_SYNC_WARN] Failed to update Aurora session {session_id}: {err}")


def lambda_handler(event, context):
    try:
        root_header = event.get('header', {})
        default_device_id = root_header.get('device_id') or event.get('device_id')
        metadata = event.get('metadata', {})
        session_id = metadata.get('session_id') or event.get('session_id')
        label = metadata.get('label') or event.get('label')
        duration_sec = metadata.get('duration_sec') or event.get('duration_sec')

        readings = event.get('readings', [])
        if not readings:
            print("Warning: No readings found in event.")
            return {"status": "No readings found"}

        inserted_count = 0
        skipped_count = 0

        # Batch insert raw readings into DynamoDB
        with table.batch_writer() as batch:
            for index, reading in enumerate(readings):
                sub_header = reading.get('header', {})
                sub_payload = reading.get('payload', {})

                device_id = sub_header.get('device_id') or default_device_id
                if not device_id or not isinstance(device_id, str):
                    skipped_count += 1
                    continue

                payload_keys = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
                is_payload_valid = True
                extracted_values = {}

                for key in payload_keys:
                    val = sub_payload.get(key)
                    if val is None or not isinstance(val, (int, float)) or isinstance(val, bool):
                        is_payload_valid = False
                        break
                    extracted_values[key] = Decimal(str(val))

                if not is_payload_valid:
                    skipped_count += 1
                    continue

                ts_str = sub_header.get('timestamp')
                if ts_str and isinstance(ts_str, str):
                    try:
                        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        timestamp_epoch = int(dt.timestamp() * 1_000_000)
                    except Exception:
                        timestamp_epoch = int(datetime.now().timestamp() * 1_000_000)
                else:
                    timestamp_epoch = int(datetime.now().timestamp() * 1_000_000)

                item = {
                    'device_id': device_id,
                    'timestamp': timestamp_epoch,
                    **extracted_values
                }

                if session_id:
                    item['session_id'] = str(session_id)
                if label:
                    item['label'] = str(label)

                batch.put_item(Item=item)
                inserted_count += 1

        print(f"DynamoDB batch processed: {inserted_count} inserted, {skipped_count} skipped.")

        # Trigger backend webhook to synchronize sample_count in Aurora DB
        if inserted_count > 0 and session_id:
            notify_backend_aurora(
                device_id=default_device_id,
                session_id=session_id,
                label=label,
                sample_count=inserted_count,
                duration_sec=duration_sec
            )

        return {
            "status": "Success",
            "inserted_count": inserted_count,
            "skipped_count": skipped_count
        }

    except Exception as e:
        print(f"CRITICAL ERROR processing telemetry batch: {str(e)}")
        raise e
```

---

## 4. Edge Activity Detection Ingestion (Aurora DB Direct Access)

- **IoT Rule Name:** `HealthKicks_ActivityDetectionIngest`
- **Rule SQL:**

```sql
SELECT * FROM 'healthkicks/v1/+/events/detection'
```

- **Trigger:** Edge device or local gateway ML inference reporting detected steps, jumps, or gait patterns.
- **Target:** AWS Lambda Function (`healthkicks-activity-detection-ingest`)

### Environment Variables

| Variable     | Required | Default      | Description                                          |
| :----------- | :------: | :----------- | :--------------------------------------------------- |
| `DB_HOST`    |   Yes    | —            | Aurora PostgreSQL endpoint hostname.                 |
| `DB_PORT`    |    No    | `5432`       | Aurora PostgreSQL connection port.                   |
| `DB_USER`    |   Yes    | `postgres`   | Database username configured for IAM authentication. |
| `DB_NAME`    |   Yes    | `postgres`   | Target database name.                                |
| `AWS_REGION` |    No    | `eu-north-1` | AWS Region where the Aurora cluster is located.      |

### Source Code (`lambda_function.py`)

```python
import json
import logging
import os
from datetime import datetime, timezone
import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize RDS boto3 client outside the handler for connection reuse
rds_client = boto3.client("rds", region_name=os.environ.get("AWS_REGION", "eu-north-1"))
conn = None


def get_db_connection():
    global conn
    if conn is None or conn.closed:
        host = os.environ["DB_HOST"]
        port = int(os.environ.get("DB_PORT", 5432))
        user = os.environ.get("DB_USER", "postgres")
        region = os.environ.get("AWS_REGION", "eu-north-1")

        logger.info("Generating RDS IAM auth token for user=%s host=%s", user, host)

        # Generate temporary RDS IAM token (valid for 15 minutes)
        auth_token = rds_client.generate_db_auth_token(
            DBHostname=host,
            Port=port,
            DBUsername=user,
            Region=region
        )

        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=os.environ.get("DB_NAME", "postgres"),
            user=user,
            password=auth_token,        # IAM token acts as database password
            sslmode="require",          # Required for RDS IAM authentication
            connect_timeout=5
        )
    return conn


def lambda_handler(event, context):
    logger.info("Received IoT detection event: %s", json.dumps(event))

    device_id = event.get("device_id")
    event_type = event.get("event_type")
    confidence = event.get("confidence")
    timestamp_ms = event.get("timestamp")

    if not device_id or not event_type or confidence is None or timestamp_ms is None:
        logger.error("Invalid payload: missing required fields in %s", json.dumps(event))
        return {"status": "error", "message": "Missing required fields"}

    try:
        timestamp_utc = datetime.fromtimestamp(int(timestamp_ms) / 1000.0, tz=timezone.utc)
        confidence_score = float(confidence)
    except (ValueError, TypeError) as e:
        logger.error("Invalid payload types in %s: %s", json.dumps(event), str(e))
        return {"status": "error", "message": f"Invalid field format: {e}"}

    query = """
        INSERT INTO activity_events (device_id, event_type, confidence_score, timestamp_utc)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (device_id, event_type, confidence_score, timestamp_utc))
            inserted_id = cursor.fetchone()[0]
            connection.commit()

        logger.info("Successfully persisted activity event id=%s for device=%s", inserted_id, device_id)
        return {"status": "ok", "inserted_id": inserted_id}

    except Exception as e:
        logger.exception("Database error while inserting activity event: %s", str(e))
        global conn
        if conn and not conn.closed:
            conn.rollback()
        raise e
```

---

## 5. Fall Alert Lifecycle Relay (FastAPI Internal Webhook)

- **IoT Rule Name:** `healthkicks_fall_alert_rule`
- **Rule SQL:**

```sql
SELECT *, topic(4) as user_id FROM 'healthkicks/v1/users/+/events/fall-alert'
```

- **Trigger:** Published by the mobile gateway in Active Surveillance mode when a fall is detected (`DETECTED`), confirmed early (`CONFIRM`), or cancelled manually / via recovery (`CANCEL`).
- **Target:** AWS Lambda Function (`healthkicks-fall-alert-relay`)

### Environment Variables

| Variable       | Required | Default                                                           | Description                                                               |
| :------------- | :------: | :---------------------------------------------------------------- | :------------------------------------------------------------------------ |
| `BACKEND_URL`  |   Yes    | `https://healthkicks.duckdns.org:8443/api/v1/internal/fall-alerts` | FastAPI internal endpoint for fall alert lifecycle management.            |
| `INGEST_TOKEN` |   Yes    | `dev-token`                                                       | Secret API authentication token sent via `X-Ingest-Token`.                |
| `VERIFY_SSL`   |    No    | `true`                                                            | Set to `false` only in development if using self-signed TLS certificates. |

### Source Code (`lambda_function.py`)

```python
import json
import os
import ssl
import urllib.request


def lambda_handler(event, context):
    print(f"[FALL_ALERT] Event received: {json.dumps(event)}")

    backend_url = os.environ.get(
        "BACKEND_URL",
        "https://healthkicks.duckdns.org:8443/api/v1/internal/fall-alerts"
    )
    ingest_token = os.environ.get("INGEST_TOKEN", "dev-token")
    verify_ssl = os.environ.get("VERIFY_SSL", "true").lower() == "true"

    user_id = event.get("user_id")
    event_id = event.get("event_id")
    action = event.get("action")

    if not user_id or not event_id or not action:
        print(f"[FALL_ALERT] Event ignored (missing user_id, event_id or action): {json.dumps(event)}")
        return {"status": "ignored", "reason": "missing required fields"}

    payload = {
        "user_id": str(user_id),
        "event_id": str(event_id),
        "action": str(action),
        "device_id": event.get("device_id"),
        "event_type": event.get("event_type"),
        "confidence": event.get("confidence"),
        "detected_at": event.get("detected_at"),
        "delivery": event.get("delivery", "live"),
        "location": event.get("location"),
        "cancel_reason": event.get("cancel_reason"),
        "notification_id": event.get("notification_id"),
        "sms_status": event.get("sms_status"),
        "error_message": event.get("error_message"),
        "sent_at": event.get("sent_at"),
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        backend_url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Ingest-Token": ingest_token,
        },
        method="POST"
    )

    ssl_context = None if verify_ssl else ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            resp_body = response.read().decode("utf-8")
            print(f"[FALL_ALERT] Backend synchronized ({event_id}, {action}). HTTP {response.status}, Response: {resp_body}")
            return {
                "statusCode": response.status,
                "body": resp_body
            }
    except Exception as e:
        print(f"[FALL_ALERT] Error calling backend ({backend_url}): {e}")
        raise e
```

---

## 6. Summary Table

| IoT Rule Name                            | MQTT Topic Filter                             | Destination Service                  | Final Data Sink                                                              |
| :--------------------------------------- | :-------------------------------------------- | :----------------------------------- | :--------------------------------------------------------------------------- |
| `healthkicks_device_presence_rule`       | `healthkicks/v1/+/status`                     | Lambda -> FastAPI REST               | Aurora DB (`devices.status`)                                                 |
| `healthkicks_user_gateway_presence_rule` | `healthkicks/v1/users/+/gateway-status`       | Lambda -> FastAPI REST               | Aurora DB (`devices.status`)                                                 |
| `HealthKicksToDynamoDBLambda`            | `healthkicks/v1/+/telemetry/raw`              | Lambda -> DynamoDB + FastAPI Webhook | DynamoDB (`healthkicks_telemetry`) + Aurora (`studio_sessions.sample_count`, `studio_sessions.duration_sec`) |
| `HealthKicks_ActivityDetectionIngest`    | `healthkicks/v1/+/events/detection`           | Lambda -> PostgreSQL (IAM Token)     | Aurora DB (`activity_events`)                                                |
| `healthkicks_fall_alert_rule`            | `healthkicks/v1/users/+/events/fall-alert`    | Lambda -> FastAPI REST               | Aurora DB (`fall_alerts`, `fall_alert_notifications`) + SMTP Email Escalation |


---

## 7. EC2 Backend IoT Core Permissions

The FastAPI backend runs on an EC2 instance associated with IAM Role `EC2ToAuroraBDDAuthRole` (via Instance Profile `EC2ToAuroraInstanceProfile`).
In addition to Aurora connection and STS assume-role capabilities, the EC2 role requires permission to publish MQTT commands to devices and downlink fall alert status updates to mobile applications via AWS IoT Core (`iot-data:Publish`).

### IAM Inline Policy: `HealthKicks-EC2-IoTPublishPolicy`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowIoTPublishHapticCommands",
      "Effect": "Allow",
      "Action": [
        "iot:Publish"
      ],
      "Resource": "arn:aws:iot:eu-north-1:693906847467:topic/healthkicks/v1/*/commands/*"
    },
    {
      "Sid": "AllowIoTPublishFallAlertDownlink",
      "Effect": "Allow",
      "Action": [
        "iot:Publish"
      ],
      "Resource": "arn:aws:iot:eu-north-1:693906847467:topic/healthkicks/v1/users/*/fall-alert/status"
    }
  ]
}
```
