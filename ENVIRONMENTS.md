# VOXMIND ENVIRONMENT SEPARATION GUIDE

This document establishes the architecture for isolating **Development**, **Staging**, and **Production** environments in VoxMind.

---

## 1. Environment Matrix

| Parameter | Development | Staging | Production |
|---|---|---|---|
| **Flutter Host** | `http://localhost:3000` | `https://staging.voxmind.ai` | `https://app.voxmind.ai` |
| **FastAPI Backend** | `http://127.0.0.1:8000` | `https://api-staging.voxmind.ai` | `https://api.voxmind.ai` |
| **Firebase Project** | `voxmind-dev` / Local Emulators | `voxmind-staging` | `voxmind-production` |
| **Firestore Database** | Isolated dev instance | Dedicated staging instance | Multi-region production instance |
| **Storage Bucket** | `gs://voxmind-dev.appspot.com` | `gs://voxmind-staging.appspot.com` | `gs://voxmind-prod.appspot.com` |
| **Debug Mode** | `true` | `false` | `false` |
| **Customer Data Allowed** | No (Mock fixtures) | No (Synthetic test suites) | Yes (Encrypted real-world data) |

---

## 2. Environment Variable Configuration

All runtime configurations are passed via environment variables (never committed to repository):

```bash
ENVIRONMENT=staging # [development | staging | production]
DEBUG=false
ALLOWED_ORIGINS=https://staging.voxmind.ai,https://admin-staging.voxmind.ai
FIREBASE_PROJECT_ID=voxmind-staging
FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase_credentials.json
```
