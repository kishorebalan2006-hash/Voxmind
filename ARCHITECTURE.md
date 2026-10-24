# VOXMIND ARCHITECTURE BLUEPRINT

Detailed design and architectural specifications for the VoxMind platform.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Client["Flutter Frontend Application"]
        UI["Material 3 Reactive UI"]
        Riverpod["Riverpod State Management"]
        SyncEngine["Sync Engine & Offline Local Queue"]
        AudioRec["Audio Recording & Diarization Engine"]
        TTS["Text-to-Speech & Voice Assistant"]
    end

    subgraph FirebaseLayer["Firebase Cloud Platform"]
        Auth["Firebase Authentication"]
        Firestore["Cloud Firestore (Multi-Tenant Scoped)"]
        Storage["Firebase Storage (Recordings & Reports)"]
        FCM["Firebase Cloud Messaging"]
    end

    subgraph BackendLayer["FastAPI Backend Services"]
        API["FastAPI REST & WebSocket Gateway"]
        AuthMiddleware["JWT Verification & RBAC Guards"]
        STT["Whisper Speech-to-Text Pipeline"]
        Diarizer["PyAnnote Speaker Diarization"]
        RAG["ChromaDB Vector Store & RAG Chat"]
        Intelligence["LLM Meeting Intelligence Engine"]
        ReportGen["PDF & DOCX Generator"]
        UsageService["Metering & Entitlement Guard"]
    end

    UI --> Riverpod
    Riverpod --> SyncEngine
    SyncEngine --> Firestore
    UI --> AudioRec
    AudioRec --> Storage
    UI --> TTS

    Riverpod --> Auth
    Riverpod --> API

    API --> AuthMiddleware
    API --> STT
    API --> Diarizer
    API --> RAG
    API --> Intelligence
    API --> ReportGen
    API --> UsageService
```

---

## 2. Layer Specifications

### A. Presentation Layer (Flutter)
- **Framework**: Flutter (Channel Stable) with Web and Mobile rendering support.
- **State Management**: Riverpod (`StateNotifierProvider`, `FutureProvider`, and `.select()` memoization for zero unnecessary rebuilds).
- **Navigation**: Declarative GoRouter with reactive route protection and workspace-gated paths.
- **Design System**: Material 3 with high-contrast accessibility tokens, adaptive sizing, and semantic labels.

### B. Service Layer (FastAPI Backend)
- **Engine**: Python 3.11 with FastAPI ASGI microservices.
- **Security**: Custom `SecurityHeadersMiddleware`, in-memory rate limiting, and RBAC dependency injection (`require_organization_member`, `require_admin_or_owner`).
- **AI Pipelines**:
  - Speech Recognition: Whisper STT.
  - Diarization: Speaker identification & speaking duration analytics.
  - Intelligence: Structured LLM output for summaries, action items, risks, and decisions.
  - Conversational RAG: Semantic search and question answering with source citations.

### C. Data & Persistence Layer
- **Cloud Firestore**: Multi-tenant database partitioned by `organizationId`. Client operations protected by hardened `firestore.rules`.
- **Firebase Storage**: Audio recordings and generated PDF/DOCX reports secured via `storage.rules`.
- **Offline Persistence**: Local `shared_preferences` queue with client-side idempotency keys for zero-loss network recovery.
