# Guide de Démarrage Rapide - HealthKicks Ecosystem

Bienvenue dans l'environnement de développement de **HealthKicks**. Ce guide détaille les prérequis, l'initialisation de l'infrastructure locale et le lancement de chaque composant de l'écosystème.

---

## 1. Prérequis Système

Pour développer sur l'écosystème complet, installez les outils suivants sur votre poste :

* **Git** 2.40+
* **Python** 3.11 avec l'outil de gestion de paquets [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh` ou via winget/brew).
* **Node.js** 22+ avec [pnpm](https://pnpm.io/) 9+ (`corepack enable && corepack prepare pnpm@latest --activate`).
* **Flutter SDK** 3.19+ et **Dart SDK** 3.3+.
* **PlatformIO Core** (`uv tool install platformio` ou via extension VS Code).
* **Docker & Docker Compose** (pour l'infrastructure de développement locale).

---

## 2. Clonant le Monorepo

L'écosystème utilise des sous-modules Git pour chaque brique logicielle indépendante :

```bash
git clone --recursive https://github.com/daverck/healthkicks-ecosystem.git
cd healthkicks-ecosystem

# Si déjà cloné sans les sous-modules :
git submodule update --init --recursive
```

Installez les hooks pre-commit pour certifier les contrats d'échange avant chaque commit :
```bash
uv tool run pre-commit install
```

---

## 3. Lancement de l'Infrastructure Locale (Docker)

Le fichier [`docker-compose.yml`](file:///f:/Programmation/healthkicks-ecosystem/docker-compose.yml) à la racine démarre les services d'infrastructure requis en local :
* **PostgreSQL 16** (port `5432`)
* **LocalStack / DynamoDB Local** (port `4566`)
* **Eclipse Mosquitto MQTT Broker** (port `1883` et WebSocket `9001`)

```bash
docker compose up -d
```

Vérifiez que les conteneurs sont sains :
```bash
docker compose ps
```

---

## 4. Démarrage des Sous-Systèmes

### A. Backend FastAPI (`health-kicks/`)

1. Naviguez dans le répertoire backend :
   ```bash
   cd health-kicks
   ```
2. Installez l'environnement virtuel et les dépendances avec `uv` :
   ```bash
   uv sync
   ```
3. Exécutez les migrations de base de données Alembic :
   ```bash
   uv run alembic upgrade head
   ```
4. Lancez le serveur de développement FastAPI :
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   * Documentation Swagger interactive : [http://localhost:8000/docs](http://localhost:8000/docs)
   * Santé de l'API : [http://localhost:8000/health](http://localhost:8000/health)

5. Exécutez la suite de tests :
   ```bash
   uv run pytest
   ```

---

### B. Frontend Angular 22 (`health-kicks-frontend/`)

1. Naviguez dans le répertoire frontend :
   ```bash
   cd health-kicks-frontend
   ```
2. Installez les dépendances avec `pnpm` :
   ```bash
   pnpm install
   ```
3. Lancez le serveur Angular en mode développement :
   ```bash
   pnpm start
   ```
   * Application accessible sur : [http://localhost:4200](http://localhost:4200)

4. Exécutez les tests unitaires Vitest et le build :
   ```bash
   pnpm test:ci
   pnpm run build
   ```

---

### C. Application Mobile Flutter (`health-kicks-mobile/`)

1. Naviguez dans le répertoire mobile :
   ```bash
   cd health-kicks-mobile
   ```
2. Récupérez les paquets Flutter :
   ```bash
   flutter pub get
   ```
3. Exécutez l'analyse statique et les tests unitaires :
   ```bash
   flutter analyze
   flutter test
   ```
4. Lancez sur émulateur ou appareil connecté :
   ```bash
   flutter run
   ```

---

### D. Firmware ESP32-S3 (`health-kicks-esp32-s3/`)

1. Naviguez dans le répertoire firmware :
   ```bash
   cd health-kicks-esp32-s3
   ```
2. Compilez le firmware pour la cible ESP32-S3 :
   ```bash
   uv tool run --from platformio pio run
   ```
3. Flashez l'appareil connecté par port USB (ou préparez le binaire OTA) :
   ```bash
   uv tool run --from platformio pio run --target upload
   ```

---

## 5. Vérification Globale de l'Écosystème

Avant de soumettre une modification, exécutez la validation des contrats et des hooks à la racine du monorepo :

```bash
# Vérification des contrats BLE GATT et OpenAPI
python scripts/verify_ble_contracts.py
python scripts/verify_openapi_drift.py

# Exécution de l'ensemble des hooks pre-commit
uv tool run pre-commit run --all-files
```

