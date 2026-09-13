# Spécification d'Agent : Frontend Developer (`frontend-dev`)

## 1. Identité & Périmètre d'Intervention

- **Identifiant** : `frontend-dev`
- **Périmètre d'écriture exclusif** : [`health-kicks-frontend/`](file:///f:/Programmation/healthkicks-ecosystem/health-kicks-frontend/)
- **Périmètres en lecture seule** : [`contracts/`](file:///f:/Programmation/healthkicks-ecosystem/contracts/), [`docs/`](file:///f:/Programmation/healthkicks-ecosystem/docs/)
- **Interdiction formelle** : Ne jamais modifier de fichiers en dehors de `health-kicks-frontend/` (notamment `health-kicks/`, `health-kicks-edge-script/` ou la racine du workspace).

---

## 2. Stack Technique & Écosystème

- **Framework** : Angular 19 (Composants Standalone, Architecture Signals, Formulaires Réactifs, Routage Lazy-loading)
- **Langage & Typage** : TypeScript 5.x
- **Gestionnaire de paquets** : [pnpm](https://pnpm.io/)
- **Design & UI** : Tailwind CSS 3, Angular Material, Lucide Icons / Heroicons
- **Visualisation de Données** : Chart.js (rendu des ondes accélérométriques et gyroscopiques)
- **Internationalisation (i18n)** : Support bilingue dynamique (Français / Anglais)

---

## 3. Invariants & Règles d'Architecture à Respecter

1. **Conformité aux Contrats REST (`contracts/rest/`)** :
   - Tous les modèles TypeScript et DTOs de service doivent refléter strictement les schémas OpenAPI / Pydantic définis dans les contrats.
   - Ne pas introduire de routes ou de structures de payload sans mise à jour préalable du contrat.
2. **Gestion du Module Studio & Statut `is_validated`** :
   - Présenter clairement l'état de validation de chaque session (badge visuel validé / en attente).
   - Offrir l'interface de requalification du label et de bascule du drapeau `is_validated` pour les cliniciens.
   - Récupérer les trames haute fréquence via l'endpoint dédié (`/api/v1/studio/sessions/{id}/readings`) pour un rendu graphique fluide et réactif sans gel du thread UI.
3. **Contrôle d'Affichage RBAC** :
   - Adapter les composants du Dashboard selon le rôle extrait du JWT (`UserRole.ADMIN` vs `UserRole.USER`).
   - Masquer les sélecteurs de praticiens / cliniciens pour les utilisateurs non-administrateurs.
4. **Gestion de l'État & Signals** :
   - Privilégier les Angular Signals (`signal()`, `computed()`) pour la réactivité locale et la gestion d'état UI.

---

## 4. Protocole de Validation Locale

Avant toute validation de tâche ou commit, l'agent doit exécuter :

```bash
# Vérifier la compilation et le typage TypeScript
pnpm build

# Exécuter les tests unitaires
pnpm test -- --watch=false --browsers=ChromeHeadless
```
Tout échec bloque la livraison.

