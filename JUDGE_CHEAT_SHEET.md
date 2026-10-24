# VOXMIND — FINAL JUDGE CHEAT SHEET

Concise, technical 1–3 sentence answers for all anticipated judge inquiries.

---

### 1. Why VoxMind?
> *"Because conventional meeting tools rely solely on audio, alienating users with hearing or visual disabilities and causing fast-paced teams to lose track of critical decisions. VoxMind unifies accessibility and AI intelligence into one seamless workspace."*

### 2. What makes VoxMind unique?
> *"Unlike standard AI note-takers that generate unverified summaries, every decision, action item, and RAG answer in VoxMind includes a clickable citation chip linking directly to the verified spoken audio timestamp."*

### 3. Why is accessibility central?
> *"Accessibility is not an afterthought in VoxMind; our dual-pathway architecture provides real-time captions and visual flash alerts for hearing accessibility alongside hands-free voice summary narration and full screen reader semantics for vision accessibility."*

### 4. Why Flutter?
> *"Flutter enables a high-performance, single-codebase experience across Web and Mobile with custom-tailored accessibility semantics, responsive Material 3 design, and smooth 60fps animations."*

### 5. Why Firebase?
> *"Firebase provides enterprise-grade identity authentication, real-time Firestore reactive streams, and scalable cloud storage secured by granular tenant-isolation security rules."*

### 6. Why FastAPI?
> *"FastAPI delivers high-throughput asynchronous execution, native OpenAPI documentation, and seamless integration with Python's leading machine learning and audio processing libraries."*

### 7. How does transcription work?
> *"Audio recordings are processed through Whisper STT models to generate precise, timestamped text segments synchronized with the audio stream."*

### 8. How does speaker identification work?
> *"PyAnnote diarization segments audio by acoustic embeddings, mapping distinct speech blocks to color-coded speaker cards and participation analytics."*

### 9. How does VoxMind help deaf users?
> *"Deaf and hard-of-hearing users can follow meetings in real time via streaming live captions, color-coded speaker attribution tags, large typography modes, and non-intrusive visual flash alerts."*

### 10. How does VoxMind help visually impaired users?
> *"Visually impaired professionals can navigate using screen reader semantics and keyboard focus orders, or listen to one-click hands-free Text-to-Speech voice summaries of all decisions and action items."*

### 11. How do you reduce AI hallucinations?
> *"AI intelligence and conversational RAG prompts are strictly bounded to stored transcript segments; models are instructed to cite exact timestamps and return explicit 'unresolved' states rather than fabricating unmentioned facts."*

### 12. How do you secure meeting data?
> *"VoxMind enforces zero-trust tenant isolation via Firebase Auth, Firestore security rules requiring `isMemberOf(orgId)`, secure headers (`nosniff`, `DENY`), and server-side secret management."*

### 13. How do you isolate organizations?
> *"All Firestore queries and storage buckets are partitioned by `organizationId`, and security rules prevent users from reading or modifying data outside their authenticated organization."*

### 14. How does offline support work?
> *"When offline, meeting actions and audio metadata are queued locally in `shared_preferences` with client-side idempotency keys, syncing seamlessly upon network recovery."*

### 15. How does the platform scale?
> *"Stateless FastAPI backend containers scale horizontally on Cloud Run, while Firestore and Firebase Storage handle massive concurrent data reads and media storage automatically."*

### 16. What is the future scope?
> *"Future milestones include real-time multi-lingual speech translation, direct Google/Outlook calendar task synchronization, and on-device edge transcription."*
