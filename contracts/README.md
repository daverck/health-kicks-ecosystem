# Exchange Contracts Repository - HealthKicks Ecosystem

This directory serves as the **single source of truth** for all data formats, interface schemas, and communication protocols shared across the subsystems of the **HealthKicks** ecosystem.

Any agent or developer must adhere to the **Spec-First** protocol described below before adding or modifying an interface.

---

## 1. Contracts Governance Protocol (Spec-First)

1. **No Unilateral Modifications**: No subproject may alter a JSON payload, an MQTT topic, or a REST endpoint without first updating the corresponding contract in this repository.
2. **Evolution Lifecycle**:
   - The orchestrator or developer proposes a contract update in `contracts/`.
   - Impacts are reviewed across affected agents (`firmware-dev`, `mobile-dev`, `backend-dev`, `frontend-dev`).
   - Once the contract is validated, implementations in subprojects proceed in parallel or in ordered phases.
   - Schema compatibility and tests are validated.

---

## 2. REST API Contracts (Backend <-> Frontend)

HTTP REST exchange contracts are based on **OpenAPI 3.1** specifications and **Pydantic v2** models exposed by FastAPI.

### A. Core Endpoints & Associated Schemas

| Domain                                | Method & Route                                                                                                                                                                                             | Request Payload                                                                                                                                                                                                                                                                     | Response Payload                                                                                                                                                                                                                            |
| :------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **OAuth2 Authentication (Login)**     | `GET /api/v1/auth/{provider}/login`                                                                                                                                                                        | Query params: `redirect_uri`, `state`, `code_challenge` _(optional, PKCE S256)_, `code_challenge_method` (`S256`)                                                                                                                                                                   | `{"authorization_url": "string", "state": "string"}`                                                                                                                                                                                        |
| **OAuth2 Ticket Exchange (One-Time)** | `POST /api/v1/auth/token/exchange`                                                                                                                                                                         | `{"ticket": "string", "code_verifier": "string"}` _(code_verifier optional if PKCE initiated)_                                                                                                                                                                                      | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer", "user": UserProfileResponse}`                                                                                                                                |
| **OAuth2 Callback (POST)**            | `POST /api/v1/auth/{provider}/callback`                                                                                                                                                                    | `{"code": "string", "state": "string", "redirect_uri": "string", "code_verifier": "string"}`                                                                                                                                                                                        | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer", "user": UserProfileResponse}`                                                                                                                                |
| **JWT Refresh**                       | `POST /api/v1/auth/refresh`                                                                                                                                                                                | `{"refresh_token": "string"}`                                                                                                                                                                                                                                                       | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer"}`                                                                                                                                                             |
| **IoT STS Credentials**               | `POST /api/v1/auth/iot-credentials`                                                                                                                                                                        | `{"device_id": "string"}` _(optional)_                                                                                                                                                                                                                                              | `{"access_key_id": "string", "secret_access_key": "string", "session_token": "string", "expiration": "datetime", "iot_endpoint": "string", "region": "string", "user_uuid": "string"}`                                                      |
| **Haptic Trigger**                    | `POST /api/v1/devices/{id}/haptic/trigger`                                                                                                                                                                 | `{"intensity": 200, "duration_ms": 500}`                                                                                                                                                                                                                                            | `{"status": "queued", "device_id": "HK-1", "command_id": "uuid"}`                                                                                                                                                                           |
| **Studio Dataset Stats**              | `GET /api/v1/studio/stats`<br>`GET /api/v1/devices/{device_id}/studio/stats`                                                                                                                               | Header: `Authorization: Bearer <jwt>`. Aggregated statistics (global or per-device).                                                                                                                                                                                                | `StudioDatasetStatsResponse` (`total_sessions`, `total_duration_sec`, `total_samples`, `by_label`, `by_label_validated`: dict[str, int], `by_label_pending`: dict[str, int], `edge_ai_labels`: list[str])                                   |
| **Studio Classes Summary**            | `GET /api/v1/studio/classes/summary`                                                                                                                                                                       | Header: `Authorization: Bearer <jwt>` (Clinician or Admin). Consolidated overview of all classes: session volume, durations, and champion ML metrics (including `confusion_matrix`: `StudioConfusionMatrix`).                                                                       | `StudioClassesSummaryResponse` (`classes`: list[`StudioClassSummaryItem`], `confusion_matrix`: `StudioConfusionMatrix` optional)                                                                                                            |
| **Studio Class Stats**                | `GET /api/v1/studio/classes/{label}/stats`                                                                                                                                                                 | Header: `Authorization: Bearer <jwt>` (Clinician or Admin). Detailed stats for an activity class: daily distribution, duration metrics (median, mean, std, min, max), and class ML performance.                                                                                     | `StudioClassDetailStatsResponse` (`label`, `total_sessions`, `validated_sessions`, `pending_sessions`, `duration_metrics`: `StudioClassDurationStats`, `ml_metrics`: `StudioClassMlMetrics`, `daily_counts`: list[`StudioClassDailyCount`]) |
| **Studio Sessions**                   | `GET /api/v1/studio/sessions`                                                                                                                                                                              | Query params: `page`, `size`, `is_validated`, `is_hitl` (`true`\|`false`), `label` (single or comma-separated e.g. `walk,run`), `device_id` (single, comma-separated e.g. `HK-1,HK-2`, or `all`), `pseudonym` (e.g. `SUBJ-XXXXXXXX`), `start_date`, `end_date`                      | `PaginatedSessionsResponse` (list of `StudioSessionSummary` with `uuid`, `author_uuid`, `author_pseudonym`, `is_hitl`, `subject_pseudonym`, `is_pseudonymized`, and PII masking for third parties)                                          |
| **Studio Authors**                    | `GET /api/v1/studio/sessions/authors`                                                                                                                                                                      | -                                                                                                                                                                                                                                                                                   | `list[StudioAuthorSummary]` (`[{"author_uuid": str, "author_pseudonym": str, "email": str, "name": str, "subject_pseudonym": str, "is_pseudonymized": bool}]` read directly from indexed `User.pseudonym`, without numeric IDs)             |
| **User Accounts (Admin)**             | `GET /api/v1/users`<br>`PATCH /api/v1/users/{user_uuid}`                                                                                                                                                   | Header: `Authorization: Bearer <jwt>` (Admin for listing; admin or own profile for update). Strict identification via `user_uuid`; suppression of all sequential numeric IDs.                                                                                                       | `list[UserResponse]`, `UserResponse` (`uuid`, `pseudonym`, `email`, `name`, `role`, `is_active`)                                                                                                                                            |
| **Device Management**                 | `POST /api/v1/devices`<br>`GET /api/v1/devices`<br>`DELETE /api/v1/devices/{device_uuid}`                                                                                                                  | `DeviceCreate` (`device_id` auto-generated as UUID if omitted, `user_uuid`), `GET` filterable by `user_uuid`, dissociation exclusively by `device_uuid`.                                                                                                                            | `list[DeviceResponse]`, `DeviceResponse` (`uuid`, `device_id`, `name`, `status`, `is_online`, `last_seen_utc` — sequential `id` masked)                                                                                                     |
| **Studio Telemetry**                  | `GET /api/v1/studio/sessions/{id}/readings`                                                                                                                                                                | -                                                                                                                                                                                                                                                                                   | `StudioSessionReadingsResponse` (`readings`: list of raw IMU samples)                                                                                                                                                                       |
| **Studio Trimming**                   | `PATCH /api/v1/studio/sessions/{id}/trim`                                                                                                                                                                  | `{"start_offset_sec": 1.0, "end_offset_sec": 3.0}` (retained interval `> 0.5 s`, unvalidated sessions only; legacy `new_duration_sec` remains accepted for trimming from the start)                                                                                                 | `StudioSessionSummary` (updated `duration_sec` and `sample_count`)                                                                                                                                                                          |
| **Studio Relabeling**                 | `PATCH /api/v1/studio/sessions/{id}`                                                                                                                                                                       | `{"label": "walk", "is_validated": true}` or `{"is_validated": false}` to return a session to pending review                                                                                                                                                                        | `StudioSessionSummary`                                                                                                                                                                                                                      |
| **Webhook Ingestion**                 | `POST /api/v1/ingest/event`                                                                                                                                                                                | Header: `X-HealthKicks-Ingest-Token`<br>Body: Detection event payload                                                                                                                                                                                                               | `{"status": "accepted", "event_id": "uuid"}`                                                                                                                                                                                                |
| **Device Presence (Internal)**        | `POST /api/v1/internal/device-presence`                                                                                                                                                                    | Header: `X-Ingest-Token`<br>Body: `DevicePresencePayload` (`device_id` or `user_id`, `state`)                                                                                                                                                                                       | `{"status": "ok", "device_id": "string", "device_status": "online/offline"}`                                                                                                                                                                |
| **Fall Alerts (Internal)**            | `POST /api/v1/internal/fall-alerts`                                                                                                                                                                        | Header: `X-Ingest-Token`<br>Body: `FallAlertIngestPayload` (`user_id`, `event_id`, `action` ∈ `DETECTED\|CONFIRM\|CANCEL\|SMS_STATUS`, `device_id`, `event_type`, `confidence`, `detected_at`, `delivery`, `location`, `cancel_reason`, `notification_id`, `sms_status`, `sent_at`) | `FallAlertIngestResponse` (`status`, `alert_id`, `event_id`, `state`, `duplicate`)                                                                                                                                                          |
| **SMS Status Report (Mobile)**        | `POST /api/v1/fall-alerts/sms-status`                                                                                                                                                                      | Header: `Authorization: Bearer <jwt>`<br>Body: `FallAlertSmsStatusRequest` (`notification_id`, `sms_status` ∈ `SENT\|FAILED`, `error_message`, `sent_at`)                                                                                                                           | `FallAlertIngestResponse` (`status`, `alert_id`, `event_id`, `state`, `duplicate`)                                                                                                                                                          |
| **Emergency Contacts (CRUD & Order)** | `GET/POST /api/v1/users/me/alert-contacts`<br>`PUT /api/v1/users/me/alert-contacts/order`<br>`PATCH/DELETE /api/v1/users/me/alert-contacts/{id}`<br>`POST /api/v1/users/me/alert-contacts/{id}/test-email` | `AlertContactCreate`, `AlertContactUpdate`, `AlertContactsOrderPayload`                                                                                                                                                                                                             | `list[AlertContactResponse]`, `AlertContactResponse`, `AlertContactTestEmailResponse`                                                                                                                                                       |
| **Fall Alert History**                | `GET /api/v1/fall-alerts`<br>`GET /api/v1/fall-alerts/{alert_id_or_uuid}`                                                                                                                                  | Query params: `page`, `page_size`, `state`, `start_date`, `end_date`, `pseudonym` _(`SUBJ-XXXXXXXX` pseudonym, admin only)_                                                                                                                                                         | `PaginatedFallAlertsResponse`, `FallAlertDetail` (with systematic pseudonymization `Patient SUBJ-XXXXXXXX` for display, exposing `uuid`, `user_uuid`, `user_pseudonym`)                                                                     |
| **Alert Metadata (Public Safe)**      | `GET /api/v1/fall-alerts/ack/info`                                                                                                                                                                         | Query param: `token` (HMAC signed 2-hour token)                                                                                                                                                                                                                                     | `FallAlertAckInfoResponse` (secure read-only metadata for frontend SPA)                                                                                                                                                                     |
| **Alert Acknowledgment (Public)**     | `POST /api/v1/fall-alerts/ack`                                                                                                                                                                             | Body JSON: `{"token": "string"}` (HMAC signed 2-hour token)                                                                                                                                                                                                                         | `FallAlertAckResultResponse` (`{"status": "ok", "state": "ACKNOWLEDGED", ...}`)                                                                                                                                                             |
| **Step Synchronization**              | `POST /api/v1/steps/sync`                                                                                                                                                                                  | `DailyStepsSyncPayload` (`device_id`, `date`, `hourly_steps`: list of `{"hour", "activity_type", "step_count"}`)                                                                                                                                                                    | `{"status": "synchronized", "synced_records": int}`                                                                                                                                                                                         |
| **Step History**                      | `GET /api/v1/steps/history`                                                                                                                                                                                | Query params: `device_id` (required), `from_date`, `to_date`, `days` (default: 30)                                                                                                                                                                                                  | `DailyStepsHistoryResponse` (`history`: list of `{"date", "total_steps", "by_activity"}`)                                                                                                                                                   |
| **Hourly Step Breakdown**             | `GET /api/v1/steps/hourly`                                                                                                                                                                                 | Query params: `device_id` (required), `date` (required, YYYY-MM-DD)                                                                                                                                                                                                                 | `HourlyStepsResponse` (`device_id`, `date`, `hourly_data`: list of 24 `{"hour", "total_steps", "by_activity"}`)                                                                                                                             |
| **Activity & Fall Events**            | `GET /api/v1/devices/{device_id}/events/activities`                                                                                                                                                        | Query params: `page`, `page_size`, `event_type` (single, comma-separated e.g. `walk,run`, or `falls`), `start_date`, `end_date`<br>Path param: `device_id` (single identifier, comma-separated e.g. `HK-1,HK-2`, or `all`)                                                          | `ActivityEventPage` (list of `ActivityEventResponse`)                                                                                                                                                                                       |
| **Haptic History**                    | `GET /api/v1/devices/{device_id}/haptic/history`                                                                                                                                                           | Query params: `page`, `page_size`, `start_date`, `end_date`<br>Path param: `device_id` (single identifier, comma-separated e.g. `HK-1,HK-2`, or `all`)                                                                                                                              | `HapticLogPage` (list of `HapticLogResponse`)                                                                                                                                                                                               |
| **S3 Firmware Distribution**          | `GET /api/v1/firmware/latest`                                                                                                                                                                              | Header: `Authorization: Bearer <jwt>`                                                                                                                                                                                                                                               | `FirmwareLatestResponse` (`version`, `download_url`, `sha256`, `size_bytes`, `expires_in_seconds`, `release_date`)                                                                                                                          |

