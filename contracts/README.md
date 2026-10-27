# Référentiel des Contrats d'Échange - HealthKicks Ecosystem

Ce répertoire constitue la **source unique de vérité** pour tous les formats de données, schémas d'interface et protocoles échangés entre les sous-systèmes de l'écosystème **HealthKicks**.

Tout agent ou développeur doit suivre le protocole **Spec-First** décrit ci-dessous avant de modifier ou d'ajouter une interface.

---

## 1. Protocole de Gouvernance des Contrats (Spec-First)

1. **Interdiction de modification unilatérale** : Aucun sous-projet ne peut altérer un payload JSON, un topic MQTT ou un endpoint REST sans modification préalable d'un contrat dans ce répertoire.
2. **Cycle d'évolution** :
   - L'orchestrateur ou le développeur propose une mise à jour d'un contrat dans `contracts/rest/` ou `contracts/mqtt/`.
   - Les impacts sont revus auprès des agents concernés (`firmware-dev`, `mobile-dev`, `backend-dev`, `frontend-dev`).
   - Une fois le contrat validé, les implémentations dans les sous-projets sont réalisées en parallèle ou de manière ordonnée.
   - Les tests de compatibilité de schéma sont validés.

---

## 2. Contrats REST API (Backend <-> Frontend)

Les contrats d'échange HTTP REST sont basés sur les spécifications **OpenAPI 3.1** et les modèles **Pydantic v2** exposés par FastAPI.

### A. Endpoints Principaux & Schémas Associés

