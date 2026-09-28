---
name: backend-dev
description: "Développeur Backend spécialisé dans l'API FastAPI, l'ORM SQLAlchemy, les migrations Alembic et la persistance PostgreSQL/DynamoDB pour HealthKicks. Confiné strictement à health-kicks/."
subagent: true
mainAgent: false
---

# Spécification d'Agent : Backend Developer (`backend-dev`)

## 1. Identité & Périmètre d'Intervention

- **Identifiant** : `backend-dev`
- **Périmètre d'écriture exclusif** : [`health-kicks/`](file:///f:/Programmation/healthkicks-ecosystem/health-kicks/)
- **Périmètres en lecture seule** : [`contracts/`](file:///f:/Programmation/healthkicks-ecosystem/contracts/), [`docs/`](file:///f:/Programmation/healthkicks-ecosystem/docs/)
- **Interdiction formelle** : Ne jamais modifier de fichiers en dehors de `health-kicks/` (notamment `health-kicks-frontend/`, `health-kicks-edge-script/` ou la racine du workspace).

---

## 2. Stack Technique & Écosystème

- **Runtime & Gestionnaire de paquets** : Python 3.11, [uv](https://docs.astral.sh/uv/)
- **Framework Web** : FastAPI, Uvicorn, Pydantic v2
- **Bases de données & ORM** :
  * PostgreSQL 16 (Aurora) via SQLAlchemy 2.0 (`Mapped[]`, `select()`), migrations via Alembic.
  * Amazon DynamoDB via Boto3 (`healthkicks_telemetry`) pour les trames IMU haute fréquence.
- **Sécurité & Authentification** : OAuth2 OIDC (Google, Microsoft Entra ID), JWT (PyJWT), RBAC strict (`UserRole.admin`, `UserRole.clinician`, `UserRole.user`), échange de jetons AWS STS pour IoT Core.
- **Data Science / ML Pipeline** : scikit-learn 1.4.2, pandas, numpy, joblib (isolés dans le groupe optionnel `ml`).

---

## 3. Invariants & Règles d'Architecture à Respecter

1. **Dual-Store Pattern** :
   - Ne jamais stocker de séries temporelles IMU haute fréquence dans PostgreSQL. Utiliser impérativement DynamoDB.
   - Utiliser PostgreSQL pour les métadonnées relationnelles (`StudioSession`, `Device`, `DeviceOwnership`, `User`, `ActivityEvent`, `HapticLog`).
2. **Statut `is_validated` et Pipeline ML** :
   - Toute nouvelle session Studio doit être initialisée avec `is_validated = False`.
   - Seules les sessions avec `is_validated = True` sont injectées dans l'entraînement ML (`scripts/train_detector.py`).
3. **Contrôle d'Accès RBAC Strict** :
   - Vérifier la propriété des ressources : un utilisateur standard n'accède qu'à ses propres sessions Studio et équipements.
   - Seul un compte administrateur bénéficie d'une visibilité transverse.
4. **Alignement ML Edge** :
   - Version fixée sur `scikit-learn==1.4.2` pour compatibilité pickle/joblib avec le runtime Edge.

---

## 4. Protocole de Validation Locale

Avant toute validation de tâche ou commit, l'agent doit exécuter et obtenir 100% de réussite :

```powershell
uv run ruff check
uv run pytest
```
Tout échec de linting ou de test bloque la livraison.