### B. Telemetry IMU Sample Format (`IMUReading`)

```json
{
  "timestamp": 1726224000.125,
  "ax": 0.052,
  "ay": 0.981,
  "az": 0.124,
  "gx": 0.012,
  "gy": -0.045,
  "gz": 0.008
}
```

### C. Secure S3 Firmware Distribution (`GET /api/v1/firmware/latest`)

Allows client applications (e.g. Flutter mobile app) to retrieve a temporary pre-signed AWS S3 download URL for the latest firmware binary, secured via centralized JWT access control.

**S3 Retention Rule:** Exactly one firmware binary is retained on S3 (key `firmware/esp32s3/latest/firmware.bin`), overwritten with each release pipeline execution.

_Example JSON response (`FirmwareLatestResponse`):_

```json
{
  "version": "v1.2.1-esp32s3",
  "download_url": "https://healthkicks-firmware-releases.s3.eu-north-1.amazonaws.com/firmware/esp32s3/latest/firmware.bin?AWSAccessKeyId=...&Signature=...&Expires=...",
  "sha256": "8a32f6b3e7d581f148e658091ecb6a93ad5d24d26f047ff690b200b3e55c2aa7",
  "size_bytes": 1048576,
  "expires_in_seconds": 900,
  "release_date": "2026-10-06T21:30:00Z"
}
```

