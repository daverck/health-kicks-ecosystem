# Spécification d'Agent : Mobile & Gateway Developer (`mobile-dev`)

## 1. Identité & Périmètre d'Intervention

- **Identifiant** : `mobile-dev`
- **Périmètre d'écriture exclusif** : [`health-kicks-mobile/`](file:///f:/Programmation/healthkicks-ecosystem/health-kicks-mobile/)
- **Périmètres en lecture seule** : [`contracts/`](file:///f:/Programmation/healthkicks-ecosystem/contracts/) (en particulier [`contracts/ble_gatt_specs.md`](file:///f:/Programmation/healthkicks-ecosystem/contracts/ble_gatt_specs.md) et [`contracts/README.md`](file:///f:/Programmation/healthkicks-ecosystem/contracts/README.md)), [`docs/`](file:///f:/Programmation/healthkicks-ecosystem/docs/)
- **Interdiction formelle** : Ne jamais modifier de fichiers en dehors de `health-kicks-mobile/` (notamment `health-kicks/`, `health-kicks-frontend/`, `health-kicks-edge-script/` ou la racine du workspace).

---

## 2. Stack Technique & Écosystème

- **Framework & Langage** : Flutter 3.19+ / Dart 3.3+
- **Connectivité BLE** : `flutter_blue_plus` (client BLE GATT central)
- **Connectivité IoT Cloud** : `mqtt_client` (relais vers AWS IoT Core via TLS X.509 ou WebSockets SigV4)
- **Gestion de l'état** : `flutter_riverpod`
- **Contrôle d'intégrité** : `crypto` (calcul et vérification de CRC32 sur le déversement burst)

---

## 3. Invariants & Règles d'Architecture à Respecter

1. **Rôle de Passerelle BLE-to-MQTT (Gateway Pattern)** :
   - Le smartphone agit comme un pont bidirectionnel transparent :
     * **Montant (Chaussure -> Cloud)** : Lors de la réception d'une notification BLE sur `7a5a0002-...` (Activity Detection), mapper immédiatement le payload en message MQTT JSON conforme à `contracts/README.md` et le publier sur `healthkicks/v1/{device_id}/events/detection` en QoS 1.
     * **Descendant (Cloud -> Chaussure)** : Lors de la réception d'un ordre haptique sur `healthkicks/v1/{device_id}/commands/haptic`, traduire le payload en trame binaire 4 octets (`[pattern_id, intensity, duration_ms]`) et l'écrire sur la caractéristique BLE `7a5a0003-...` (Haptic Command).
2. **Gestion du Burst Transfer Studio** :
   - Initialiser la session via la commande textuelle UTF-8 sur `7a5a0004-...` (`START <label> <duration_sec> <session_id>`).
   - Mémoriser dans un buffer local les paquets `DATA_CHUNK` reçus sur `7a5a0005-...`.
   - À la réception du paquet `END_OF_BURST` (`0x03`), valider l'intégrité via le CRC32 et le compte d'échantillons. En cas de succès, téléverser l'ensemble au format batch télémétrique vers l'API Cloud ou AWS IoT Core.
3. **Robustesse et Reconnexion BLE** :
   - Gérer les déconnexions intempestives (reconnexion automatique, synchronisation d'état au retour de connexion).
   - Négocier une MTU étendue (247 octets minimum) dès l'établissement de la liaison GATT pour optimiser le débit du burst transfer.

---

## 4. Protocole de Validation Locale

Avant toute validation de tâche ou commit, l'agent doit exécuter :

```bash
# Vérifier l'analyse statique et le linting
flutter analyze

# Exécuter les tests unitaires
flutter test
```
Tout échec bloque la livraison.
