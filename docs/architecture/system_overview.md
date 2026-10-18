# Vue d'Ensemble du Système HealthKicks

L'écosystème **HealthKicks** est une solution connectée temps réel de prévention des chutes, d'analyse biomécanique de la marche et de stimulation haptique plantaire. Il intègre de l'intelligence embarquée à la source (_Edge AI_ sur microcontrôleur ESP32-S3 ou Raspberry Pi), une passerelle mobile Flutter/Dart, une API Cloud FastAPI élastique, et une interface clinique réactive sous Angular 21.

---

## 1. Cartographie Globale des Composants

```mermaid
flowchart TD
    subgraph Footwear["1. Chaussure Instrumentée (health-kicks-esp32-s3)"]
        ESP32["ESP32-S3 (240MHz, FreeRTOS)\n• IMU 6-axes MPU-6050 (19 Hz / 100 Hz)\n• Inférence C++ transpiled (m2cgen)\n• Compteur de pas (podomètre matériel)\n• Alerte d'inactivité & calibration 0g\n• Actuateur vibrotactile PWM (10 kHz)\n• Serveur NimBLE GATT (LESC Encrypted)\n• Moteur OTA avec SHA-256 & Rollback"]
    end

    subgraph Mobile["2. Passerelle Mobile (health-kicks-mobile)"]
        FlutterApp["Application Flutter / Dart\n• Client BLE GATT chiffré & Bouton d'appairage\n• Passerelle MQTT AWS IoT Core (WebSockets SigV4)\n• Négociation STS éphémère (Scoped Policy)\n• Authentification OAuth2 PKCE (S256 + Ticket)\n• Odomètre différentiel net (SQLite)\n• Mise à jour OTA avec vérification SHA-256 & SemVer"]
    end

    subgraph Cloud["3. Backend & Données Cloud (health-kicks)"]
        IoTCore["AWS IoT Core (Broker MQTT v1)"]
        FastAPI["API REST FastAPI / Uvicorn\n• Courtier de jetons AWS STS\n• Échange de tickets OAuth2 PKCE\n• Historique activités & podométrie\n• Gestionnaire de sessions Studio\n• S3 Firmware Release Manager\n• Probes /health & métriques opérationnelles"]
        Postgres[("Aurora PostgreSQL 16\nVérité Relationnelle & Audit")]
        DynamoDB[("DynamoDB\nTélémétrie brute haute fréquence")]
    end

    subgraph Client["4. Restitution Clinique (health-kicks-frontend)"]
        AngularUI["Tableau de Bord Web (Angular 22)\n• Angular Signals & Standalone Components\n• Visualisation temps réel & alertes chutes\n• Requalification et validation Studio (is_validated)\n• Déclencheur haptique & calibration à distance\n• Calendrier d'activité & rapports cliniques"]
    end

    ESP32 <-->|BLE GATT LESC Chiffré| FlutterApp
    FlutterApp <-->|MQTT WebSockets SigV4| IoTCore
    FlutterApp <-->|REST HTTPS / JWT| FastAPI
    IoTCore -->|Rule Engine / Ingestion| FastAPI
    IoTCore -->|Rule Engine| DynamoDB
    FastAPI <-->|SQLAlchemy 2.0 / Alembic| Postgres
    FastAPI <-->|Boto3 SDK| DynamoDB
    AngularUI <-->|REST HTTPS / JWT| FastAPI
    AngularUI -.->|WebSockets Directs| FastAPI
```

---

## 2. Rôles et Responsabilités des Sous-Projets

### A. Firmware Embarqué (`health-kicks-esp32-s3/`)