---

## 3. IoT MQTT Contracts (Edge <-> AWS IoT Core <-> Backend)

IoT communications use MQTT over AWS IoT Core following a strict hierarchical naming convention under prefix `healthkicks/v1/{device_id}/` or `healthkicks/v1/users/{user_uuid}/`.

### A. Detection Alert Topic: `healthkicks/v1/{device_id}/events/detection`

Published by the Edge agent or mobile gateway with QoS 1 when an event (activity or critical fall) is detected by the local ML model:

```json
{
  "device_id": "HK-1",
  "event_type": "fall_forward",
  "confidence": 0.87,
  "timestamp": 1726224000123,
  "is_fall": true,
  "haptic_triggered": true
}
```

_Validation constraints:_

- `device_id`: Sensor identifier (non-empty string).
- `event_type`: Detected activity type (`idle`, `walk`, `run`, `stairs_up`, `stairs_down`, `sit_down`, `stand_up`, `lying_supine`, `lying_prone`, `lying_lateral`, `jump`, `lie_down`, `fall_forward`, `fall_backward`, `fall_lateral`, `fall_recovery`, `fall_generic`, `stumble_recover`, `inactivity_alert`).
- `confidence`: Float between `0.0` and `1.0`.
- `timestamp`: Integer representing UTC Epoch timestamp in milliseconds (`ms`).
- `is_fall`: Boolean (`true` for critical fall).
- `haptic_triggered`: Boolean (`true` if autonomous local vibration was triggered).

