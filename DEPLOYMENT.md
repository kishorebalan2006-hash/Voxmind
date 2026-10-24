# VOXMIND CI/CD & PRODUCTION DEPLOYMENT GUIDE

Comprehensive guide for automated testing, container builds, staging deployments, and official production releases.

---

## 1. Release Version & Tag
- **Production Version**: `1.0.0`
- **Git Release Tag**: `v1.0.0`
- **Release Status**: **OFFICIALLY DEPLOYED & PRODUCTION READY**

---

## 2. Branching Strategy & Git Workflow

```text
feature/<name>  ──(PR)──>  develop  ──(Automated Deploy)──>  Staging Environment
                               │
                          (Release PR)
                               ↓
                             main  ──(Protected Gate)──>  Production Environment
```

- **`develop` branch**: Staging integration branch. Every push triggers GitHub Actions to test and deploy to the Staging environment.
- **`main` branch**: Production release branch. Requires successful staging sign-off and explicit approval gates.

---

## 3. GitHub Actions Workflows

| Workflow | File Path | Trigger | Purpose |
|---|---|---|---|
| **Flutter CI** | `.github/workflows/flutter-ci.yml` | Push / PR on `main`, `develop` | Dart format, Flutter analyze, 139 unit tests, web bundle build |
| **Backend CI** | `.github/workflows/backend-ci.yml` | Push / PR on `main`, `develop` | Flake8 linting, pytest suite, Docker container compilation |
| **Security CI** | `.github/workflows/security-ci.yml` | Push / PR on `main`, `develop` | TruffleHog secret scanning & pip-audit dependency scan |
| **Staging Deploy** | `.github/workflows/staging.yml` | Push on `develop` | Automated deployment to staging Firebase & Cloud Run |

---

## 4. Rollback & Disaster Recovery Procedures

1. **Frontend (Flutter Web)**:
   - Rollback Firebase Hosting release:
     ```bash
     firebase hosting:releases:rollback --project voxmind-production
     ```
2. **Backend (FastAPI)**:
   - Re-route Cloud Run traffic to the previous healthy revision:
     ```bash
     gcloud run services update-traffic voxmind-backend --to-revisions=voxmind-backend-PREVIOUS_REVISION=100
     ```
3. **Firestore & Storage Rules**:
   - Re-deploy previous tagged rules from Git history (`git checkout v1.0.0 -- firestore.rules && firebase deploy --only firestore:rules`).
