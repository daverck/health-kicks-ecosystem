# Architecture Mobile & Passerelle d'Arrière-Plan (HealthKicks Mobile)

Ce document décrit l'architecture de l'application **HealthKicks Mobile** (Flutter / Android), le fonctionnement du service de premier plan persistant (_Foreground Service_), ainsi que la gestion du cycle de vie des connexions BLE et MQTT en arrière-plan.

---

## 1. Vue d'Ensemble de la Passerelle Mobile

L'application mobile fait office de passerelle active entre :

1. **La Chaussure Connectée (ESP32-S3)** via **Bluetooth Low Energy (BLE GATT)**.
2. **Le Cloud AWS IoT Core** via **MQTT sur WebSockets SigV4**.

```text
[ Chaussure Connectée ESP32-S3 ]
         │ (BLE GATT - Services 0001-0005)
         ▼
[ HealthKicks Mobile (Flutter) ] ──(Foreground Service Android)──
         │ (MQTT SigV4 WebSockets / REST HTTPS)
         ▼
[ AWS IoT Core & FastAPI Backend ]
```

---

## 2. Mode Surveillance Active (Foreground Service Android)

### A. Rôle et Comportement

Le **Mode Surveillance Active** permet à l'application de maintenir actives la connexion Bluetooth Low Energy avec la chaussure et la session MQTT avec AWS IoT Core même lorsque :

- L'écran du smartphone est éteint ou verrouillé.
- L'utilisateur bascule sur une autre application.

> [!IMPORTANT]
> **Compatibilité Plateforme :**
> _Le maintien de la passerelle BLE/MQTT avec écran éteint est actuellement réservé à Android. iOS n'est pas supporté pour ce mode en raison des restrictions d'arrière-plan de l'OS (interdiction des sockets TCP/MQTT arbitraires permanents sans profil VoIP/Audio)._

### B. Spécifications Techniques sous Android 14+

Conformément aux exigences strictes de Google Play et d'Android 14 (API 34+), le service d'arrière-plan est configuré avec deux types de service déclarés dans `AndroidManifest.xml` :

```xml
<!-- Permissions requises -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />

<!-- Déclaration avec types obligatoires -->
<service
    android:name="com.pravera.flutter_foreground_task.service.ForegroundService"
    android:foregroundServiceType="connectedDevice|dataSync"
    android:exported="false" />
```

- **`connectedDevice` :** Justifie le maintien de la connexion continue avec un périphérique physique externe (chaussure connectée via BLE).
- **`dataSync` :** Justifie la synchronisation en temps réel des flux de télémétrie biomécanique vers AWS IoT Core.

---

## 3. Notification Permanente & Actions Rapides

Tant que le mode surveillance est activé :

1. **Canal de Notification :** `healthkicks_surveillance_channel` (Importance: `LOW` pour éviter les bips intempestifs).
2. **Titre :** `HealthKicks - Mode Surveillance Active`
3. **Texte Dynamique :**
   - _"Connecté à la chaussure (HK-2)"_
   - _"Recherche du device HK-2... (Arrêt auto dans 5 min)"_
4. **Bouton d'Action Rapide :**
   - **[Arrêter]** : Permet à l'utilisateur de couper immédiatement la passerelle et la notification sans ouvrir l'application.

---

## 4. Gestion Intelligente de la Batterie & Timeout d'Inactivité (5 Minutes)

Pour éviter de décharger la batterie du smartphone si l'utilisateur s'éloigne ou éteint sa chaussure :

1. Dès que le signal BLE est perdu (statut `disconnected` ou `scanning`), un compte à rebours de **5 minutes** (`AppConfig.bleDisconnectTimeout`) démarre.
2. Si la reconnexion réussit avant l'échéance : le timer est immédiatement annulé et le service reste actif.
3. Si le timer de 5 minutes expire sans reconnexion :
   - Le Foreground Service s'arrête automatiquement.
   - Le toggle _Mode Surveillance Active_ repasse à `false` dans les réglages.
   - La session MQTT est clôturée proprement.

---

## 5. Interface Utilisateur & Activation

Le composant est accessible depuis l'écran des **Paramètres** (`SettingsScreen`) :

- **Intitulé :** _"Mode Surveillance Active"_
- **Sous-titre :** _"Maintient la connexion active écran éteint pour l'enregistrement et la télémétrie"_
- Lors de la première activation sous Android 13+, l'application sollicite les permissions de notification (`POST_NOTIFICATIONS`) et invite l'utilisateur à autoriser l'exemption d'optimisation de batterie.