| Domaine                              | Méthode & Route                                         | Payload Requête                                                                                                                                                                                                                                                                                                                | Payload Réponse                                                                                                                                                                |
| :----------------------------------- | :------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Authentification OAuth2 (Login)**  | `GET /api/v1/auth/{provider}/login`                     | Query params: `redirect_uri`, `state`, `code_challenge` _(optionnel, PKCE S256)_, `code_challenge_method` (`S256`)                                                                                                                                                                                                             | `{"authorization_url": "string", "state": "string"}`                                                                                                                           |
| **Échange Ticket OAuth2 (One-Time)** | `POST /api/v1/auth/token/exchange`                      | `{"ticket": "string", "code_verifier": "string"}` _(code_verifier optionnel si PKCE initié)_                                                                                                                                                                                                                                   | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer", "user": UserProfileResponse}`                                                                   |
| **Callback OAuth2 (POST)**           | `POST /api/v1/auth/{provider}/callback`                 | `{"code": "string", "state": "string", "redirect_uri": "string", "code_verifier": "string"}`                                                                                                                                                                                                                    | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer", "user": UserProfileResponse}`                                                                   |
| **Rafraîchissement JWT**             | `POST /api/v1/auth/refresh`                             | `{"refresh_token": "string"}`                                                                                                                                                                                                                                                                                                  | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer"}`                                                                                                |
| **Identifiants IoT STS**             | `POST /api/v1/auth/iot-credentials`                     | `{"device_id": "string"}` _(optionnel)_                                                                                                                                                                                                                                                                                        | `{"access_key_id": "string", "secret_access_key": "string", "session_token": "string", "expiration": "datetime", "iot_endpoint": "string", "region": "string"}`                |
| **Haptique**                         | `POST /api/v1/devices/{id}/haptic/trigger`              | `{"intensity": 200, "duration_ms": 500}`                                                                                                                                                                                                                                                                                       | `{"status": "queued", "device_id": "HK-1", "command_id": "uuid"}`                                                                                                              |
| **Studio Sessions**                  | `GET /api/v1/studio/sessions`                           | Query params: `page`, `size`, `is_validated`, `is_hitl` (`true`\|`false`), `label` (valeur unique ou liste séparée par virgule ex: `walk,run`), `device_id` (valeur unique, liste séparée par virgule ex: `HK-1,HK-2`, ou `all`), `pseudonym` (ex: `SUBJ-XXXXXXXX`), `start_date`, `end_date` | `PaginatedSessionsResponse` (liste de `StudioSessionSummary` avec `author_uuid`, `author_pseudonym`, `is_hitl`, `subject_pseudonym`, `is_pseudonymized` et masquage PII pour les tiers) |
| **Studio Authors**                   | `GET /api/v1/studio/sessions/authors`                   | -                                                                                                                                                                                                                                                                                                                              | `list[StudioAuthorSummary]` (`[{"author_uuid": str, "email": str, "name": str, "subject_pseudonym": str, "is_pseudonymized": bool}]` lu directement depuis `User.pseudonym` indexé en base) |
| **Comptes Utilisateurs (Admin)**    | `GET /api/v1/users`<br>`PATCH /api/v1/users/{user_uuid}` | Header: `Authorization: Bearer <jwt>` (Admin pour listage, admin ou profil propre pour mise à jour). Identification stricte par `user_uuid` ; suppression de tout ID numérique séquentiel.                                                                                                                                     | `list[UserResponse]`, `UserResponse` (`uuid`, `pseudonym`, `email`, `name`, `role`, `is_active`)                                                                                              |
| **Gestion Équipements**             | `POST /api/v1/devices`<br>`GET /api/v1/devices`<br>`DELETE /api/v1/devices/{device_id_or_uuid}` | `DeviceCreate` (`device_id` auto-généré sous forme d'UUID si omis, `user_uuid`), `GET` filtrable par `user_uuid`, dissociation par identifiant d'équipement.                                                                                                                                                                 | `list[DeviceResponse]`, `DeviceResponse` (`uuid`, `device_id`, `name`, `status`, `is_online`, `last_seen_utc` — `id` séquentiel masqué)                                                      |
| **Studio Telemetry**                 | `GET /api/v1/studio/sessions/{id}/readings`             | -                                                                                                                                                                                                                                                                                                                              | `StudioSessionReadingsResponse` (`readings`: liste d'échantillons IMU)                                                                                                         |
| **Rognage Studio**                   | `PATCH /api/v1/studio/sessions/{id}/trim`               | `{"start_offset_sec": 1.0, "end_offset_sec": 3.0}` (intervalle conservé `> 0.5 s`, session non validée uniquement; l'ancien `new_duration_sec` reste accepté pour un rognage depuis le début)                                                                                                                                      | `StudioSessionSummary` (`duration_sec` et `sample_count` mis à jour)                                                                                                           |
| **Requalification Studio**           | `PATCH /api/v1/studio/sessions/{id}`                    | `{"label": "walk", "is_validated": true}` ou `{"is_validated": false}` pour repasser une session en attente                                                                                                                                                                                                                    | `StudioSessionSummary`                                                                                                                                                         |
| **Ingestion Webhook**                | `POST /api/v1/ingest/event`                             | Header: `X-HealthKicks-Ingest-Token`<br>Body: Payload d'événement détection                                                                                                                                                                                                                                                    | `{"status": "accepted", "event_id": "uuid"}`                                                                                                                                   |
| **Présence Équipements (Interne)**   | `POST /api/v1/internal/device-presence`                 | Header: `X-Ingest-Token`<br>Body: `DevicePresencePayload` (`device_id` ou `user_id`, `state`)                                                                                                                                                                                                                                  | `{"status": "ok", "device_id": "string", "device_status": "online/offline"}`                                                                                                   |
| **Alertes de Chute (Interne)**       | `POST /api/v1/internal/fall-alerts`                     | Header: `X-Ingest-Token`<br>Body: `FallAlertIngestPayload` (`user_id`, `event_id`, `action` ∈ `DETECTED\|CONFIRM\|CANCEL\|SMS_STATUS`, `device_id`, `event_type`, `confidence`, `detected_at`, `delivery`, `location`, `cancel_reason`, `notification_id`, `sms_status`, `sent_at`)                                     | `FallAlertIngestResponse` (`status`, `alert_id`, `event_id`, `state`, `duplicate`)                                                                                             |
| **Rapport Statut SMS (Mobile)**      | `POST /api/v1/fall-alerts/sms-status`                   | Header: `Authorization: Bearer <jwt>`<br>Body: `FallAlertSmsStatusRequest` (`notification_id`, `sms_status` ∈ `SENT\|FAILED`, `error_message`, `sent_at`)                                                                                                                                                                      | `FallAlertIngestResponse` (`status`, `alert_id`, `event_id`, `state`, `duplicate`)                                                                                             |
| **Proches d'Urgence (CRUD & Ordre)** | `GET/POST /api/v1/users/me/alert-contacts`<br>`PUT /api/v1/users/me/alert-contacts/order`<br>`PATCH/DELETE /api/v1/users/me/alert-contacts/{id}`<br>`POST /api/v1/users/me/alert-contacts/{id}/test-email` | `AlertContactCreate`, `AlertContactUpdate`, `AlertContactsOrderPayload`                                                                                                                                                                                                                                                        | `list[AlertContactResponse]`, `AlertContactResponse`, `AlertContactTestEmailResponse`                                                                                          |
| **Historique Alertes de Chute**      | `GET /api/v1/fall-alerts`<br>`GET /api/v1/fall-alerts/{alert_id_or_uuid}` | Query params: `page`, `page_size`, `state`, `start_date`, `end_date`, `pseudonym` _(pseudonyme `SUBJ-XXXXXXXX`, admin uniquement)_                                                                                                                                                                              | `PaginatedFallAlertsResponse`, `FallAlertDetail` (avec pseudonymisation systématique `Patient SUBJ-XXXXXXXX` pour l'affichage, exposition de `uuid`, `user_uuid`, `user_pseudonym`)                                                  |
| **Métadonnées Alerte (Public Safe)** | `GET /api/v1/fall-alerts/ack/info`                      | Query param: `token` (jeton signé HMAC 2 h)                                                                                                                                                                                                                                                                                    | `FallAlertAckInfoResponse` (lecture seule sécurisée pour la SPA frontend)                                                                                                       |
| **Prise en Charge Alerte (Public)**  | `POST /api/v1/fall-alerts/ack`                          | Body JSON: `{"token": "string"}` (jeton signé HMAC 2 h)                                                                                                                                                                                                                                                                        | `FallAlertAckResultResponse` (`{"status": "ok", "state": "ACKNOWLEDGED", ...}`)                                                                                                |
| **Synchronisation des Pas**          | `POST /api/v1/steps/sync`                               | `DailyStepsSyncPayload` (`device_id`, `date`, `hourly_steps`: liste de `{"hour", "activity_type", "step_count"}`)                                                                                                                                                                                                            | `{"status": "synchronized", "synced_records": int}`                                                                                                                            |
| **Historique des Pas**               | `GET /api/v1/steps/history`                             | Query params: `device_id` (requis), `from_date`, `to_date`, `days` (défaut: 30)                                                                                                                                                                                                                                                | `DailyStepsHistoryResponse` (`history`: liste de `{"date", "total_steps", "by_activity"}`)                                                                                     |
| **Ventilation Horaire des Pas**      | `GET /api/v1/steps/hourly`                              | Query params: `device_id` (requis), `date` (requis, YYYY-MM-DD)                                                                                                                                                                                                                                                                 | `HourlyStepsResponse` (`device_id`, `date`, `hourly_data`: liste de 24 `{"hour", "total_steps", "by_activity"}`)                                                               |
| **Événements d'Activités & Chutes**  | `GET /api/v1/devices/{device_id}/events/activities`     | Query params: `page`, `page_size`, `event_type` (valeur unique, liste séparée par virgule ex: `walk,run`, ou `falls`), `start_date`, `end_date`<br>Path param: `device_id` (identifiant unique, liste séparée par virgule ex: `HK-1,HK-2`, ou `all`)                                                                           | `ActivityEventPage` (liste d'`ActivityEventResponse`)                                                                                                                          |
| **Historique Haptique**              | `GET /api/v1/devices/{device_id}/haptic/history`        | Query params: `page`, `page_size`, `start_date`, `end_date`<br>Path param: `device_id` (identifiant unique, liste séparée par virgule ex: `HK-1,HK-2`, ou `all`)                                                                                                                                                               | `HapticLogPage` (liste d'`HapticLogResponse`)                                                                                                                                  |
| **Distribution Firmware S3**         | `GET /api/v1/firmware/latest`                           | Header: `Authorization: Bearer <jwt>`                                                                                                                                                                                                                                                                                          | `FirmwareLatestResponse` (`version`, `download_url`, `sha256`, `size_bytes`, `expires_in_seconds`, `release_date`)                                                             |

### B. Format d'un Échantillon IMU Télémétrique (`IMUReading`)

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

### C. Distribution du Firmware Sécurisé S3 (`GET /api/v1/firmware/latest`)

Permet aux clients (ex: application mobile Flutter) de récupérer une URL de téléchargement pré-signée AWS S3 temporaire pour le binaire firmware le plus récent, avec contrôle d'accès JWT centralisé.

**Règle de rétention S3 :** Un seul et unique binaire firmware est conservé sur S3 (clé `firmware/esp32s3/latest/firmware.bin`), écrasé à chaque exécution du pipeline de publication.

_Exemple de réponse JSON (`FirmwareLatestResponse`)_ :

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

## 3. Contrats MQTT IoT (Edge <-> AWS IoT Core <-> Backend)

Les communications IoT utilisent le protocole MQTT sur AWS IoT Core avec une convention de nommage hiérarchique stricte sous le préfixe `healthkicks/v1/{device_id}/` ou `healthkicks/v1/users/{user_uuid}/`.

### A. Topic d'Alerte de Détection : `healthkicks/v1/{device_id}/events/detection`

Publié par l'agent Edge ou la passerelle mobile en QoS 1 lorsqu'un événement (activité ou chute critique) est détecté par le modèle ML local :

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

_Contraintes de validation_ :

- `device_id` : Identifiant du capteur (chaîne non vide).
- `event_type` : Type d'activité détectée (`idle`, `walk`, `run`, `stairs_up`, `stairs_down`, `fall_forward`, `fall_backward`, `fall_lateral`, `fall_recovery`, `fall_generic`, `stumble_recover`).
- `confidence` : Flottant compris entre `0.0` et `1.0`.
- `timestamp` : Entier représentant l'horodatage Epoch UTC en millisecondes (`ms`).
- `is_fall` : Booléen (`true` si chute critique).
- `haptic_triggered` : Booléen (`true` si vibration locale autonome déclenchée).

### B. Topic de Commande Haptique : `healthkicks/v1/{device_id}/commands/haptic`

Publié par le backend Cloud via AWS IoT Core `iot-data` pour commander une vibration sur la chaussure :

```json
{
  "command_id": "4f9d8a32-1234-4567-89ab-cdef01234567",
  "intensity": 200,
  "duration_ms": 500,
  "pattern": "single_pulse",
  "created_at": "2026-09-13T10:14:02.000Z"
}
```

_Contraintes de validation_ :

- `intensity` : entier compris entre `0` (arrêt) et `255` (puissance maximale).
- `duration_ms` : entier compris entre `50` et `10000` millisecondes.

### C. Topic de Statut & Heartbeat : `healthkicks/v1/{device_id}/status`

Publié périodiquement par l'agent Edge avec rétention / Last Will and Testament (LWT) configuré sur la déconnexion :

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

_LWT Payload (en cas de perte de connexion inopinée)_ :

```json
{
  "device_id": "HK-1",
  "state": "offline",
  "timestamp": "2026-09-13T10:15:00.000Z"
}
```

### D. Topic de Télémétrie Studio : `healthkicks/v1/{device_id}/telemetry/raw`

Publié à l'issue d'une session de capture Studio pour enregistrement dans Amazon DynamoDB :

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

### E. Topic LWT Passerelle Utilisateur : `healthkicks/v1/users/{user_uuid}/gateway-status`

Publié automatiquement par le broker AWS IoT Core en cas de rupture inopinée de la passerelle mobile (crash, coupure réseau, perte de batterie) :

```json
{
  "user_uuid": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "state": "offline",
  "gateway": "mobile"
}
```

_Effet côté backend_ : Passage de l'ensemble des équipements associés à l'utilisateur en statut `offline`.

### F. Topics d'Alerting de Chute : `healthkicks/v1/users/{user_uuid}/events/fall-alert` & `.../fall-alert/status`

Spécification détaillée dans [`contracts/fall_alerting.md`](fall_alerting.md) :
- **Uplink (`healthkicks/v1/users/{user_uuid}/events/fall-alert`)** : émis par le mobile lors d'une détection de chute (`DETECTED`), d'une confirmation immédiate d'aide (`CONFIRM`), d'une annulation manuelle / relevage (`CANCEL`) ou du rapport d'envoi SMS (`SMS_STATUS`).
- **Downlink (`healthkicks/v1/users/{user_uuid}/fall-alert/status`)** : publié par le backend à chaque changement d'état (`PENDING`, `ESCALATING`, `ACKNOWLEDGED`, `CANCELLED`, `EXHAUSTED`, `SUPPRESSED`) et porteur de l'ordre `sms_command` pour le relais GSM du mobile.

---

## 4. Spécifications Binaires Matérielles & Protocoles Dédiés

Pour les échanges directs par Bluetooth Low Energy (BLE GATT) et les workflows transverses, les protocoles canoniques sont documentés dans des spécifications dédiées :

- [`contracts/ble_gatt_specs.md`](ble_gatt_specs.md) : Table des UUIDs de services et caractéristiques, codes d'état d'activité, structures binaires packées.
- [`contracts/studio_burst_protocol.md`](studio_burst_protocol.md) : Protocole de transmission haute fréquence des signaux IMU (opcodes de contrôle, header 4 octets, trames IMU 12 octets big-endian int16).
- [`contracts/ota_ble_protocol.md`](ota_ble_protocol.md) : Protocole de mise à jour firmware sans fil (opcodes Start/Data/End, magic byte `0xE9`, digest SHA-256 obligatoire de 32 octets, codes d'erreurs et période de probation).
- [`contracts/fall_alerting.md`](fall_alerting.md) : Cycle de vie des alertes de chute, escalade séquentielle par email et SMS, jeton signé d'acquittement, contrats MQTT et REST.
