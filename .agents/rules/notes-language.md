---
trigger: always_on
description: Enforce English exclusively for all notes and documentation, language mirroring in chat, and audio note transcription.
---

# Notes Language & Conversational Protocol Rule

All notes, documentation, architectural guidelines, research logs, schemas, and markdown files in this workspace must be written and persisted exclusively in **English**. Simultaneously, the agent must maintain strict **language mirroring** during live chat dialogues to ensure conversational cohesion.

---

## 1. Core Operating Architecture: Bilingual Interface, Monolingual Vault

To eliminate cognitive friction and maintain publishable epistemic integrity, the agent strictly separates interactive discussion from persisted knowledge storage:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INTERFACE LAYER (CONVERSATIONAL DIALOGUE)           │
│    Mirror user's language (e.g., 100% Polish or English).   │
├─────────────────────────────────────────────────────────────┤
│ 2. TRANSLATION & CONCEPTUAL DISTILLATION PIPELINE           │
│    Translate user insights into idiomatic, technical English.│
├─────────────────────────────────────────────────────────────┤
│ 3. PERSISTED KNOWLEDGE BASE (THE OBSIDIAN VAULT)            │
│    100% English notes, frontmatter, diagrams, and wikilinks. │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory Language Protocols

### 1. Exclusively English Notes
- All note titles, YAML frontmatter (titles, tags, aliases), section headings, body paragraphs, bullet points, table cells, code comments, and ASCII diagram labels must be written in English.
- **Never write Polish or non-English text directly into note files**, with the sole exception of proper nouns or official non-English citations where strictly unavoidable.

### 2. Spoken Audio Note Handling
- When the user submits an audio recording or voice note:
  1. Always lead the response with a faithful, word-for-word transcript in the original spoken language per [`audio-transcription.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/audio-transcription.md).
  2. Translate user insights, requirements, and mental models into idiomatic English before persisting them into vault notes.

### 3. Conversational Consistency & Language Mirroring
- **Strict Language Mirroring**: The chat dialogue must strictly mirror the language used by the user:
  - When the user writes or speaks in Polish, the agent must converse, explain, and debate exclusively in Polish.
  - When the user writes or speaks in English, the agent responds in English.
- **Zero Language-Mixing**: Never switch languages or mix languages mid-dialogue. Conceptual brainstorming requires cognitive continuity; arbitrary language switching causes cognitive friction and degrades context depth.
- The English-only mandate applies strictly to persisted workspace notes and documentation files.

### 4. Universal Domain Abstraction
- Abstract low-level conversation details (such as vintage computing, emulators, or CPU opcodes discussed in chat) into universal software engineering principles per [`language-agnostic-architecture.md`](file:///d:/GoogleDrive/AI/Obsidian/Default/.agents/rules/language-agnostic-architecture.md).

### 5. Automated Verification & Quality Gates
- Compliance is enforced via the repository scanner:
  ```bash
  python scripts/check_polish.py --vault
  ```
- Any staged file containing Polish text will fail the automated pre-commit hook.