- **Technologies** : ESP32-S3-DevKitC-1 (Xtensa dual-core 240 MHz), Framework Arduino-ESP32 / PlatformIO, FreeRTOS, NimBLE-Arduino 1.4.3, MPU-6050 I2C (400 kHz).
- **Responsabilités** :
  - **Acquisition biomécanique** : Échantillonnage à 19 Hz (~94 échantillons sur fenêtre glissante de 5 s) aligné sur le référentiel ISB.
  - **Classifieur Edge AI sur puce** : Inférence locale C++ pure (sans runtime externe, générée via `m2cgen`), détection de chute multiclasse (`fall_forward`, `fall_backward`, `fall_lateral`) et garde biomécanique anti-fausses alertes assises (`isSittingDownNominalPosture`).
  - **Serveur BLE GATT sécurisé** :
    - Service Podomètre (0005) : Odomètre matériel monotone (marche, course, escaliers, non-classifié).
    - Service Haptique (0003) : Patterns vibratoires (0–255, 50–10000 ms), configuration du rappel d'inactivité (Opcode 0x06), calibration zéro (Opcode 0x05).
    - Service Studio (0004 & 0005) : Burst de données télémétriques brutes calibrées.
    - Service Device Information (0x180A) : Version firmware (0x2A26) et date de compilation UTC (0x2A28).
    - Service OTA (0010, 0011, 0012) : Flashage différentiel over-the-air.
  - **Sécurité & Résilience** :
    - Chiffrement de liaison LESC (_LE Secure Connections_) Just Works + Bonding.
    - Fenêtre d'appairage physique de 60 secondes déclenchée par appui sur bouton matériel (`GPIO 14`).
    - Vérification d'intégrité OTA : En-tête magique ESP32 `0xE9`, empreinte cryptographique SHA-256 obligatoire de 32 octets.
    - Fenêtre de probation de 15 secondes au redémarrage avec rollback automatique en cas de défaillance capteur.

### B. Application Mobile (`health-kicks-mobile/`)

- **Technologies** : Flutter 3.x, Dart 3.x, Flutter Blue Plus, MQTT Client, SQLite (sqflite), SharedPreferences.
- **Responsabilités** :
  - **Passerelle de terrain BLE $\leftrightarrow$ Cloud** : Maintien de la connexion Bluetooth avec la chaussure, auto-reconnexion post-reboot OTA.
  - **Courtage d'identité & AWS STS** : Négociation de jetons AWS temporaires (15 minutes) avec politique de session restreinte par `clean_user_id`.
  - **Passerelle MQTT SigV4** : Connexion temps réel sur `healthkicks/v1/{device_id}/*` via WebSockets signés AWS SigV4.
  - **Odométrie différentielle SQLite** : Calcul du delta de pas journalier net à partir de l'odomètre matériel monotone pour éviter les fuites de pas entre jours calendaires ou lors de redémarrages.
  - **Mise à jour OTA sécurisée** : Téléchargement depuis S3/Cloud, contrôle cryptographique SHA-256, comparaison par Semantic Versioning et tolérance aux décalages horaires UTC.

### C. Backend Cloud (`health-kicks/`)

- **Technologies** : Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL 16 (Aurora), DynamoDB, AWS IoT Core, Alembic, Docker.
- **Responsabilités** :
  - **Gestion des identités & SSO** : Authentification OAuth2 Google et Azure Entra ID avec support strict de **PKCE RFC 7636 (S256)** et échange de jeton par ticket éphémère à usage unique (`POST /api/v1/auth/token/exchange`).
  - **Contrôle d'accès & Isolation RBAC** : Rôles `user`, `clinician`, `admin`. Vérification d'appartenance des dispositifs (`verify_device_ownership`).
  - **Courtage STS AWS IoT** : Génération de session policies strictement restreintes aux identifiants clients de l'utilisateur authentifié (`client/healthkicks-mobile-{userId}-*`).
  - **Observabilité & Santé** : Endpoints `/health` (avec mesure de latence SQL et diagnostic du pool de connexions), `/health/liveness`, `/health/readiness` et `/metrics`.
  - **Pipeline ML & Transpilation** : Scripts `train_detector.py` et `update_edge_model.py` pour réentraîner les modèles d'activité et générer le code C pour l'ESP32.

### D. Frontend Web (`health-kicks-frontend/`)