### B. Haptic Command Topic: `healthkicks/v1/{device_id}/commands/haptic`

Published by the Cloud backend via AWS IoT Core `iot-data` to trigger a vibration on the footwear:

```json
{
  "command_id": "4f9d8a32-1234-4567-89ab-cdef01234567",
  "intensity": 200,
  "duration_ms": 500,
  "pattern": "single_pulse",
  "created_at": "2026-09-13T10:14:02.000Z"
}
```

_Validation constraints:_

- `intensity`: Integer between `0` (off) and `255` (maximum power).
- `duration_ms`: Integer between `50` and `10000` milliseconds.

### C. Status & Heartbeat Topic: `healthkicks/v1/{device_id}/status`

Published periodically by the Edge agent with retention / Last Will and Testament (LWT) configured on disconnect:

```json
{
  "device_id": "HK-1",
  "state": "online",
  "firmware_version": "0.1.0",
  "model_version": "1.4.2",
  "uptime_seconds": 3600,
  "timestamp": "2026-09-13T10:14:05.000Z"
}
```

_LWT Payload (upon unexpected connection loss):_

```json
{
  "device_id": "HK-1",
  "state": "offline",
  "timestamp": "2026-09-13T10:15:00.000Z"
}
```

### D. Studio Telemetry Topic: `healthkicks/v1/{device_id}/telemetry/raw`

