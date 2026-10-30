---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #0f172a
color: #f8fafc
---

# **HealthKicks**
### Chaussure Intelligente : Podométrie Haute Précision & Détection de Chute Autonome

**IoT Embarqué (ESP32-S3)** | **Edge AI (TinyML)** | **Passerelle Mobile & AWS IoT Core**

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **1. Architecture Globale : Du Capteur au Cloud**
### Pipeline Hybride Temps Réel & Ségrégation des Responsabilités

* **Chaussure (ESP32-S3)** : IMU 6-axes MPU-6050, inférence C++ pure (~12 µs), retour haptique PWM, serveur BLE GATT LESC.
* **Passerelle Mobile (Flutter)** : Client BLE, odométrie différentielle SQLite, sécurité OAuth2 PKCE RFC 7636, MQTT WebSockets SigV4.
* **Cloud & Backend (FastAPI / AWS)** : Broker AWS IoT Core (QoS 1), STS Token Broker (clés temporaires 15 min), DynamoDB & Aurora PostgreSQL 16.
* **Dashboard Web (Angular 22)** : Visualisation réactive via Angular Signals, suivi d'activité et mode Studio de capture.

<!-- Notes orateur :
Souligner la séparation stricte : le capteur est autonome pour la sécurité critique (chute), le mobile gère l'agrégation et le réseau, le cloud centralise et historise.
-->

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **2. Cœur IoT : Chaussure Instrumentée & ESP32-S3**
### Matériel, Référentiel Biomécanique & Maintenance Sécurisée

* **Hardware & Capteurs** : ESP32-S3-N16R8 (240 MHz dual-core), MPU-6050 I2C Fast-Mode (400 kHz), vibreur haptique PWM 10 kHz (MOSFET AO3400).
* **Référentiel Biomécanique ISB** : Axe Z vertical (+1g repos), Axe X propulsion/freinage, Axe Y médio-latéral.
* **Sécurité & Rollback OTA** : Double partition Flash A/B avec digest SHA-256 (32 octets), probation 15s avec rollback automatique en cas d'erreur IMU.
* **Chiffrement BLE LESC** : Appairage sécurisé Just Works avec échange de clés ECDH.

<!-- Notes orateur :
L'ESP32-S3 offre les extensions vectorielles DSP idéales pour le calcul de magnitude euclidienne. L'OTA est sécurisé pour éviter tout bricking d'un équipement scellé dans la semelle.
-->

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **3. Edge Machine Learning : Classification & Sécurité**
### 16 Indicateurs Canoniques & Forêt d'Arbres Randomisés (ExtraTrees)

* **Pourquoi l'Edge AI ?** Réaction d'urgence immédiate (< 1 ms), fonctionnement autonome sans réseau, confidentialité totale des données brutes.
* **16 Indicateurs Canoniques (19 Hz)** : Magnitudes euclidiennes invariantes en rotation (||a||, ||ω||), dispersions axiales, énergies spectrales moyennes.
* **Classifieur Hybride ExtraTrees** : Ensemble d'arbres décisionnels multiclasse (marche, course, escaliers, repos, chutes) hautement robuste au surapprentissage.
* **Double Verrou Biomécanique** : Détection du pic d'impact (> 16.2 m/s²) + confirmation d'immobilité anormale au sol (`isUprightFlatFootStillness`).

<!-- Notes orateur :
L'invariance par magnitude élimine les biais de placement de la semelle. Le double verrou évite les faux positifs lors des chocs sportifs (sauts, frappes).
-->

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **4. Boucle MLOps : Du Terrain au Code C Embarqué**
### Collecte Studio, Stratified 5-Fold & Transpilation sans Runtime

1. **Mode Studio** : Enregistrement de données IMU brutes (54/100 Hz), transfert burst BLE avec contrôle CRC32 vers DynamoDB.
2. **Évaluation Stratified 5-Fold** : Cache local incrémental pour accélérer l'entraînement. Équilibrage strict des classes rares (chutes). Optimisation sur le Macro F1.
3. **Transpilation C Pure (m2cgen)** : Modèle scikit-learn converti en C standard (`activity_model_generated.h`). 0 Ko d'allocation dynamique en RAM.
4. **Validation Automatique & CI** : Seuil éliminatoire Macro F1 ≥ 85% avant tout déploiement. Compilation de contrôle PlatformIO (`pio run`).

<!-- Notes orateur :
Cycle complet sans framework d'inférence lourd (pas de TensorFlow Lite Micro). Du code C pur, ultra-léger, inféré en quelques microsecondes.
-->

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **5. Réseau & Podométrie Différentielle Nette**
### Odométrie SQLite, Ventilation Horaire Réelle & AWS IoT Core

* **Podométrie Différentielle Mobile** :
  - Odomètre matériel monotone sur ESP32 (sans horloge RTC).
  - Calcul différentiel SQLite local : `delta = current - previous`.
  - Résilience totale aux reboots matériels et bascule nette à minuit sans pertes.
  - Ventilation horaire 100% réelle (`hourly_steps`), aucune extrapolation artificielle.
* **Passerelle Cloud Sécurisée (AWS IoT Core)** :
  - Session WebSockets MQTT signée cryptographiquement en SigV4 via jetons STS temporaires.
  - Alertes transmises en QoS 1 vers `healthkicks/v1/{deviceId}/events/detection`.

<!-- Notes orateur :
Architecture hors-ligne par conception. Si le téléphone perd le réseau, la podométrie continue d'être accumulée localement et synchronisée dès reconnexion.
-->

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **6. Performances Mesurées & Personnalisation**
### Métriques Clés d'Exécution & Réglage Dynamique

| Métrique Clé | Valeur Mesurée | Implication Système |
| :--- | :--- | :--- |
| **Temps d'inférence C** | **~12 µs** | 0.02% du CPU ESP32-S3 |
| **Précision ML (Macro F1)** | **92.4%** | Détection multi-allure fiable |
| **Empreinte RAM Modèle** | **0 Ko dynamique** | Aucune fragmentation mémoire |
| **Latence Alerte Chute** | **< 100 ms** | Envoi immédiat aux proches |

* **Sensibilité Ajustable** : Seuil d'impact réglable depuis l'application mobile (profil sportif vs profil senior/marcheur).
* **Autonomie Énergétique** : Optimisation continue avec passage en deep sleep en cas d'inactivité prolongée.

<!-- Notes orateur :
L'exécution en 12 microsecondes démontre la suprématie du code C compilé sur les moteurs d'inférence interprétés. Le réglage du seuil permet d'adapter la chaussure à tous les usages.
-->

---

<!--
_backgroundColor: #f8fafc
_color: #0f172a
-->

# **7. Conclusion & Perspectives**
### Les Piliers d'un Écosystème Connecté et Autonome

* **Edge Computing Décentralisé** : La sécurité critique (alerte chute) ne dépend d'aucun serveur ni d'aucun réseau.
* **Hybridation Capteur-Réseau** : Répartition optimale des charges entre ESP32-S3, smartphone et AWS IoT Core.
* **Zero Trust & Clés Éphémères** : Architecture sécurisée de bout en bout (LESC, PKCE, SigV4, STS).
* **Perspectives** :
  - Analyse avancée de la biomécanique de foulée (pronation / supination).
  - Apprentissage fédéré et adaptation dynamique au profil de marche de l'utilisateur.

---

<!--
_class: lead
backgroundColor: #0f172a
color: #f8fafc
-->

# **Merci pour votre attention**
### Questions & Échanges

**Projet HealthKicks** — Architecture IoT, Edge AI & Cloud