- **Technologies** : Angular 22 (Standalone Components, Signals), Tailwind CSS 4, Angular Material, Chart.js, pnpm.
- **Responsabilités** :
  - **Supervision clinique** : Suivi des patients, détection des chutes en direct, analyse des cadences de marche.
  - **Module Studio & Annotation** : Enregistrement de sessions calibrées avec compte à rebours visuel/sensoriel, visualisation des signaux 3-axes ($a_x, a_y, a_z, g_x, g_y, g_z$), requalification et validation des labels cliniques (`is_validated`).
  - **Contrôle matériel distant** : Déclenchement de stimulations haptiques et configuration des seuils d'inactivité.

---

## 3. Matrice de Sécurité & Protocoles

| Couche                              | Protocole             | Chiffrement / Intégrité                | Mécanisme de Protection                                                                                        |
| :---------------------------------- | :-------------------- | :------------------------------------- | :------------------------------------------------------------------------------------------------------------- |
| **Footwear BLE**                    | BLE 5.0 GATT          | LESC (_Just Works_ + Bonding)          | Fenêtre d'appairage physique 60s (`GPIO 14`) + Rejet des écritures non chiffrées                               |
| **Firmware OTA**                    | BLE OTA Service       | SHA-256 + Magic Header `0xE9`          | Validation de l'octet magique à l'offset 0, contrôle SHA-256 obligatoire, rollback automatique si IMU en échec |
| **Mobile $\rightarrow$ Cloud REST** | HTTPS (TLS 1.3)       | JWT Bearer (HS256 $\ge 256$ bits)      | OAuth2 PKCE S256 + Ticket éphémère (aucun token en URL GET)                                                    |
| **Mobile $\rightarrow$ AWS IoT**    | MQTT over WebSockets  | AWS SigV4 (HMAC-SHA256)                | AWS STS temporaire (15 min), Client ID scopé strictly par utilisateur                                          |
| **Web $\rightarrow$ Cloud REST**    | HTTPS (TLS 1.3)       | JWT Bearer + Strict-Transport-Security | CSP, HSTS, X-Frame-Options DENY, Rate Limiting par IP/Token                                                    |
| **Données Sensibles**               | PostgreSQL & DynamoDB | Chiffrement au repos (AES-256 KMS)     | Pseudonymisation déterministe via HMAC-SHA256 (`HEALTHKICKS_PSEUDONYMIZATION_PEPPER`)                          |

---

## 4. Référentiel Biomécanique ISB

L'ensemble des composants respecte la norme de l'**International Society of Biomechanics** (_Wu & Cavanagh, 1995_) :

- **Axe X (Antéro-postérieur)** : Positif vers l'avant (propulsion de la foulée).
- **Axe Y (Médio-latéral)** : Positif vers la gauche de la chaussure.
- **Axe Z (Longitudinal / Vertical)** : Positif vers le haut ($+1.0\,g$ statique au repos sur sol plat).
- Plus d'informations : [`docs/architecture/biomechanical_reference_frame.md`](file:///f:/Programmation/healthkicks-ecosystem/docs/architecture/biomechanical_reference_frame.md).

---

## 5. Cycle de Mise à Jour OTA & Reconnexion Automatique

La mise à jour logicielle de la chaussure connectée s'exécute exclusivement over-the-air (BLE OTA), le port USB physique étant réservé à l'alimentation ou sujet aux contraintes d'étanchéité mécanique.

### 5.1 Protocole de Transfert & Validation d'Intégrité

1. **Transfert par Chunks** : L'application mobile découpe le binaire du firmware en blocs de 240 octets (adaptés au MTU négocié) et les transmet séquentiellement sur la caractéristique `CHAR_OTA_DATA_UUID`.
2. **Contrôle Magic Byte** : À l'offset 0, l'ESP32 valide l'octet magique `0xE9` (signature de l'en-tête ESP-IDF). Tout paquet initial non conforme provoque l'avortement immédiat (`Update.abort()`) et le renvoi de l'erreur `OTA_ERR_VALIDATION_FAILED` (0x05).
3. **Contrôle Cryptographique SHA-256** : À la fin du transfert, la commande `OTA_CMD_END` transporte obligatoirement l'empreinte SHA-256 de 32 octets. L'ESP32 compare l'empreinte calculée au vol via mbedTLS avec l'empreinte transmise. Si elles divergent ou si le condensat est absent, la mise à jour est rejetée (`OTA_ERR_CHECKSUM_MISMATCH`, 0x07).
4. **Basculement de Partition & Reboot** : L'ESP32 valide l'image dans la partition inactive (`ota_0` ou `ota_1`), configure le bootloader pour basculer sur ce slot au prochain démarrage, et invoque `esp_restart()`.

