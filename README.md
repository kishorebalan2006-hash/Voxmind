# VoxMind — Enterprise Meeting Intelligence & Accessibility Platform

**VoxMind** is an accessible, AI-powered meeting intelligence platform designed to transcribe, diarize, summarize, and analyze high-stakes meetings with zero-trust multi-tenant security and assistive accessibility.

---

## Key Features

- **Live Speech-to-Text & Diarization**: Multi-speaker acoustic segmentation with timestamped transcript alignments.
- **Assistive Accessibility Foundation**: Real-time live captions, customizable typography, auditory alerts, screen reader semantic labels, and hands-free voice summary narration.
- **Traceable AI Meeting Intelligence**: Grounded executive summaries, key decisions, prioritized action items, deadline detection, and risk analysis mapped to transcript source citations.
- **"Ask the Meeting" & Semantic Search**: Multi-turn conversational RAG across single meetings or organization-wide archives with vector embeddings and keyword filtering.
- **Productivity Analytics & Reports**: Organization meeting trends, speaker balance charts, action item metrics, and one-click PDF/DOCX professional report exports.
- **Governance, Admin & SaaS Metering**: Multi-tenant RBAC (Owner, Admin, Member), audit log trails, 4 subscription tiers (Free, Pro, Team, Enterprise), and soft/hard usage quota enforcement.
- **Offline First & Network Resilience**: Local queue persistence via `shared_preferences` with idempotent background synchronization.
- **Enterprise Security Hardened**: Strict Firestore security rules, Firebase Storage policies, security headers middleware, and in-memory API rate limiting.

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│               Flutter Web / Mobile Client              │
│  Riverpod State • GoRouter • Material 3 • Offline Sync │
└───────────┬────────────────────────────────┬───────────┘
            │                                │
     Firebase SDKs                    FastAPI Backend
(Auth • Firestore • Storage)     (STT • LLM • RAG • Diarization)
```

---

## Getting Started

### 1. Flutter Client Setup
```bash
cd voxmind
flutter pub get
flutter run -d chrome
```

### 2. FastAPI Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Running Automated Tests
```bash
# Backend Test Suite
cd backend
pytest

# Flutter Quality Gate & Tests
cd voxmind
flutter analyze lib/
flutter test
flutter build web --no-tree-shake-icons
```

---

## Documentation Index
- [`ARCHITECTURE.md`](file:///b:/final%20project/ARCHITECTURE.md) — System Blueprint & Data Flow
- [`SECURITY_AUDIT.md`](file:///b:/final%20project/SECURITY_AUDIT.md) — Zero-Trust Security Report
- [`PERFORMANCE.md`](file:///b:/final%20project/PERFORMANCE.md) — Profiling & Benchmarking Results
- [`DEPLOYMENT.md`](file:///b:/final%20project/DEPLOYMENT.md) — CI/CD & Deployment Operations
- [`ENVIRONMENTS.md`](file:///b:/final%20project/ENVIRONMENTS.md) — Dev / Staging / Prod Configuration
- [`QA_REPORT.md`](file:///b:/final%20project/QA_REPORT.md) — Quality Assurance Matrix
- [`RELEASE_CHECKLIST.md`](file:///b:/final%20project/RELEASE_CHECKLIST.md) — Production Deployment Checklist
- [`DEMO_GUIDE.md`](file:///b:/final%20project/DEMO_GUIDE.md) — 3-Minute Hackathon Demo Script
- [`FINAL_RELEASE_STATUS.md`](file:///b:/final%20project/FINAL_RELEASE_STATUS.md) — Production Release Sign-off