Published upon completion of a Studio capture session for storage in Amazon DynamoDB:

```json
{
  "device_id": "HK-1",
  "session_id": "7b8e9f01-2345-6789-abcd-ef0123456789",
  "label": "walk",
  "trigger": "studio",
  "is_hitl": false,
  "sample_rate_hz": 100,
  "readings": [
    {
      "timestamp": 1726224000.0,
      "ax": 0.02,
      "ay": 0.98,
      "az": 0.11,
      "gx": 0.01,
      "gy": -0.01,
      "gz": 0.02
    },
    {
      "timestamp": 1726224000.01,
      "ax": 0.03,
      "ay": 0.97,
      "az": 0.12,
      "gx": 0.02,
      "gy": -0.02,
      "gz": 0.01
    }
  ]
}
```

### E. User Gateway LWT Topic: `healthkicks/v1/users/{user_uuid}/gateway-status`

Published automatically by the AWS IoT Core broker upon unexpected loss of the mobile gateway (crash, network disruption, battery depletion):

```json
{
  "user_uuid": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "state": "offline",
  "gateway": "mobile"
}
```

_Backend effect:_ Switches all devices associated with the user to `offline` status.

### F. Fall Alerting Topics: `healthkicks/v1/users/{user_uuid}/events/fall-alert` & `.../fall-alert/status`

Detailed specifications in [`contracts/fall_alerting.md`](fall_alerting.md):

- **Uplink (`healthkicks/v1/users/{user_uuid}/events/fall-alert`)**: Emitted by the mobile app upon fall detection (`DETECTED`), immediate confirmation for help (`CONFIRM`), manual cancellation / recovery (`CANCEL`), or SMS delivery report (`SMS_STATUS`).
- **Downlink (`healthkicks/v1/users/{user_uuid}/fall-alert/status`)**: Published by the backend upon state changes (`PENDING`, `ESCALATING`, `ACKNOWLEDGED`, `CANCELLED`, `EXHAUSTED`, `SUPPRESSED`) and conveying the `sms_command` instruction for the mobile GSM relay.

---

## 4. Hardware Binary Specifications & Dedicated Protocols

For direct Bluetooth Low Energy (BLE GATT) communications and cross-cutting workflows, canonical protocols are documented in dedicated specifications:

- [`contracts/ble_gatt_specs.md`](ble_gatt_specs.md): Service and characteristic UUID table, activity state codes, packed binary structures.
- [`contracts/studio_burst_protocol.md`](studio_burst_protocol.md): High-frequency IMU signal transmission protocol (control opcodes, 4-byte header, 12-byte big-endian int16 IMU frames).
- [`contracts/ota_ble_protocol.md`](ota_ble_protocol.md): Wireless firmware update protocol (Start/Data/End opcodes, magic byte `0xE9`, mandatory 32-byte SHA-256 digest, error codes, and rollback probation period).
- [`contracts/fall_alerting.md`](fall_alerting.md): Fall alert lifecycle, sequential email and SMS escalation, HMAC signed acknowledgment tokens, MQTT and REST contracts.
