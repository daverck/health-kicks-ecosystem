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
  * PostgreSQL 16 (Aurora) via SQLAlchemy 2.0 (syntaxe moderne 2.0 avec `Mapped[]` et `select()`), migrations via Alembic.
  * Amazon DynamoDB via Boto3 (`healthkicks_telemetry`) pour les trames IMU brutes haute fréquence.
- **Sécurité & Authentification** : OAuth2 OIDC (Google, Microsoft Entra ID), JWT (PyJWT), RBAC strict (`UserRole.USER`, `UserRole.ADMIN`).
- **Data Science / ML Pipeline** : scikit-learn 1.4.2, pandas, numpy, joblib (isolés dans le groupe optionnel `ml`).

---

## 3. Invariants & Règles d'Architecture à Respecter

1. **Dual-Store Pattern** :
   - Ne jamais stocker de séries temporelles IMU haute fréquence dans PostgreSQL. Utiliser impérativement DynamoDB via `TelemetryService`.
   - Utiliser PostgreSQL pour les métadonnées transactionnelles (`StudioSession`, `Device`, `User`, `ActivityEvent`, `HapticLog`).
2. **Statut `is_validated` et Pipeline ML** :
   - Toute nouvelle session Studio doit être initialisée avec `is_validated = False`.
   - Dans [`scripts/train_detector.py`](file:///f:/Programmation/healthkicks-ecosystem/health-kicks/scripts/train_detector.py), ne charger que les sessions où `is_validated.is_(True)`.
3. **Contrôle d'Accès RBAC Strict** :
   - Vérifier systématiquement la propriété des ressources : un utilisateur standard ne doit pouvoir accéder qu'à ses propres sessions Studio (`session.user_id == user.id`).
   - Seul un compte administrateur peut accéder aux données transverses.
4. **Alignement ML Edge** :
   - Conserver impérativement l'alignement sur `scikit-learn==1.4.2` pour garantir la compatibilité des artefacts `.joblib` avec l'agent Edge.

---

## 4. Protocole de Validation Locale

Avant toute validation de tâche ou commit, l'agent doit exécuter :

```powershell
# Exécuter les tests backend
uv run pytest

# Vérifier la validité des modèles et migrations Alembic
uv run alembic check
```
Tout échec bloque la livraison.

