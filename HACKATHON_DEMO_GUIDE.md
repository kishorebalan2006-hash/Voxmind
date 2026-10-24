# VOXMIND HACKATHON DEMO GUIDE & PITCH SCRIPT

**Platform**: VoxMind — Accessible AI Meeting Intelligence Platform  
**Target Pitch Duration**: 3 to 5 Minutes  
**Target Audience**: Hackathon Judges, Enterprise Clients, & Accessibility Advocates  

---

## 1. Executive Hook & Pitch Statement

> *"Millions of professionals with hearing or visual impairments, as well as fast-moving teams, lose hours every week struggling to capture, track, and act on meeting conversations. **VoxMind** transforms spoken meetings into structured, searchable, and fully accessible intelligence — with real-time captions, grounded AI summaries, and hands-free voice assistance."*

---

## 2. 3-Minute Hackathon Demo Script

```text
⏱️ [0:00 - 0:30] 1. The Problem & Accessible Live Recording
⏱️ [0:30 - 1:15] 2. Traceable AI Intelligence & Decision Tracking
⏱️ [1:15 - 2:00] 3. "Ask the Meeting" (RAG) & Semantic Search
⏱️ [2:00 - 2:30] 4. Hands-Free Voice Assistant & Accessibility
⏱️ [2:30 - 3:00] 5. Productivity Analytics, PDF Report & Closing Impact
```

### [0:00 - 0:30] — Part 1: Problem & Accessible Live Captions
1. **Show**: Open **Dashboard** at `http://localhost:3000`.
2. **Talk**: *"Let’s start in the Meeting Room. During high-stakes strategy discussions, keeping up with multiple speakers is challenging."*
3. **Action**: Click **Start Recording** to launch the live recording dialog.
4. **Demonstrate**:
   - Live stream with speaker diarization.
   - **High-Contrast mode** and **Large Font toggle** designed specifically for deaf and hard-of-hearing participants.

### [0:30 - 1:15] — Part 2: AI Meeting Intelligence & Source Traceability
1. **Show**: Open the processed **Quarterly Strategic Roadmap** meeting.
2. **Talk**: *"Once a meeting concludes, VoxMind’s AI engine extracts structured intelligence with zero hallucinations."*
3. **Demonstrate**:
   - **Executive Summary**: 3 concise bullet points.
   - **Key Decisions & Prioritized Action Items**: Clearly assigned owners, status tags, and deadlines.
   - **Source Traceability**: Click any decision or action item citation chip — the transcript instantly highlights and seeks to the exact spoken timestamp!

### [1:15 - 2:00] — Part 3: "Ask the Meeting" (RAG) & Semantic Search
1. **Show**: Switch to the **Ask Meeting** tab.
2. **Talk**: *"Need specific answers from a 1-hour call? You can chat directly with the meeting."*
3. **Action**: Type: *"What was decided regarding the Q4 security audit deadline?"*
4. **Demonstrate**: Instant, grounded response citing specific speaker quotes without guessing.

### [2:00 - 2:30] — Part 4: Hands-Free Voice Assistant & Accessibility
1. **Show**: Click the **Voice Summary** player at the top right.
2. **Talk**: *"For visually impaired executives or busy team members commuting hands-free, VoxMind narrates the entire summary aloud with adjustable pitch and speed."*
3. **Demonstrate**: Voice playback starting and pausing cleanly.

### [2:30 - 3:00] — Part 5: Analytics, PDF Reports & Closing Impact
1. **Show**: Open **Analytics** & **Reports**.
2. **Action**: Click **Export PDF Report** to show the professional 1-click executive brief.
3. **Closing Statement**:
   > *"VoxMind is an AI-powered accessible meeting intelligence platform that transforms conversations into understandable, searchable, and actionable information while making meetings genuinely inclusive for all professionals."*

---

## 3. Demo Fallback & Reliability Contingencies

| Scenario | Fallback Action |
|---|---|
| **Microphone Permission Blocked** | Open the pre-seeded **Quarterly Strategic Roadmap** demo meeting to demonstrate transcript, captions, AI summary, and citations. |
| **No Internet / Offline Presentation** | VoxMind automatically uses local `shared_preferences` cached demo data and local fallback models. |
| **TTS Audio Disabled on Projector** | Highlight the visual high-contrast live captions and citation highlighting. |
