# Contrat d'Échange — Alerting en cas de Chute (Fall Alerting)

> **Statut** : `VALIDATED v1.1` — Spécification validée par l'utilisateur (Email SMTP + SMS piloté par le Backend via Relais GSM Mobile).
> **Projets impactés** :
> - `health-kicks` (Backend FastAPI, SQLAlchemy/Alembic, Worker d'escalade, SMTP, Ordres SMS MQTT Downlink, Suivi `SMS_STATUS`, Webhook IoT, Page d'acquittement HTML)
> - `health-kicks-mobile` (Mobile Flutter Android, Détection BLE -> Uplink MQTT, GPS, Écran d'alerte 60 s, Réception Downlink MQTT, Envoi SMS natif `SmsManager` + acquittement `SMS_STATUS`, Appel 112)
> - `health-kicks-frontend` (Angular 22, Page `/dashboard/fall-alerts` à deux onglets : *Historique des alertes* avec trace Email/SMS et *Mes proches d'urgence* avec téléphone optionnel)
> - `health-kicks-esp32-s3` : **Aucun changement** (s'appuie sur la caractéristique BLE `7a5a0002` définie dans [`ble_gatt_specs.md`](./ble_gatt_specs.md)).

---

## 1. Périmètre & Principes Directeurs

| Principe | Règle Normative |
| :--- | :--- |
| **Canaux d'alerte** | **Email** (SMTP STARTTLS émis par le backend) **+ SMS optionnel** (orchestré par le backend via MQTT Downlink et émis par le téléphone Android de l'utilisateur via `SmsManager`, avec évolution future possible vers une API SMS Cloud type OVH SMS). |
| **Pré-condition** | **Mode Surveillance Active** ([`docs/mobile_architecture.md`](../docs/mobile_architecture.md)) : l'application mobile Android maintient le Foreground Service connecté à la chaussure (BLE) **et** au broker AWS IoT Core (MQTT). Aucune alerte email/SMS n'est émise pour une chute remontée en différé (`SUPPRESSED`). |
| **Destinataires (Proches)** | Contacts d'urgence associés au compte utilisateur : `first_name`, `last_name`, `email` (obligatoire), `phone` (**optionnel**, format international/local normalisé), `priority` (`1..5`). **Gérés exclusivement depuis l'application web** (onglet *Mes proches d'urgence* sur `/dashboard/fall-alerts`). Maximum **5** proches par utilisateur. Aucun envoi automatique lors de l'ajout, mais un bouton **« Tester »** envoie un email de test et, si `phone` est renseigné, un ordre de SMS de test au mobile. |
| **Escalade séquentielle** | Un seul proche est notifié à la fois par ordre de `priority` croissant (`1`, puis `2`, etc.). Si le proche possède un numéro `phone`, le backend déclenche simultanément l'envoi de l'email **et** l'ordre d'envoi du SMS pour ce proche. Sans prise en charge sous **180 secondes (3 min)**, le proche suivant est notifié. Dès qu'un proche confirme la prise en charge (via le lien dans l'email ou dans le SMS), **l'escalade s'arrête et les proches suivants ne sont jamais notifiés**. |
| **Épuisement (`EXHAUSTED`)** | Si le dernier proche de la liste n'a pas confirmé après **180 secondes** (ou si l'utilisateur n'a configuré aucun proche à la fin des 60 s), l'alerte passe à l'état `EXHAUSTED` : **on arrête les relances** et le téléphone du patient affiche en plein écran **« Appeler le 112 »**. |
| **Fenêtre d'annulation (60 s)** | À la réception d'une chute, l'alerte démarre en `PENDING` pour **60 secondes** (minuterie pilotée par le backend) pendant que le téléphone affiche l'écran « Ça va ? ». Si le patient clique sur « Je vais bien » ou si la chaussure détecte un relevage (`fall_recovery`, code `0x13`), l'alerte passe en `CANCELLED` et **aucune notification n'est envoyée**. |
| **Relevage après envoi** | Si `fall_recovery` (ou annulation manuelle par le patient) survient pendant `ESCALATING`, l'alerte passe immédiatement en `CANCELLED`, **l'escalade s'arrête et aucune notification supplémentaire n'est envoyée**. |
| **Prise en charge (ACK)** | Via un **lien cliquable signé valable 2 heures (7 200 s)** présent dans l'email et dans le SMS : `f"{frontend_url}/fall-alerts/ack?token={token}"`. Le lien ouvre directement la page du frontend Angular (`/fall-alerts/ack?token=...`) qui charge les métadonnées de l'alerte via `GET /api/v1/fall-alerts/ack/info` (lecture seule sécurisée), puis un bouton explicite confirme la prise en charge via `POST /api/v1/fall-alerts/ack` (payload JSON `{"token": "..."}`) afin d'éviter tout faux acquittement par les robots d'aperçu de liens SMS ou scanners d'emails. |
| **Concurrence d'alertes** | Un utilisateur ne peut avoir **qu'une seule alerte active** (`PENDING` ou `ESCALATING`) à la fois. Toute nouvelle chute `DETECTED` reçue alors qu'une alerte est déjà active pour cet utilisateur est rattachée/ignorée de manière idempotente sans déclencher une seconde chaîne parallèle. |
| **Visibilité Historique & RBAC** | L'historique des alertes est visible par **l'utilisateur concerné** (rôle `user` ou `clinician`, chacun ne voyant **que ses propres alertes**) et par le rôle **`admin`** (qui voit toutes les alertes avec pseudonymisation RGPD par défaut pour les comptes tiers, aligné sur Studio). |

---

## 2. Machine à États (`FallAlertState`)

```mermaid
stateDiagram-v2
    [*] --> PENDING : MQTT action=DETECTED (delivery=live)
    [*] --> SUPPRESSED : MQTT action=DETECTED (delivery=replayed ou retard > 120s)
    PENDING --> CANCELLED : MQTT action=CANCEL (user_cancel | fall_recovery)
    PENDING --> ESCALATING : 60 s écoulées OU MQTT action=CONFIRM (≥ 1 proche configuré)
    PENDING --> EXHAUSTED : 60 s écoulées OU MQTT action=CONFIRM (0 proche configuré)
    ESCALATING --> ESCALATING : 180 s sans ACK (ou échec d'envoi) → proche suivant
    ESCALATING --> CANCELLED : MQTT action=CANCEL (user_cancel | fall_recovery)
    ESCALATING --> ACKNOWLEDGED : POST /api/v1/fall-alerts/ack (jeton valide ≤ 2h)
    ESCALATING --> EXHAUSTED : dernier proche + 180 s sans ACK (ou tous envois en échec)
    EXHAUSTED --> ACKNOWLEDGED : POST /api/v1/fall-alerts/ack tardif (jeton encore valide ≤ 2h)
    CANCELLED --> [*]
    ACKNOWLEDGED --> [*]
    SUPPRESSED --> [*]
```

| État (`FallAlertState`) | Terminal | Description |
| :--- | :---: | :--- |
| `PENDING` | ❌ | Chute reçue en direct ; fenêtre d'annulation de 60 s en cours (`next_action_at = detected_at + 60s`). Aucune notification envoyée. |
| `ESCALATING` | ❌ | Envoi séquentiel en cours ; `current_contact_rank` (`1..N`) indique le proche actuellement sollicité (`next_action_at = now + 180s`). |
| `ACKNOWLEDGED` | ✅ | Un proche a confirmé la prise en charge via le lien signé (Email ou SMS). Escalade stoppée. |
| `CANCELLED` | ✅ | Annulée par le patient (`user_cancel`) ou par détection de relevage (`fall_recovery`). Aucune notification envoyée après cet état. |
| `EXHAUSTED` | ⚠️ semi | Tous les proches ont été sollicités sans confirmation dans le délai imparti (ou aucun proche configuré). Le mobile affiche « Appeler le 112 ». Seule transition encore autorisée : `ACKNOWLEDGED` si un proche clique sur son lien avant l'expiration des 2 h. |
| `SUPPRESSED` | ✅ | Chute remontée hors surveillance active (`delivery="replayed"`, bit 2 `flags` NVS BLE, ou retard > 120 s). Enregistrée pour traçabilité sans aucune notification. |

---

## 3. Contrats MQTT IoT (Mobile ↔ AWS IoT Core ↔ Backend)

Les topics utilisent l'espace de noms utilisateur `healthkicks/v1/users/{user_id}/...` déjà autorisé en `iot:Publish`, `iot:Subscribe` et `iot:Receive` par la politique STS dynamique (`AWSSTSService.build_session_policy`).

### A. Topic Uplink (Mobile → Cloud) : `healthkicks/v1/users/{user_id}/events/fall-alert`

Publié par l'application mobile en **QoS 1**.

#### 1. Payload `action = "DETECTED"` (émis dès la réception BLE `0x10`, `0x11`, `0x12`, `0x1F`)

```json
{
  "event_id": "0b6f4b1e-6a51-4c1f-9a3e-2d7f1c9b8e10",
  "action": "DETECTED",
  "device_id": "HK-1",
  "event_type": "fall_forward",
  "confidence": 0.91,
  "detected_at": 1792745943123,
  "delivery": "live",
  "location": {
    "lat": 50.8466,
    "lon": 4.3528,
    "accuracy_m": 12.5,
    "captured_at": 1792745941000
  },
  "sent_at": 1792745943410
}
```

#### 2. Payload `action = "CONFIRM"` (si le patient appuie sur « J'ai besoin d'aide maintenant » avant la fin des 60 s)

```json
{
  "event_id": "0b6f4b1e-6a51-4c1f-9a3e-2d7f1c9b8e10",
  "action": "CONFIRM",
  "location": {
    "lat": 50.8466,
    "lon": 4.3528,
    "accuracy_m": 8.0,
    "captured_at": 1792745955000
  },
  "sent_at": 1792745955100
}
```

#### 3. Payload `action = "CANCEL"` (appui sur « Je vais bien » ou réception BLE `0x13` `fall_recovery`)

```json
{
  "event_id": "0b6f4b1e-6a51-4c1f-9a3e-2d7f1c9b8e10",
  "action": "CANCEL",
  "cancel_reason": "fall_recovery",
  "sent_at": 1792745951000
}
```

#### 4. Payload `action = "SMS_STATUS"` (retour d'exécution du relais SMS Android vers le Backend via MQTT ou REST `POST /api/v1/fall-alerts/sms-status`)

```json
{
  "event_id": "0b6f4b1e-6a51-4c1f-9a3e-2d7f1c9b8e10",
  "action": "SMS_STATUS",
  "notification_id": 102,
  "sms_status": "SENT",
  "error_message": null,
  "sent_at": 1792746005000
}
```

#### Contraintes de validation des champs Uplink

| Champ | Type | Requis | Contraintes & Sémantique |
| :--- | :--- | :---: | :--- |
| `event_id` | `string` | ✅ | UUID v4 généré par le mobile lors de la chute. **Clé d'idempotence** partagée entre `DETECTED`, `CONFIRM`, `CANCEL` et `SMS_STATUS`. |
| `action` | `enum` | ✅ | `"DETECTED"` \| `"CONFIRM"` \| `"CANCEL"` \| `"SMS_STATUS"` |
| `device_id` | `string` | si `DETECTED` | Identifiant de la chaussure (`1..128` car.). |
| `event_type` | `enum` | si `DETECTED` | `"fall_forward"` \| `"fall_backward"` \| `"fall_lateral"` \| `"fall_generic"` |
| `confidence` | `float` | si `DETECTED` | Score ML compris entre `0.0` et `1.0`. |
| `detected_at` | `int` | si `DETECTED` | Epoch UTC en millisecondes (`ms`) au moment de la chute. |
| `delivery` | `enum` | si `DETECTED` | `"live"` si transmis immédiatement en mode Surveillance Active ; `"replayed"` si issu du cache NVS hors-ligne de la chaussure (`flags` bit 2 = 1) ou d'une file hors-ligne. |
| `location` | `object \| null` | ❌ | Position GPS (`lat`: `[-90, 90]`, `lon`: `[-180, 180]`, `accuracy_m`: `≥ 0`, `captured_at`: epoch ms UTC). |
| `cancel_reason` | `enum` | si `CANCEL` | `"user_cancel"` (bouton « Je vais bien ») \| `"fall_recovery"` (relevage `0x13` détecté par la chaussure). |
| `notification_id` | `int` | si `SMS_STATUS` | Identifiant de la ligne `fall_alert_notifications` (`channel="sms"`) créée par le backend. |
| `sms_status` | `enum` | si `SMS_STATUS` | `"SENT"` (SMS remis au modem GSM Android) \| `"FAILED"` (permission refusée ou erreur modem). |
| `error_message` | `string \| null` | ❌ | Détail de l'erreur en cas de `sms_status == "FAILED"` (max 512 car.). |
| `sent_at` | `int` | ✅ | Epoch UTC en millisecondes (`ms`) d'envoi du message MQTT. |

### B. Topic Downlink (Cloud → Mobile) : `healthkicks/v1/users/{user_id}/fall-alert/status`

Publié par le backend via `AWSIoTPublishService` (`iot-data:Publish`, **QoS 1**) à chaque création, changement d'état d'une alerte, ou demande de SMS de test (`state = "TEST_SMS"`).

```json
{
  "event_id": "0b6f4b1e-6a51-4c1f-9a3e-2d7f1c9b8e10",
  "alert_id": 42,
  "state": "ESCALATING",
  "current_contact_rank": 1,
  "contacts_total": 3,
  "acknowledged_by": null,
  "cancel_reason": null,
  "next_action_at": "2026-10-23T08:43:03Z",
  "updated_at": "2026-10-23T08:40:03Z",
  "sms_command": {
    "notification_id": 102,
    "contact_id": 7,
    "contact_first_name": "Marie",
    "recipient_phone": "+32470123456",
    "message": "[HealthKicks URGENCE] Chute détectée pour Jean Martin (10:39). Position : https://maps.google.com/?q=50.8466,4.3528 Confirmez la prise en charge : https://healthkicks.duckdns.org:8443/api/v1/fall-alerts/ack?token=...",
    "is_test": false
  }
}
```

| État reçu (`state`) | Action de l'application mobile (Android) |
| :--- | :--- |
| `PENDING` | Affiche l'écran d'alerte plein écran (« Chute détectée — Ça va ? ») avec compte à rebours synchronisé sur `next_action_at`, bouton **« Je vais bien (Annuler) »** et bouton **« J'ai besoin d'aide »**. |
| `ESCALATING` | Affiche « Alerte envoyée au proche n°`current_contact_rank` sur `contacts_total` — En attente de réponse… » + bouton « Je vais bien (Annuler l'alerte) ». Si `sms_command` est présent (et non encore traité pour ce `notification_id`), envoie immédiatement le SMS via `SmsManager` et publie `action: "SMS_STATUS"` (`SENT` ou `FAILED`) sur le topic uplink. |
| `ACKNOWLEDGED` | Affiche « Rassurez-vous : **`acknowledged_by.first_name`** a pris en charge votre alerte » avec un bouton pour fermer l'écran. |
| `EXHAUSTED` | Affiche en plein écran haute visibilité **« Aucun proche n'a pu confirmer — Appeler le 112 »** (bouton déclenchant le composeur téléphonique `tel:112`). |
| `CANCELLED` / `SUPPRESSED` | Ferme l'écran d'alerte actif s'il est affiché. |
| `TEST_SMS` | **N'ouvre pas l'écran d'alerte de chute.** Envoie immédiatement le SMS de test décrit dans `sms_command` via `SmsManager`. |

### C. Règle AWS IoT Core & Fonction Lambda Relais

- **IoT Rule Name** : `healthkicks_fall_alert_rule`
- **Rule SQL** :
  ```sql
  SELECT *, topic(4) AS user_id FROM 'healthkicks/v1/users/+/events/fall-alert'
  ```
- **Target** : Fonction AWS Lambda `healthkicks-fall-alert-relay` qui effectue un `POST {BACKEND_URL}/api/v1/internal/fall-alerts` avec l'en-tête `X-Ingest-Token` (transmet aussi bien `DETECTED`, `CONFIRM`, `CANCEL` que `SMS_STATUS`).

---

## 4. Contrats REST API (Backend FastAPI)

### A. Endpoint Interne d'Ingestion (Lambda → Backend)

#### `POST /api/v1/internal/fall-alerts`
- **Authentification** : Header `X-Ingest-Token` (`Depends(verify_ingest_token)`).
- **Règles métier supplémentaires pour `action == "SMS_STATUS"`** :
  - Recherche `FallAlertNotification` par `id == payload.notification_id` en vérifiant que l'alerte parente appartient à `user_id`.
  - Si introuvable → `404 Not Found`.
  - Si `notification.status != "ACKNOWLEDGED"` : met à jour `notification.status = payload.sms_status` (`"SENT"` ou `"FAILED"`) et `notification.error_message = payload.error_message`.
  - Retourne `200 OK` (`FallAlertIngestResponse` avec l'état courant de l'alerte).

---

### B. Gestion des Proches / Contacts d'Urgence (Frontend Web ↔ Backend)

| Méthode & Route | Code Succès | Description & Codes d'Erreur |
| :--- | :---: | :--- |
| `GET /api/v1/users/me/alert-contacts` | `200 OK` | Retourne `list[AlertContactResponse]` triée par `priority` croissant (`1..N`). |
| `POST /api/v1/users/me/alert-contacts` | `201 Created` | Ajoute un proche en dernière position (`priority = count + 1`). `email` obligatoire, `phone` optionnel. `409 Conflict` si le plafond de **5 proches** est atteint ou si l'`email` existe déjà pour cet utilisateur. |
| `PUT /api/v1/users/me/alert-contacts/order` | `200 OK` | Réordonne les priorités (`{"contact_ids": [int, ...]}`). |
| `PATCH /api/v1/users/me/alert-contacts/{contact_id}` | `200 OK` | Modifie `first_name`, `last_name`, `email` et/ou `phone` (passer `phone: null` ou `""` efface le numéro). |
| `DELETE /api/v1/users/me/alert-contacts/{contact_id}` | `204 No Content` | Supprime le proche et re-compacte les `priority` restantes (`1..N`). |
| `POST /api/v1/users/me/alert-contacts/{contact_id}/test-email` | `202 Accepted` | Envoie un email de vérification au proche **et**, si `contact.phone` est renseigné, publie un ordre `state="TEST_SMS"` sur le topic MQTT du mobile. Met à jour `last_test_email_at`. Rate-limit : **3 envois / heure / utilisateur** (`429`). |

#### Schémas JSON (`app/schemas/fall_alert.py`)

```json
// AlertContactCreate
{
  "first_name": "Marie",
  "last_name": "Dupont",
  "email": "marie.dupont@example.com",
  "phone": "+32470123456"
}

// AlertContactUpdate (tous les champs sont optionnels, au moins un requis)
{
  "first_name": "Marie",
  "last_name": "Dupont-Martin",
  "email": "marie.dupont@example.com",
  "phone": "+32470123456"
}

// AlertContactResponse
{
  "id": 7,
  "first_name": "Marie",
  "last_name": "Dupont",
  "email": "marie.dupont@example.com",
  "phone": "+32470123456",
  "priority": 1,
  "last_test_email_at": "2026-10-23T08:10:00Z",
  "created_at": "2026-10-23T08:00:00Z",
  "updated_at": "2026-10-23T08:10:00Z"
}

// AlertContactTestEmailResponse
{
  "status": "sent",
  "contact_id": 7,
  "sent_at": "2026-10-23T08:10:00Z",
  "sms_dispatched": true
}
```

_Contraintes de validation_ :
- `first_name`, `last_name` : chaîne nettoyée (`strip()`), longueur `1..100` caractères.
- `email` : format email valide, converti en minuscules, longueur `3..320` caractères (obligatoire).
- `phone` : optionnel (`null` ou chaîne vide convertie en `null`). Après suppression des espaces, tirets, points et parenthèses, doit respecter `^\+?[0-9]{6,20}$` (longueur max 32 caractères).

---

### C. Historique des Alertes de Chute (Frontend Web ↔ Backend)

Dans `FallAlertDetail.notifications[]`, chaque entrée expose désormais le canal (`channel: "email" | "sms"`) et le numéro de téléphone éventuel (`contact_phone: string | null`) :

```json
{
  "id": 102,
  "rank": 1,
  "channel": "sms",
  "contact_first_name": "Marie",
  "contact_last_name": "Dupont",
  "contact_email": "marie.dupont@example.com",
  "contact_phone": "+32470123456",
  "status": "SENT",
  "sent_at": "2026-10-23T08:40:04Z",
  "acknowledged_at": null,
  "error_message": null
}
```

- `notifications[].channel` ∈ `"email"` | `"sms"`
- `notifications[].status` ∈ `"SENT"` | `"PENDING_SMS"` | `"ACKNOWLEDGED"` | `"FAILED"`
- **Pseudonymisation RGPD (`admin` sur compte tiers)** : `contact_phone` est masqué (ex. `+32*******56`).

---

## 5. Modèle de Données Relationnel (PostgreSQL / Alembic)

Migration Alembic additionnelle (`20261023_0005_add_sms_support_to_fall_alerting.py`) :
1. **`alert_contacts`** :
   - Ajout de la colonne `phone` (`String(32)`, nullable).
2. **`fall_alert_notifications`** :
   - Ajout de la colonne `channel` (`String(16)`, non null, server_default `"email"`).
   - Ajout de la colonne `contact_phone` (`String(32)`, nullable).

---

## 6. Worker d'Escalade (`AlertService`)

Lors de la notification du contact de rang `k` :
1. **Canal Email** : envoi via `SmtpEmailChannel` et création d'une ligne `FallAlertNotification(channel="email", status="SENT" | "FAILED")`.
2. **Canal SMS (si `contact.phone` est non nul)** :
   - Création d'une ligne `FallAlertNotification(channel="sms", contact_phone=contact.phone, status="PENDING_SMS")`.
   - Génération d'un jeton signé dédié `(alert.id, sms_notification.id)` et construction du message SMS concis contenant le nom du patient, le lien Google Maps (si disponible) et le lien d'acquittement.
   - Inclusion de `sms_command` dans le payload MQTT Downlink publié sur `healthkicks/v1/users/{user_id}/fall-alert/status`.
   - Si la publication MQTT échoue côté backend, la notification SMS passe immédiatement à `status="FAILED"`.
3. **Progression de l'escalade** :
   - Si au moins un canal a réussi (`email` envoyé **ou** `sms_command` publié sur MQTT), le palier de 180 s démarre (`current_contact_rank = k`, `next_action_at_utc = now + 180s`).
   - Si tous les canaux du contact ont échoué immédiatement, le worker passe sans attendre au contact `k + 1`.
