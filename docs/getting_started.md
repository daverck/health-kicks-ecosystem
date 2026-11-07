# Quick Start Guide - HealthKicks Ecosystem

Welcome to the **HealthKicks** development environment. This guide outlines prerequisites, local infrastructure initialization, and how to run each component of the ecosystem.

---

## 1. System Prerequisites

To develop across the complete ecosystem, install the following tools:

- **Git** 2.40+
- **Python** 3.11 with [uv](https://docs.astral.sh/uv/) package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh` or via winget/brew).
- **Node.js** 22+ with [pnpm](https://pnpm.io/) 9+ (`corepack enable && corepack prepare pnpm@latest --activate`).
- **Flutter SDK** 3.19+ and **Dart SDK** 3.3+.
- **PlatformIO Core** (`uv tool install platformio` or via VS Code extension).
- **Docker & Docker Compose** (for local development infrastructure).

---

## 2. Cloning the Repository

The ecosystem uses Git submodules for each independent software project:

```bash
git clone --recursive https://github.com/daverck/healthkicks-ecosystem.git
cd healthkicks-ecosystem

# If already cloned without submodules:
git submodule update --init --recursive
```

Install pre-commit hooks to validate exchange contracts before each commit:

```bash
uv tool run pre-commit install
```

---

## 3. Launching Local Infrastructure (Docker)

The [`docker-compose.yml`](file:///f:/Programmation/healthkicks-ecosystem/docker-compose.yml) file at the repository root starts the required local infrastructure services:

- **PostgreSQL 16** (port `5432`)
- **LocalStack / DynamoDB Local** (port `4566`)
- **Eclipse Mosquitto MQTT Broker** (port `1883` and WebSocket `9001`)

```bash
docker compose up -d
```

Verify that containers are healthy:

```bash
docker compose ps
```

---

## 4. Starting Subsystems

### A. FastAPI Backend (`health-kicks/`)

1. Navigate to the backend directory:
   ```bash
   cd health-kicks
   ```
2. Install the virtual environment and dependencies with `uv`:
   ```bash
   uv sync
   ```
3. Run Alembic database migrations:
   ```bash
   uv run alembic upgrade head
   ```
4. Start the FastAPI development server:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - Interactive Swagger documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - API health check: [http://localhost:8000/health](http://localhost:8000/health)

5. Run the test suite:
   ```bash
   uv run pytest
   ```

---

### B. Angular 22 Frontend (`health-kicks-frontend/`)

1. Navigate to the frontend directory:
   ```bash
   cd health-kicks-frontend
   ```
2. Install dependencies with `pnpm`:
   ```bash
   pnpm install
   ```
3. Start the Angular development server:
   ```bash
   pnpm start
   ```
   - Application accessible at: [http://localhost:4200](http://localhost:4200)

4. Run Vitest unit tests and production build:
   ```bash
   pnpm test:ci
   pnpm run build
   ```

---

### C. Flutter Mobile Application (`health-kicks-mobile/`)

1. Navigate to the mobile directory:
   ```bash
   cd health-kicks-mobile
   ```
2. Fetch Flutter packages:
   ```bash
   flutter pub get
   ```
3. Run static analysis and unit tests:
   ```bash
   flutter analyze
   flutter test
   ```
4. Launch on an emulator or connected device:
   ```bash
   flutter run
   ```

---

### D. ESP32-S3 Firmware (`health-kicks-esp32-s3/`)

1. Navigate to the firmware directory:
   ```bash
   cd health-kicks-esp32-s3
   ```
2. Compile firmware for the ESP32-S3 target:
   ```bash
   uv tool run --from platformio pio run
   ```
3. Flash the device connected via USB (or prepare the OTA binary):
   ```bash
   uv tool run --from platformio pio run --target upload
   ```

---

## 5. Global Ecosystem Verification

Before submitting changes, run contract verification and pre-commit checks at the repository root:

```bash
# Verify BLE GATT and OpenAPI contracts
python scripts/verify_ble_contracts.py
python scripts/verify_openapi_drift.py

# Run all pre-commit hooks
uv tool run pre-commit run --all-files
```
