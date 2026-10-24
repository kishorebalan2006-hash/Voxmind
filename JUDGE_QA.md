# VOXMIND HACKATHON JUDGE Q&A PREPARATION

Anticipated judge inquiries and concise, technical answers for the VoxMind presentation.

---

### Q1: How do you prevent LLM hallucinations in high-stakes meeting summaries?
**Answer**:
> *"We implement a strict RAG retrieval boundary where LLM prompts strictly enforce source segment citations. Every summary claim, decision, and action item must map to a verified timestamped transcript range. If information is ambiguous or unmentioned, our models return explicit 'unassigned' or 'unresolved' states rather than fabricating facts."*

### Q2: How is multi-tenant enterprise data isolated?
**Answer**:
> *"We enforce zero-trust multi-tenancy at every tier. Cloud Firestore security rules mandate `request.auth.token.organizationId == orgId` across all collections and subcollections. Our backend API dependencies inject organization-scoped database queries, ensuring Organization A cannot access or mutate Organization B's data under any condition."*

### Q3: What makes your accessibility implementation genuine rather than cosmetic?
**Answer**:
> *"We designed two distinct assistive workflows: for deaf and hard-of-hearing users, we provide real-time streaming captions, high-contrast themes (>7:1 ratio), visual speaker tags, and flash alerts. For visually impaired users, we provide full screen reader semantic labels, keyboard navigation, and complete Text-to-Speech voice summary narration."*

### Q4: How does VoxMind handle network loss during recording?
**Answer**:
> *"Audio recordings are written directly to local device storage before upload. If the network drops, our offline sync engine queues metadata locally in `shared_preferences` with client-generated idempotency keys, seamlessly resuming upload and synchronization as soon as connectivity is restored."*