### 5.2 Séquence de Reconnexion Automatique Post-Reboot

```mermaid
sequenceDiagram
    autonumber
    actor User as Utilisateur
    participant Mobile as App Mobile (Flutter)
    participant BLE as NimBLE Stack
    participant ESP32 as Firmware ESP32-S3
    participant IMU as Capteur IMU MPU-6050

    Mobile->>ESP32: OTA_CMD_END + SHA-256 (32 octets)
    ESP32->>ESP32: Vérification SHA-256 & esp_ota_set_boot_partition()
    ESP32-->>Mobile: Statut Succès (0x00) & Déconnexion BLE
    ESP32->>ESP32: esp_restart()
    Note over Mobile: Début temporisation sécurité (3s)
    ESP32->>ESP32: Boot sur nouveau slot (otaPendingVerification = true)
    ESP32->>BLE: openPairingWindow(60s) + Advertising BLE
    ESP32->>IMU: Test initialisation & calibration (15s probation)
    alt Défaillance IMU pendant la probation
        ESP32->>ESP32: esp_ota_mark_app_invalid_rollback_and_reboot()
    else IMU Opérationnel
        ESP32->>ESP32: esp_ota_mark_app_valid_cancel_rollback()
    end
    Mobile->>BLE: BleConnectionManager.startAutoConnect(targetDeviceId, timeout: 45s)
    BLE->>Mobile: BleConnectionStatus.ready (Liaison LESC chiffrée)
    Mobile->>BLE: readDeviceFirmwareInfo() (DIS 0x180A)
    BLE-->>Mobile: Firmware Version (0x2A26) & Build Date (0x2A28)
    Mobile->>Mobile: FirmwareService.saveLocalInstalledFirmware(...)
    Mobile->>User: Notification succès & mise à jour en direct (Settings & Dashboard)
```

### 5.3 Détails d'Implémentation Mobile & Firmware

- **Temporisation de Reboot (3 secondes)** : `FirmwareUpdateScreen._triggerAutoReconnectAfterReboot()` introduit un délai de garde de 3 s (`Future.delayed(const Duration(seconds: 3))`) afin de laisser à l'ESP32 le temps de redémarrer son SoC, de réinitialiser le sous-système radio Bluetooth et de recommencer à émettre ses trames d'annonce (_advertisements_).
- **Fenêtre de Sauvetage / Appairage (60 secondes)** : Au redémarrage post-OTA, le firmware détecte le drapeau `otaPendingVerification` et ouvre automatiquement une fenêtre d'appairage physique de 60 secondes (`bleServer.openPairingWindow(60000)`). Même en cas de régénération des clés de liaison SMP ou de purge du cache côté OS mobile, la reconnexion et le ré-appairage s'exécutent de façon transparente sans blocage.
- **Interrogation du DIS (Device Information Service)** : Dès la reconnexion confirmée (`BleConnectionStatus.ready`), l'application lit la caractéristique standard `0x2A26` (_Firmware Revision String_) et `0x2A28` (_Hardware / Build Date_).
- **Persistance & Propagation Réactive** : La nouvelle version lue est enregistrée dans le stockage local `SharedPreferences`. Elle se propage instantanément à la modale de suivi OTA, à la tuile "INFORMATIONS SYSTÈME" de l'écran des Paramètres (`SettingsScreen`) et au widget d'état du matériel du Tableau de Bord (`_GatewayDashboardScreenState`).
