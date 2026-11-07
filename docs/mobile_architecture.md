# Mobile Architecture & Background Gateway (HealthKicks Mobile)

This document describes the architecture of the **HealthKicks Mobile** application (Flutter / Android), the operation of its persistent **Foreground Service**, and background connection lifecycle management across BLE and MQTT.

---

## 1. Mobile Gateway Overview

The mobile application acts as an active gateway between:

1. **The Connected Shoe (ESP32-S3)** via **Bluetooth Low Energy (BLE GATT)**.
2. **AWS IoT Core Cloud** via **MQTT over SigV4 WebSockets**.

```text
[ Connected Shoe ESP32-S3 ]
         │ (BLE GATT - Services 0001-0005)
         ▼
[ HealthKicks Mobile (Flutter) ] ──(Android Foreground Service)──
         │ (MQTT SigV4 WebSockets / REST HTTPS)
         ▼
[ AWS IoT Core & FastAPI Backend ]
```

---

## 2. Active Surveillance Mode (Android Foreground Service)

### A. Role & Behavior

**Active Surveillance Mode** enables the application to maintain active Bluetooth Low Energy communication with the shoe and an MQTT session with AWS IoT Core even when:

- The smartphone screen is turned off or locked.
- The user switches to another application.

> [!IMPORTANT]
> **Platform Compatibility:**
> _Maintaining the BLE/MQTT gateway with the screen turned off is currently supported on Android. iOS is not supported for this mode due to operating system background restrictions (disallowance of arbitrary permanent TCP/MQTT sockets without VoIP/Audio profiles)._

### B. Technical Specifications on Android 14+

In accordance with strict Google Play and Android 14 (API 34+) requirements, the background service is declared with two distinct service types in `AndroidManifest.xml`:

```xml
<!-- Required permissions -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />

<!-- Declaration with mandatory types -->
<service
    android:name="com.pravera.flutter_foreground_task.service.ForegroundService"
    android:foregroundServiceType="connectedDevice|dataSync"
    android:exported="false" />
```

- **`connectedDevice`**: Justifies continuous connectivity with an external physical peripheral (connected shoe over BLE).
- **`dataSync`**: Justifies real-time streaming synchronization of biomechanical telemetry to AWS IoT Core.

---

## 3. Persistent Notification & Quick Actions

While surveillance mode is active:

1. **Notification Channel**: `healthkicks_surveillance_channel` (Importance: `LOW` to avoid spurious chimes).
2. **Title**: `HealthKicks - Active Surveillance Mode`
3. **Dynamic Text**:
   - _"Connected to shoe (HK-2)"_
   - _"Searching for device HK-2... (Auto-stop in 5 min)"_
4. **Quick Action Button**:
   - **[Stop]**: Allows the user to stop the gateway and dismiss the notification immediately without launching the app.

---

## 4. Intelligent Battery Management & Inactivity Timeout (5 Minutes)

To avoid draining smartphone battery if the user walks away or turns off the shoe:

1. As soon as the BLE signal is lost (status `disconnected` or `scanning`), a **5-minute countdown** (`AppConfig.bleDisconnectTimeout`) begins.
2. If reconnection succeeds before timeout: the timer is immediately cancelled and service remains active.
3. If the 5-minute timer expires without reconnection:
   - The Foreground Service stops automatically.
   - The _Active Surveillance Mode_ toggle switches to `false` in settings.
   - The MQTT session disconnects gracefully.

---

## 5. User Interface & Activation

The feature is accessible from the **Settings** screen (`SettingsScreen`):

- **Label**: _"Active Surveillance Mode"_
- **Subtitle**: _"Maintains connection with screen turned off for recording and telemetry"_
- Upon first activation on Android 13+, the app requests notification permissions (`POST_NOTIFICATIONS`) and guides the user to grant battery optimization exemption.
