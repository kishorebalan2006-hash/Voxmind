# VOXMIND — FINAL HACKATHON PRESENTATION GUIDE

A comprehensive overview of VoxMind for hackathon judges, investors, and enterprise stakeholders.

---

## 1. Problem
Meetings contain mission-critical discussions, yet professionals miss key details due to fast speech, time constraints, noise, or accessibility barriers. For deaf, hard-of-hearing, and visually impaired team members, conventional audio-first meetings present substantial communication barriers.

## 2. Solution
VoxMind converts spoken meeting audio into real-time accessible captions, speaker-tagged transcripts, grounded AI summaries, prioritized action items, and conversational Q&A — ensuring every meeting is understandable, searchable, and actionable.

## 3. Why VoxMind?
Traditional note-taking tools generate loose, unverified summaries. VoxMind grounds every decision and action item in verified transcript timestamps while providing a dual-path accessibility suite for hearing and vision needs.

## 4. Key Features
- **Real-Time Live Captions**: Streaming text with speaker diarization tags and visual flash alerts.
- **Timestamped Transcripts**: Virtualized lazy rendering with keyword search filtering.
- **Traceable AI Intelligence**: Summaries, decisions, deadlines, and action items with clickable citation chips.
- **"Ask the Meeting" (RAG)**: Conversational Q&A grounded strictly in meeting quotes.
- **Voice Summary Narration**: Hands-free TTS for visually impaired users.
- **1-Click Reports**: Executive PDF and DOCX exports.

## 5. Accessibility Suite
- **Hearing**: Live captions, speaker tags, large typography mode, visual flash cues, WCAG AAA contrast.
- **Vision**: Full screen reader `Semantics` tree, keyboard navigation, hands-free voice summary narration.

## 6. AI Architecture
- **Whisper STT**: High-accuracy speech-to-text with segment timestamp alignment.
- **PyAnnote Diarization**: Multi-speaker segmentation and speaking-time breakdown.
- **Sliding-Window RAG**: Grounded LLM generation with mandatory transcript citation bounds to eliminate hallucinations.

## 7. Tech Stack
- **Frontend**: Flutter, Dart, Riverpod, GoRouter, Material 3.
- **Backend**: FastAPI, Python 3.11, Docker.
- **Data & Auth**: Firebase Auth, Cloud Firestore, Firebase Storage.

## 8. Enterprise Security
- Zero-trust multi-tenancy enforced by Firestore rules (`isMemberOf(orgId)`).
- Rate limiting, security headers (`nosniff`, `DENY`), and server-side secret management.

## 9. Business Value
- Saves 3–5 hours/week per employee on meeting debriefs.
- Eliminates dropped commitments with explicit action item ownership and due dates.

## 10. Social Impact
- Empowers deaf, hard-of-hearing, and visually impaired professionals to participate with equal autonomy.

## 11. Live Demo Flow (3 Minutes)
- `0:00` Problem → `0:20` Introduce VoxMind → `0:35` Login → `0:45` Dashboard → `1:00` Open Meeting → `1:15` Live Captions → `1:30` Speaker Diarization → `1:45` Transcript → `2:00` AI Summary → `2:15` Decisions & Actions → `2:30` Ask Meeting → `2:45` Accessibility → `2:55` Final Impact.

## 12. Future Scope
- Real-time multi-lingual translation and automated calendar task synchronization.
