---
trigger: always_on
description: Always transcribe user voice/audio notes word-for-word in the original spoken language at the start of the response
---

# Audio Note Transcription Rule

Whenever the user submits an audio recording or spoken voice note in their prompt, the agent must prioritize immediate, transparent acoustic feedback before initiating cognitive reasoning or vault modifications.

---

## 1. Core Operating Principle: Acoustic Verification First

Spoken inputs introduce transcription ambiguity, phonetic artifacts, and acoustic noise. Displaying a faithful, word-for-word transcript at the very top of the agent response establishes immediate mutual ground truth between the user and the agent:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. INCOMING SPOKEN AUDIO STREAM                             │
│    User provides voice note (e.g., Polish or English).      │
├─────────────────────────────────────────────────────────────┤
│ 2. VERBATIM RESPONSE TRANSCRIPTION BLOCK                    │
│    Lead response with exact acoustic text in original lang. │
├─────────────────────────────────────────────────────────────┤
│ 3. COGNITIVE REASONING & DOWNSTREAM EXECUTION               │
│    Translate thoughts to English, update vault, reply.      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory Formatting & Execution Protocols

### Protocol 1: Response-Leading Transcription Callout
The very first lines of the agent's response must display a dedicated markdown blockquote containing the verbatim transcript:

```markdown
> 🎙️ **Audio Transcription:**  
> *"Exact words spoken by the user in original language..."*
```

- **No Preceding Text**: No greetings, preamble, tool call summaries, or conversational filler may appear above the audio transcription block.
- **Verbatim Fidelity**: Transcribe spoken words exactly as articulated, preserving technical terms, idioms, and phrasing without premature editing or summarization.

### Protocol 2: Preserve the Original Spoken Language
- The transcription block must **never** be translated into English if the user spoke in another language (e.g., Polish).
- Preserving the original spoken language allows the user to immediately verify that the acoustic model correctly parsed domain-specific terminology and architectural intent.

### Protocol 3: Immediate Operational Continuity
- Directly below the transcription quote, begin addressing the user's intent without redundant meta-commentary (e.g., avoid *"Now I will process your voice note..."*).
- If the user spoke in Polish, maintain Polish conversational dialogue in the chat while persisting all vault documentation changes strictly in English per [`notes-language.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/notes-language.md).

---

## 3. Edge Cases & Multimodal Handshakes

| Scenario | Agent Execution Protocol |
| :--- | :--- |
| **Pure Audio Prompt** | Render transcription block at line 1; proceed directly to answering/executing. |
| **Audio + Accompanying Text** | Render transcription block for audio first; reference and integrate the text prompt immediately after. |
| **Unclear or Phonetically Degraded Audio** | Transcribe best phonetic match; append a brief inline alert: `> *[Acoustic clarity degraded around timestamp X: inferred intent is Y]*`. |
| **Code Snippets Spoken Aloud** | Transcribe words as spoken in the quote; provide clean, formatted code blocks in the subsequent operational response. |
